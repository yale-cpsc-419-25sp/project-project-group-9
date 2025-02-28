// server.js
require('dotenv').config();
const express = require('express');
const { sequelize } = require('./models');  // from models/index.js

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(express.json());

// Basic test route
app.get('/', (req, res) => {
  res.send('BigSib.com API is running!');
});

// Test DB connection & sync tables
(async () => {
  try {
    await sequelize.authenticate();
    console.log('Database connection successful.');

    // Sync all models 
    await sequelize.sync({ force: false });
    console.log('All models synced successfully.');

    // Start server AFTER successful DB connection
    app.listen(PORT, () => {
      console.log(`Server is listening on port ${PORT}`);
    });
  } catch (error) {
    console.error('Unable to connect to the database:', error);
  }
})();
