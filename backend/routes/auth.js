const express = require('express');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const pool = require('../database/db');
const { authenticate } = require('../middleware/auth');

const router = express.Router();

// Helper function to verify Django PBKDF2 password
// Format: pbkdf2_sha256$<iterations>$<salt>$<hash>
function verifyDjangoPBKDF2(password, hash) {
  try {
    // Parse Django PBKDF2 hash format: pbkdf2_sha256$<iterations>$<salt>$<hash>
    const parts = hash.split('$');
    if (parts.length !== 4 || parts[0] !== 'pbkdf2_sha256') {
      return false;
    }

    const iterations = parseInt(parts[1], 10);
    const salt = parts[2];
    const storedHashBase64 = parts[3];

    // Derive the key using PBKDF2 (32 bytes = 256 bits)
    const derivedKey = crypto.pbkdf2Sync(password, salt, iterations, 32, 'sha256');

    // Base64 encode the derived key
    const derivedHashBase64 = derivedKey.toString('base64');

    // Compare base64 strings directly (they should be the same)
    // Use timing-safe comparison by comparing buffers
    let storedBuffer;
    let derivedBuffer = Buffer.from(derivedHashBase64, 'base64');

    // Try interpreting stored hash as base64 first, then hex as fallback
    try {
      storedBuffer = Buffer.from(storedHashBase64, 'base64');
      if (storedBuffer.length === 0) throw new Error('empty base64');
    } catch (e) {
      try {
        // fallback: stored as hex
        storedBuffer = Buffer.from(storedHashBase64, 'hex');
      } catch (e2) {
        // Last resort: compare string forms
        const derivedHex = derivedKey.toString('hex');
        // Log mismatch details in development to help debugging
        if (process.env.NODE_ENV !== 'production') {
          console.log('🔍 PBKDF2 compare fallback string forms');
          console.log('   storedHash (raw):', storedHashBase64);
          console.log('   derivedHashBase64:', derivedHashBase64);
          console.log('   derivedHex:', derivedHex);
        }
        return storedHashBase64 === derivedHex || storedHashBase64 === derivedHashBase64;
      }
    }

    // Ensure buffers are same length for timing-safe comparison
    if (storedBuffer.length !== derivedBuffer.length) {
      if (process.env.NODE_ENV !== 'production') {
        console.log('🔍 PBKDF2 length mismatch');
        console.log('   storedBuffer.length:', storedBuffer.length);
        console.log('   derivedBuffer.length:', derivedBuffer.length);
        try {
          console.log('   stored (base64):', Buffer.from(storedBuffer).toString('base64'));
        } catch (_) {}
        try {
          console.log('   derived (base64):', derivedBuffer.toString('base64'));
        } catch (_) {}
      }
      return false;
    }

    const equal = crypto.timingSafeEqual(storedBuffer, derivedBuffer);
    if (!equal && process.env.NODE_ENV !== 'production') {
      try {
        console.log('🔍 PBKDF2 mismatch details:');
        console.log('   storedHash (raw):', storedHashBase64);
        console.log('   derivedHashBase64:', derivedHashBase64);
        console.log('   storedHex:', Buffer.from(storedBuffer).toString('hex'));
        console.log('   derivedHex:', derivedBuffer.toString('hex'));
      } catch (_) {}
    }
    return equal;
  } catch (error) {
    console.error('Error verifying Django PBKDF2 password:', error);
    return false;
  }
}

// Helper function to check if password hash is Django PBKDF2 format
function isDjangoPBKDF2(hash) {
  if (!hash || typeof hash !== 'string') return false;
  // Django PBKDF2 format: pbkdf2_sha256$<iterations>$<salt>$<hash>
  return /^pbkdf2_sha256\$\d+\$[^$]+\$.+$/.test(hash);
}

// Helper function to verify password (supports both bcrypt and Django PBKDF2)
async function verifyPassword(password, hash) {
  if (!hash || !password) return false;

  // Normalize password using NFKC to match Django's normalization
  try {
    if (typeof password === 'string' && password.normalize) {
      password = password.normalize('NFKC');
    }
  } catch (normErr) {
    console.warn('⚠️ Password normalization failed:', normErr.message);
  }

  // Check if it's Django PBKDF2 format
  if (isDjangoPBKDF2(hash)) {
    const ok = verifyDjangoPBKDF2(password, hash);
    console.log('🔐 verifyPassword: Django PBKDF2 result =', ok);
    return ok;
  }

  // Otherwise, assume it's bcrypt
  try {
    const ok = await bcrypt.compare(password, hash);
    console.log('🔐 verifyPassword: bcrypt result =', ok);
    return ok;
  } catch (e) {
    console.warn('⚠️ verifyPassword bcrypt compare error:', e.message);
    return false;
  }
}

