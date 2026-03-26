// const { Pool } = require('pg');
// require('dotenv').config();

// // Determine SSL configuration based on DATABASE_URL and environment
// // Easypanel Postgres services typically require SSL
// function getSSLConfig() {
//   const dbUrl = process.env.DATABASE_URL || '';
  
//   // If DATABASE_URL contains 'localhost' or '127.0.0.1', disable SSL
//   if (dbUrl.includes('localhost') || dbUrl.includes('127.0.0.1')) {
//     return false;
//   }
  
//   // For production or remote databases (like Easypanel), enable SSL
//   if (process.env.NODE_ENV === 'production' || dbUrl.includes('@')) {
//     return { rejectUnauthorized: false };
//   }
  
//   return false;
// }

// const pool = new Pool({
//   connectionString: process.env.DATABASE_URL,
//   ssl: getSSLConfig(),
// });

// pool.on('error', (err) => {
//   console.error('Unexpected error on idle client', err);
//   process.exit(-1);
// });

// module.exports = pool;


const { Pool } = require('pg');
require('dotenv').config();

const dbSslEnv = (process.env.DB_SSL || '').toLowerCase();
const useSsl =
  dbSslEnv === 'true' ||
  dbSslEnv === '1' ||
  dbSslEnv === 'require' ||
  dbSslEnv === 'yes';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  // Do not force SSL just because NODE_ENV=production.
  // Some VPS/local Postgres setups do not support SSL.
  ssl: useSsl ? { rejectUnauthorized: false } : false,
});

pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

module.exports = pool;





