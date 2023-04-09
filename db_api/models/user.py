import asyncio
import asyncpg
from sqlalchemy import PrimaryKeyConstraint, Integer, Column, ForeignKey, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base,  relationship

from db_api.config import Base


from sqlalchemy import PrimaryKeyConstraint, Integer, Column, ForeignKey, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

from db_api.config import Base




from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class GroupUser(Base):
    __tablename__ = 'group_user'
    __table_args__ = (PrimaryKeyConstraint('group_id', 'user_id'), {})

    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    group = relationship('Group', back_populates='users')
    user = relationship('User', back_populates='groups')

    def __repr__(self):
        return f"<GroupUser(group_id={self.group_id}, user_id={self.user_id})>"


class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship('GroupUser', back_populates='group')

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    phone = Column(String)
    email = Column(String)
    desc = Column(String)
    groups = relationship('GroupUser', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone}, email={self.email}, desc={self.desc})>"