// Register
router.post('/signup', [
  body('name').trim().notEmpty().withMessage('Name is required'),
  body('email').isEmail().withMessage('Valid email is required'),
  body('phone').trim().notEmpty().withMessage('Phone is required'),
  body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { name, email, phone, password, address } = req.body;

    // Check if user exists
    // Ensure email uniqueness across user_app table
    const existingUser = await pool.query(
      'SELECT id FROM user_app WHERE email = $1',
      [email]
    );

    if (existingUser.rows.length > 0) {
      return res.status(400).json({ message: 'User already exists' });
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, 10);

    // Create user
    // Insert into user_app table for mobile/app users
    const result = await pool.query(
      `INSERT INTO user_app (name, email, phone, password_hash, address, role)
       VALUES ($1, $2, $3, $4, $5, 'customer')
       RETURNING id, name, email, phone, role, address, created_at`,
      [name, email, phone, passwordHash, address || null]
    );

    const user = result.rows[0];

    // Update last login for user_app (was previously updating users table)
    try {
      await pool.query(
        'UPDATE user_app SET last_login = CURRENT_TIMESTAMP WHERE id = $1',
        [user.id]
      );
    } catch (updateErr) {
      console.warn('⚠️ Could not update last_login in user_app:', updateErr.message);
    }

    // Generate token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    res.status(201).json({
      message: 'User created successfully',
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        phone: user.phone,
        role: user.role,
        address: user.address,
        createdAt: user.created_at,
      },
    });
  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
});

// App Login: authenticate only against user_app table
router.post('/login', [
  body('username').trim().notEmpty().withMessage('Username is required'),
  body('password').notEmpty().withMessage('Password is required'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Validation failed', errors: errors.array() });
    }

    const { username, password } = req.body;
    console.log('🔵 App login attempt for username:', username);

    const uaQuery = await pool.query(
      `SELECT id, name, email, phone, password_hash, role, address, created_at, last_login
       FROM user_app
       WHERE email = $1
       LIMIT 1`,
      [username]
    );

    if (uaQuery.rows.length === 0) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const uaUser = uaQuery.rows[0];
    const valid = uaUser.password_hash ? await bcrypt.compare(password, uaUser.password_hash) : false;
    if (!valid) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    // Update last_login
    try {
      await pool.query('UPDATE user_app SET last_login = CURRENT_TIMESTAMP WHERE id = $1', [uaUser.id]);
    } catch (e) {
      console.warn('Could not update user_app.last_login:', e.message);
    }

    const token = jwt.sign({ userId: uaUser.id, email: uaUser.email, source: 'user_app' }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRES_IN || '7d' });

    return res.json({
      success: true,
      message: 'Login successful',
      data: {
        token,
        user: {
          id: uaUser.id,
          name: uaUser.name,
          email: uaUser.email,
          phone: uaUser.phone,
          role: uaUser.role,
          address: uaUser.address,
          createdAt: uaUser.created_at,
        }
      }
    });
  } catch (error) {
    console.error('❌ Login error:', error);
    return res.status(500).json({ success: false, message: 'Server error' });
  }
});

