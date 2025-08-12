const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Enable CORS for all routes
app.use(cors());

// Serve static files from the reports directory
app.use('/reports', express.static(path.join(__dirname, '../backend-python/reports'), {
  setHeaders: (res, path) => {
    if (path.endsWith('.pdf')) {
      res.set('Content-Type', 'application/pdf');
      res.set('Content-Disposition', 'inline');
    }
  }
}));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'PDF server is running',
    timestamp: new Date().toISOString()
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`📁 PDF Static File Server running on http://localhost:${PORT}`);
  console.log(`🔗 Reports available at http://localhost:${PORT}/reports/`);
  console.log(`📋 Discharge reports: http://localhost:${PORT}/reports/discharge/`);
});

module.exports = app;
