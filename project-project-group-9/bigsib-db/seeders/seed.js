// seeders/seed.js
require('dotenv').config();
const { sequelize, User, UserProfile, Tag, Community, Post } = require('../models');

(async function seed() {
  try {
    // Re-sync tables from scratch for seeding
    // NOTE: This will wipe all existing data in dev
    await sequelize.sync({ force: true });

    // 1) Create some Tags
    const [csTag, econTag, debateTag] = await Promise.all([
      Tag.create({ name: 'Computer Science', category: 'major' }),
      Tag.create({ name: 'Economics', category: 'major' }),
      Tag.create({ name: 'Debate', category: 'hobby' })
    ]);

    // 2) Create a User + Profile
    const user1 = await User.create({ email: 'alice@example.com' });
    const profile1 = await UserProfile.create({
      userId: user1.id,
      name: 'Alice Zhong',
      residentialCollege: 'Branford',
      hometown: 'New York',
      major: 'Computer Science',
      gradeLevel: 'Senior'
    });
    await profile1.addTag(csTag);
    await profile1.addTag(debateTag);

    // 3) Create a Community
    const community1 = await Community.create({
      name: 'Pre-Med Community',
      description: 'All things pre-med at Yale.'
    });

    // 4) Create a Post
    await Post.create({
      title: 'Shadowing Opportunity',
      content: 'Join us at the local hospital this summer.',
      type: 'event',
      communityId: community1.id,
      userId: user1.id
    });

    console.log('Seeding complete. Sample data inserted.');
    process.exit(0);
  } catch (error) {
    console.error('Error during seeding:', error);
    process.exit(1);
  }
})();
