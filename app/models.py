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
class HookMethods(Enum):
    GET = 'get'
    POST = 'post'

# TODO: add alembic migration sortable hash to identify migration versions and files (PR proposal)
# TODO: add SQLAlchemyBaseUserTableULID PR proposal to fastapi_users package
class User(SQLAlchemyBaseUserTableUUID, Base):
    wants_product_updates = Column(Boolean, default=False)



class Hook(Base):
    __tablename__ = "hooks"
    id = Column(String, server_default=text("generate_ulid()"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    method = Column(pgEnum(HookMethods), unique=False, nullable=False)
    url = Column(String, nullable=False)
    body = Column(String)
    cron = Column(String, nullable=False)
    headers = Column(JSONB)
    last_hit = Column(DateTime)
    user_id = Column(UUIDType(binary=False), ForeignKey('user.id'))

class Hit(Base):
    __tablename__ = "hits"
    id = Column(String, server_default=text("generate_ulid()"), primary_key=True)
    started_at = Column(DateTime, default=datetime.now)
    finished_at = Column(DateTime)
    hook_id = Column(String, ForeignKey('hooks.id', ondelete="CASCADE"))
    response_status = Column(Integer)
    response_data = Column(String)

# guarantees should be given ran_until should never be more than 1 minute, and should always be closer to 0 as possible
class Run(Base):
    __tablename__ = "runs"
    id = Column(String, server_default=text("generate_ulid()"), primary_key=True)
    scheduled_at = Column(DateTime, default=datetime.now)
    effectively_ran_at = Column(DateTime, default=datetime.now, nullable=True)
    ran_until = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    hook_id = Column(String, ForeignKey('hooks.id', ondelete="CASCADE"))
    hit_id = Column(String, ForeignKey('hits.id', ondelete="CASCADE"))



engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
