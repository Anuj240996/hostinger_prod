const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/plants', require('./routes/plants'));
app.use('/api/progress', require('./routes/progress'));
app.use('/api/projects', require('./routes/projects'));
app.use('/api/complaints', require('./routes/complaints'));
app.use('/api/faqs', require('./routes/faqs'));
app.use('/api/quotations', require('./routes/quotations'));
app.use('/api/leads', require('./routes/leads'));
app.use('/api/support', require('./routes/support'));
app.use('/api/users', require('./routes/users'));
app.use('/api/growatt', require('./routes/growatt'));

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'DB Solar API is running' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    message: err.message || 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err : {}
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ message: 'Route not found' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT} (accepts connections from network)`);
});

