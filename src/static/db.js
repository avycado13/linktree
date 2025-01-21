const { Sequelize, DataTypes, Op } = require('sequelize');

const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: 'links.db',
});

const LinkTag = sequelize.define('LinkTag', {}, { timestamps: false });

const Link = sequelize.define('Link', {
  url: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
});

const Tag = sequelize.define('Tag', {
  name: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
});

Link.belongsToMany(Tag, { through: LinkTag });
Tag.belongsToMany(Link, { through: LinkTag });

class Database {
  constructor() {
    sequelize.sync();
  }

  async insertLinkWithTags(url, tagNames) {
    try {
      const [link, created] = await Link.findOrCreate({ where: { url } });
      for (let tagName of tagNames) {
        const [tag] = await Tag.findOrCreate({ where: { name: tagName } });
        await link.addTag(tag);
      }
    } catch (err) {
      console.error(`Error inserting link with tags: ${err.message}`);
    }
  }

  async removeLink(url) {
    try {
      const link = await Link.findOne({ where: { url } });
      if (!link) {
        throw new Error(`URL '${url}' does not exist in the database`);
      }
      await link.destroy();
    } catch (err) {
      console.error(`Error removing link: ${err.message}`);
    }
  }

  async removeTags(url, tagNames) {
    try {
      const link = await Link.findOne({ where: { url } });
      if (!link) {
        throw new Error(`URL '${url}' does not exist in the database`);
      }

      for (let tagName of tagNames) {
        const tag = await Tag.findOne({ where: { name: tagName } });
        if (tag) {
          await link.removeTag(tag);
        }
      }
    } catch (err) {
      console.error(`Error removing tags: ${err.message}`);
    }
  }

  async getLinksByTag(tagName) {
    const tag = await Tag.findOne({ where: { name: tagName } });
    if (!tag) {
      return [];
    }
    const links = await tag.getLinks();
    return links.map(link => link.url);
  }

  async getTags() {
    const tags = await Tag.findAll();
    return tags.map(tag => tag.name).sort();
  }

  async getLinks() {
    const links = await Link.findAll();
    return links.map(link => link.url).sort();
  }

  async getTagsByLink(url) {
    const link = await Link.findOne({ where: { url } });
    if (!link) {
      return [];
    }
    const tags = await link.getTags();
    return tags.map(tag => tag.name).sort();
  }
}

// Example usage:
(async () => {
  const db = new Database();
  await db.insertLinkWithTags("https://example.com", ["tag1", "tag2", "tag3"]);
  await db.removeTags("https://example.com", ["tag2"]);
  console.log(await db.getTagsByLink("https://example.com"));
  await db.removeLink("https://example.com");
})();
