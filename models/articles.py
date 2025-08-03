from models import Base
from sqlalchemy import Integer, String, Column, Text, ForeignKey
from sqlalchemy.orm import relationship


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    articles = relationship("Article", secondary="article_tag", back_populates='tags', lazy='dynamic')


class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    # author_id和author用于表示一对多的关系
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship("User", backref='articles')
    # tags：表示Article和Tag的多对多的关系
    tags = relationship("Tag", secondary="article_tag", back_populates='articles', lazy='dynamic')

# Article和Tag的中间表
class ArticleTag(Base):
    __tablename__ = "article_tag"
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("article.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)