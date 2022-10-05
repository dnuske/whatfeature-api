from io import StringIO
import os, sys
from typing import AsyncGenerator

from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text, Boolean
from sqlalchemy_utils import UUIDType
from datetime import datetime
from sqlalchemy.dialects.postgresql import ENUM as pgEnum
from enum import Enum, unique

DATABASE_URL = os.environ["DATABASE_URL"]
Base: DeclarativeMeta = declarative_base()


@unique
class FeatureStatus(Enum):
    DRAFT = 'DRAFT'
    VOTING = 'VOTING'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'

class VoteType(Enum):
    UPVOTE = 'UPVOTE'
    DOWNVOTE = 'DOWNVOTE'

class UserType(Enum):
    FOUNDER = 'FOUNDER'
    PUSHER = 'PUSHER'

# TODO: add alembic migration sortable hash to identify migration versions and files (PR proposal)
# TODO: add SQLAlchemyBaseUserTableULID PR proposal to fastapi_users package
class User(SQLAlchemyBaseUserTableUUID, Base):
    wants_product_updates = Column(Boolean, default=False)
    type = Column(pgEnum(UserType, name='user_type'), default=UserType.PUSHER)


class Project(Base):
    __tablename__ = "projects"
    id = Column(String, server_default=text("generate_ulid()"), primary_key=True)
    name = Column(String, nullable=False)
    logo = Column(String)
    color_primary = Column(String)
    color_secondary = Column(String)
    subdomain_url = Column(String)
    user_id = Column(UUIDType(binary=False), ForeignKey('user.id'))
    created_at = Column(DateTime, default=datetime.now)

class Feature(Base):
    __tablename__ = "features"
    id = Column(String, server_default=text("generate_ulid()"), primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    project_id = Column(String, ForeignKey('projects.id'))
    visible = Column(Boolean, default=True)
    status = Column(pgEnum(FeatureStatus, name='feature_status'), default=FeatureStatus.DRAFT)
    allow_voting = Column(Boolean, default=True)
    # allow_pay = Column(Boolean, default=False)

class Vote(Base):
    __tablename__ = "votes"
    id = Column(String, server_default=text("generate_ulid()"), primary_key=True)
    type = Column(pgEnum(VoteType, name='vote_type'))
    user_id = Column(UUIDType(binary=False), ForeignKey('user.id'))
    feature_id = Column(String, ForeignKey('features.id'))
    # project_id should keep the same type as the project.id
    project_id = Column(String, ForeignKey('projects.id'))

class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, server_default=text("generate_ulid()"), primary_key=True)
    content = Column(String, nullable=False)
    user_id = Column(UUIDType(binary=False), ForeignKey('user.id'))
    feature_id = Column(String, ForeignKey('features.id'))
    project_id = Column(String, ForeignKey('projects.id'))


engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
