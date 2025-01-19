from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

# Association table for many-to-many relationship
link_tags = Table(
    "link_tags",
    Base.metadata,
    Column("link_id", Integer, ForeignKey("links.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    tags = relationship("Tag", secondary=link_tags, back_populates="links")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    links = relationship("Link", secondary=link_tags, back_populates="tags")


class Database:
    def __init__(self, db_url="sqlite:///links.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)

    def insert_link_with_tags(self, url: str, tag_names: list[str]):
        with Session(self.engine) as session:
            existing_link = session.query(Link).filter_by(url=url).first()
            if existing_link:
                link = existing_link
            else:
                link = Link(url=url)
                session.add(link)

            for tag_name in tag_names:
                tag = session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                if tag not in link.tags:
                    link.tags.append(tag)

            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError(f"URL '{url}' already exists in database")

    def remove_link(self, url: str):
        with Session(self.engine) as session:
            link = session.query(Link).filter_by(url=url).first()
            if not link:
                raise ValueError(f"URL '{url}' does not exist in the database")
            session.delete(link)
            session.commit()

    def remove_tags(self, url: str, tag_names: list[str]):
        with Session(self.engine) as session:
            link = session.query(Link).filter_by(url=url).first()
            if not link:
                raise ValueError(f"URL '{url}' does not exist in the database")

            for tag_name in tag_names:
                tag = session.query(Tag).filter_by(name=tag_name).first()
                if tag and tag in link.tags:
                    link.tags.remove(tag)

            session.commit()

    def get_links_by_tag(self, tag_name: str) -> list[str]:
        with Session(self.engine) as session:
            tag = session.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                return []
            return [link.url for link in tag.links]

    def get_tags(self) -> list[str]:
        with Session(self.engine) as session:
            tags = session.query(Tag).all()
            return sorted(tag.name for tag in tags)

    def get_links(self) -> list[str]:
        with Session(self.engine) as session:
            links = session.query(Link).all()
            return sorted(link.url for link in links)

    def get_tags_by_link(self, url: str) -> list[str]:
        with Session(self.engine) as session:
            link = session.query(Link).filter_by(url=url).first()
            if not link:
                return []
            return sorted(tag.name for tag in link.tags)


# Example usage
# if __name__ == "__main__":
#     db = Database()
#     db.insert_link_with_tags("https://example.com", ["tag1", "tag2", "tag3"])
#     db.remove_tags("https://example.com", ["tag2"])
#     print(db.get_tags_by_link("https://example.com"))
#     db.remove_link("https://example.com")
