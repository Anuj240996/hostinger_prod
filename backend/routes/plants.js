const express = require('express');
const { authenticate } = require('../middleware/auth');
const pool = require('../database/db');

const router = express.Router();

// Helper function to convert snake_case to camelCase
function toCamelCase(str) {
  return str.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
}

// Helper function to map database row to camelCase JSON
function mapPlantToJson(row) {
  // Handle installation_date - it might be a Date object or a string
  let installationDate = null;
  if (row.installation_date) {
    if (row.installation_date instanceof Date) {
      installationDate = row.installation_date.toISOString().split('T')[0];
    } else if (typeof row.installation_date === 'string') {
      // Already a string, use it directly (PostgreSQL DATE types are returned as strings)
      installationDate = row.installation_date.split('T')[0]; // Remove time if present
    } else {
      // Try to parse if it's some other format
      try {
        installationDate = new Date(row.installation_date).toISOString().split('T')[0];
      } catch (e) {
        installationDate = null;
      }
    }
  }

  return {
    id: row.id ? String(row.id) : null,
    name: row.name || '',
    location: row.location || '',
    capacity: parseFloat(row.capacity || 0),
    status: row.status || 'active',
    installationDate: installationDate,
    dailyGeneration: row.daily_generation != null ? parseFloat(row.daily_generation) : null,
    monthlyGeneration: row.monthly_generation != null ? parseFloat(row.monthly_generation) : null,
    yearlyGeneration: row.yearly_generation != null ? parseFloat(row.yearly_generation) : null,
    lifetimeGeneration: row.lifetime_generation != null ? parseFloat(row.lifetime_generation) : null,
    efficiency: row.efficiency != null ? parseFloat(row.efficiency) : null,
    healthMetrics: row.health_metrics || null,
    growattPlantId: row.growatt_plant_id || null,
  };
}

// Get all plants for authenticated user
router.get('/', authenticate, async (req, res) => {
  try {
    // Use auth_user_id if available (integer from auth_user table), otherwise use id
    // Since plants.user_id is now bigint, we need the integer ID
    let userId = req.user.auth_user_id || req.user.id;
    
    // Convert to integer if it's a string
    if (typeof userId === 'string') {
      // Check if it's a UUID (contains dashes) - if so, we can't use it for plants.user_id
      if (userId.includes('-')) {
        console.error('⚠️ User ID appears to be UUID but plants.user_id requires integer');
        // If we have auth_user_id, use that
        if (req.user.auth_user_id) {
          userId = req.user.auth_user_id;
        } else {
          // Try to find a matching auth_user record by email to obtain integer ID
          try {
            if (req.user && req.user.email) {
              const match = await pool.query('SELECT id FROM auth_user WHERE email = $1 LIMIT 1', [req.user.email]);
              if (match.rows.length > 0) {
                userId = match.rows[0].id;
                console.log('✅ Mapped UUID user to auth_user id via email:', userId);
              }
            }
          } catch (mapErr) {
            console.error('❌ Error while mapping UUID user to auth_user id:', mapErr.message);
          }

          // If still a UUID or not mapped, return empty list instead of error to avoid blocking UI
          if (typeof userId === 'string' && userId.includes('-')) {
            console.warn('⚠️ Could not map UUID user to integer auth_user id. Returning empty plants list.');
            return res.json({ projects: [], plants: [] , message: 'No plants found' });
          }
        }
      } else {
        userId = parseInt(userId, 10);
        if (isNaN(userId)) {
          return res.status(400).json({ message: 'Invalid user ID format' });
        }
      }
    }

    console.log('📋 Fetching plants for user_id:', userId, '(type:', typeof userId, ')');
    console.log('📋 req.user:', { id: req.user.id, auth_user_id: req.user.auth_user_id });

    const result = await pool.query(
      `SELECT id, name, location, capacity, status, installation_date,
              daily_generation, monthly_generation, yearly_generation,
              lifetime_generation, efficiency, health_metrics, growatt_plant_id
       FROM plants
       WHERE user_id = $1
       ORDER BY created_at DESC`,
      [userId]
    );

    console.log(`✅ Found ${result.rows.length} plant(s) for user_id: ${userId}`);

    res.json({ plants: result.rows.map(mapPlantToJson) });
  } catch (error) {
    console.error('❌ Get plants error:', error.message);
    console.error('Error stack:', error.stack);
    console.error('User object:', JSON.stringify(req.user, null, 2));
    res.status(500).json({ 
      message: 'Server error',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// Get single plant details
router.get('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    
    // Use auth_user_id if available, otherwise use id (handle conversion)
    let userId = req.user.auth_user_id || req.user.id;
    if (typeof userId === 'string' && !userId.includes('-')) {
      userId = parseInt(userId, 10);
    } else if (userId && typeof userId === 'string' && userId.includes('-')) {
      // UUID case - try auth_user_id
      if (req.user.auth_user_id) {
        userId = req.user.auth_user_id;
      }
    }

    const result = await pool.query(
      `SELECT id, name, location, capacity, status, installation_date,
              daily_generation, monthly_generation, yearly_generation,
              lifetime_generation, efficiency, health_metrics, growatt_plant_id
       FROM plants
       WHERE id = $1 AND user_id = $2`,
      [id, userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Plant not found' });
    }

    res.json({ plant: mapPlantToJson(result.rows[0]) });
  } catch (error) {
    console.error('Get plant error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get generation data for a plant
router.get('/:id/generation', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    const { period } = req.query; // daily, monthly, yearly

    // Verify plant belongs to user
    const plantCheck = await pool.query(
      'SELECT id FROM plants WHERE id = $1 AND user_id = $2',
      [id, req.user.id]
    );

    if (plantCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Plant not found' });
    }

    let query;
    if (period === 'daily') {
      query = `
        SELECT date, generation
        FROM generation_data
        WHERE plant_id = $1 AND date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY date ASC
      `;
    } else if (period === 'monthly') {
      query = `
        SELECT DATE_TRUNC('month', date) as date, SUM(generation) as generation
        FROM generation_data
        WHERE plant_id = $1 AND date >= CURRENT_DATE - INTERVAL '12 months'
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY date ASC
      `;
    } else if (period === 'yearly') {
      query = `
        SELECT DATE_TRUNC('year', date) as date, SUM(generation) as generation
        FROM generation_data
        WHERE plant_id = $1
        GROUP BY DATE_TRUNC('year', date)
        ORDER BY date ASC
      `;
    } else {
      return res.status(400).json({ message: 'Invalid period' });
    }

    const result = await pool.query(query, [id]);

    res.json({
      data: result.rows.map(row => ({
        date: row.date,
        generation: parseFloat(row.generation),
      })),
    });
  } catch (error) {
    console.error('Get generation data error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;

