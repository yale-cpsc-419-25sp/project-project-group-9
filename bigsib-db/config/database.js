require('dotenv').config();
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(
  process.env.DB_NAME,      // bigsib_db
  process.env.DB_USER,      // bigsib_user
  process.env.DB_PASSWORD,  
  {
    host: process.env.DB_HOST,       // localhost
    dialect: process.env.DB_DIALECT, // postgres
    port: process.env.DB_PORT,       // 5432
    logging: false //
  }
);

module.exports = sequelize;
