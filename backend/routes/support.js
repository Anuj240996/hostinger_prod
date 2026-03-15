const express = require('express');
const { body, validationResult } = require('express-validator');
const pool = require('../database/db');
const { authenticate } = require('../middleware/auth');

const router = express.Router();

// Submit support query
router.post('/query', authenticate, [
  body('subject').trim().notEmpty().withMessage('Subject is required'),
  body('message').trim().notEmpty().withMessage('Message is required'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { subject, message } = req.body;

    const result = await pool.query(
      `INSERT INTO support_queries (user_id, subject, message)
       VALUES ($1, $2, $3)
       RETURNING id, subject, message, status, created_at`,
      [req.user.id, subject, message]
    );

    res.json({
      message: 'Query submitted successfully',
      query: result.rows[0],
    });
  } catch (error) {
    console.error('Submit query error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;

