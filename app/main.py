import os
from time import sleep
import logging
from multiprocessing import Process
import signal
import asyncio

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, fastapi_users
from app.controllers import hooks
from app.models import User
from app.processes import schedule_manager
from app.processes import dispatch_manager

import logging
# from ddtrace import config, patch_all
# patch_all(logging=True)
#
# config.env = "local"      # the environment the application is in
# config.service = "cronhooks"  # name of your application
# config.version = "0.1"  # version of your application
#
# config.fastapi['service_name'] = 'custom-service-name'
# config.fastapi['request_span_name'] = 'custom-request-span-name'
# config.debug = True
#
# FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
#           '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
#           '- %(message)s')
# logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.level = logging.DEBUG



log.info(" ******************** HELLO ******************** ")
log.error(" UWU ")

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    hooks.router,
    prefix="/hook",
    tags=["hooks"],
)

# add planet web project urls to CORS settings
PLANET_WEB_URL = os.environ.get("CLIENT_URL", "*")
# leave this to be able to set up "PLANET_WEB_URL=http://localhost:3000,http://localhost:80"
origins = PLANET_WEB_URL.split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    pass

@app.on_event("shutdown")
def shutdown_event():
    print(" ===== shutting down ====== ")

# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
