from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from application.auth.oauth_errors import http_error_handler
from application.database.database import init_db
from application.routes.api import router as api_router
from core.config import get_app_settings
from core.logging import logger


def get_application(db_initialization: bool = True) -> FastAPI:
    settings = get_app_settings()
    logger.info("Foodify is in '%s' environment", settings.app_env)

    # Load app
    application = FastAPI(**settings.fastapi_kwargs)

    if db_initialization:
        # Init the database
        init_db()

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(HTTPException, http_error_handler)

    application.include_router(api_router, prefix=settings.api_prefix)

    return application
