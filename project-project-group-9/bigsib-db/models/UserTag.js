// models/UserTag.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const UserTag = sequelize.define('UserTag', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  }
}, {
  tableName: 'user_tags'
});

module.exports = UserTag;