// Verify credentials against auth_user table and fetch that user's projects (customers)
router.post('/verify-fetch-projects', authenticate, [
  body('username').trim().notEmpty().withMessage('Username is required'),
  body('password').notEmpty().withMessage('Password is required'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username, password } = req.body;

    // Query auth_user table for username/email
    const columnCheck = await pool.query(`
      SELECT column_name 
      FROM information_schema.columns 
      WHERE table_name = 'auth_user' 
      AND table_schema = 'public'
    `);
    const availableColumns = columnCheck.rows.map(r => r.column_name);

    let whereClause = '';
    if (availableColumns.includes('username') && availableColumns.includes('email')) {
      whereClause = 'WHERE username = $1 OR email = $1';
    } else if (availableColumns.includes('username')) {
      whereClause = 'WHERE username = $1';
    } else if (availableColumns.includes('email')) {
      whereClause = 'WHERE email = $1';
    } else {
      return res.status(400).json({ message: 'auth_user table structure not supported' });
    }

    const selectFields = ['id', availableColumns.includes('username') ? 'username as name' : "'User' as name"];
    if (availableColumns.includes('email')) selectFields.push('email');
    if (availableColumns.includes('password_hash')) selectFields.push('password_hash');
    else if (availableColumns.includes('password')) selectFields.push('password as password_hash');

    const selectQuery = `SELECT ${selectFields.join(', ')} FROM auth_user ${whereClause}`;
    console.log('📝 verify-fetch-projects request body:', req.body);
    console.log('📝 Auth select query:', selectQuery);
    let result;
    try {
      result = await pool.query(selectQuery, [username]);
    } catch (queryErr) {
      console.error('❌ SQL error on auth_user query:', queryErr.message);
      return res.status(500).json({ message: 'Server error' });
    }

    console.log('📊 auth_user rows:', result.rows.length);
    if (result.rows.length === 0) {
      console.log('⚠️ No auth_user found for username/email:', username);
      return res.status(401).json({ success: false, message: 'Invalid credentials', reason: 'user-not-found' });
    }

    const user = result.rows[0];
    // Verify password (bcrypt) - support different column names
    const storedHash = user.password_hash || user.password || user.passwordHash || user.passwordHash;
    if (!storedHash) {
      console.log('❌ No password hash found on auth_user record for id:', user.id);
      return res.status(401).json({ success: false, message: 'Invalid credentials', reason: 'no-password-hash' });
    }

    // Use verifyPassword helper which supports bcrypt and Django PBKDF2
    const isValid = await verifyPassword(password, storedHash);
    console.log('🔐 verifyPassword result =', isValid);
    if (!isValid) {
      console.log('❌ Password verification failed for auth_user id:', user.id);
      return res.status(401).json({ success: false, message: 'Invalid credentials', reason: 'password-mismatch' });
    }

    // Fetch projects/customers for this auth_user id from customer table
    const custResult = await pool.query(
      `SELECT cust_id, consumer, first_name, last_name, email, phone, address, city, state, comp_name, new_customer_id
       FROM customer
       WHERE new_customer_id = $1
       ORDER BY cust_id DESC`,
      [user.id]
    );

    const projects = custResult.rows.map(customer => ({
      id: customer.cust_id,
      projectId: customer.cust_id,
      projectName: customer.comp_name || `${customer.first_name || ''} ${customer.last_name || ''}`.trim() || `AF#${customer.consumer || customer.cust_id}`,
      consumer: customer.consumer,
      location: `${customer.city || ''}, ${customer.state || ''}`.trim() || customer.address || 'N/A',
      // Include original auth_user id so clients can request related assets if needed
      originalAuthUserId: user.id,
    }));

    res.json({ success: true, message: 'Projects fetched', data: { projects } });
  } catch (error) {
    console.error('❌ verify-fetch-projects error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Forgot Password
router.post('/forgot-password', [
  body('email').isEmail().withMessage('Valid email is required'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email } = req.body;

    // Check if user exists
    const result = await pool.query(
      'SELECT id, name FROM users WHERE email = $1',
      [email]
    );

    // Always return success to prevent email enumeration
    res.json({
      message: 'If an account exists with this email, a password reset link has been sent.',
    });

    // In production, send email with reset token
    if (result.rows.length > 0) {
      // Generate reset token
      const resetToken = jwt.sign(
        { userId: result.rows[0].id, type: 'password-reset' },
        process.env.JWT_SECRET,
        { expiresIn: '1h' }
      );

      // TODO: Send email with reset link
      console.log(`Password reset token for ${email}: ${resetToken}`);
    }
  } catch (error) {
    console.error('Forgot password error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Reset Password
router.post('/reset-password', [
  body('token').notEmpty().withMessage('Token is required'),
  body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { token, password } = req.body;

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    if (decoded.type !== 'password-reset') {
      return res.status(400).json({ message: 'Invalid token' });
    }

    // Hash new password
    const passwordHash = await bcrypt.hash(password, 10);

    // Update password
    await pool.query(
      'UPDATE users SET password_hash = $1 WHERE id = $2',
      [passwordHash, decoded.userId]
    );

    res.json({ message: 'Password reset successful' });
  } catch (error) {
    console.error('Reset password error:', error);
    res.status(400).json({ message: 'Invalid or expired token' });
  }
});

// Get current user
router.get('/me', authenticate, async (req, res) => {
  res.json({ user: req.user });
});

module.exports = router;

