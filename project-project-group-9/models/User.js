// models/User.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const User = sequelize.define('User', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  },
  // local auth in addition to CAS:
  password: {
    type: DataTypes.STRING,
    allowNull: true
  }
}, {
  tableName: 'users'
});

module.exports = User;
