// models/index.js
const sequelize = require('../config/database');
const User = require('./User');
const UserProfile = require('./UserProfile');
const Tag = require('./Tag');
const UserTag = require('./UserTag');
const Community = require('./Community');
const Post = require('./Post');
const Event = require('./Event');

// 1. User <-> UserProfile (One-to-One)
User.hasOne(UserProfile, {
  foreignKey: 'userId',
  onDelete: 'CASCADE'
});
UserProfile.belongsTo(User, {
  foreignKey: 'userId'
});

// 2. UserProfile <-> Tag (Many-to-Many via UserTag)
UserProfile.belongsToMany(Tag, {
  through: UserTag,
  foreignKey: 'userProfileId'
});
Tag.belongsToMany(UserProfile, {
  through: UserTag,
  foreignKey: 'tagId'
});

// 3. User <-> Post (One-to-Many)
User.hasMany(Post, {
  foreignKey: 'userId',
  onDelete: 'CASCADE'
});
Post.belongsTo(User, {
  foreignKey: 'userId'
});

// 4. Community <-> Post (One-to-Many)
Community.hasMany(Post, {
  foreignKey: 'communityId',
  onDelete: 'CASCADE'
});
Post.belongsTo(Community, {
  foreignKey: 'communityId'
});


// 5. User <-> Event (One-to-Many)
User.hasMany(Event, {
  foreignKey: 'userId',
  onDelete: 'CASCADE'
});
Event.belongsTo(User, {
  foreignKey: 'userId'
});

// Export them all for easy import
module.exports = {
  sequelize,
  User,
  UserProfile,
  Tag,
  UserTag,
  Community,
  Post,
  Event
};
