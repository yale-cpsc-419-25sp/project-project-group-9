// models/Tag.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Tag = sequelize.define('Tag', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  category: {
    type: DataTypes.ENUM('major', 'hobby', 'affinity', 'career', 'interest'),
    allowNull: false
  }
}, {
  tableName: 'tags'
});

module.exports = Tag;
