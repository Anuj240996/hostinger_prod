const { Pool } = require('pg');
require('dotenv').config();

// Determine SSL configuration based on DATABASE_URL and environment
// Easypanel Postgres services typically require SSL
function getSSLConfig() {
  const dbUrl = process.env.DATABASE_URL || '';
  
  // If DATABASE_URL contains 'localhost' or '127.0.0.1', disable SSL
  if (dbUrl.includes('localhost') || dbUrl.includes('127.0.0.1')) {
    return false;
  }
  
  // For production or remote databases (like Easypanel), enable SSL
  if (process.env.NODE_ENV === 'production' || dbUrl.includes('@')) {
    return { rejectUnauthorized: false };
  }
  
  return false;
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: getSSLConfig(),
});

pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

module.exports = pool;

