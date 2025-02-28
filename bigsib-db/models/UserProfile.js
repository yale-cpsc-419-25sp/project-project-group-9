// models/UserProfile.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const UserProfile = sequelize.define('UserProfile', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  hometown: {
    type: DataTypes.STRING
  },
  residentialCollege: {
    type: DataTypes.STRING // e.g. Branford, Saybrook, etc.
  },
  ethnicity: {
    type: DataTypes.STRING
  },
  major: {
    type: DataTypes.STRING
  },
  gradeLevel: {
    type: DataTypes.ENUM('Freshman', 'Sophomore', 'Junior', 'Senior'),
    allowNull: true
  },
  // Additional fields for extracurriculars, jobs, etc. if desired
}, {
  tableName: 'user_profiles'
});

module.exports = UserProfile;
