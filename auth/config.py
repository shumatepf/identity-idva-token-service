# server/config.py

import os
import json
import logging

log = logging.getLogger(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Base configuration."""

    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(BaseConfig):
    """Development configuration for cloud foundry deployments."""

    DEFAULT_SECONDS = 604800  # 7 days
    DEFAULT_USES = 1

    SECRET_KEY = None

    GDRIVE_APP_HOST = os.getenv("GDRIVE_APP_HOST")
    GDRIVE_APP_PORT = os.getenv("GDRIVE_APP_PORT")

    vcap_services = os.getenv("VCAP_SERVICES", "")

    try:
        services = json.loads(vcap_services)
        for service in services["user-provided"]:
            if service["name"] == "token-service-secret":
                log.info("Loading secret key from user service")
                SECRET_KEY = service["credentials"]["key"]
                break
        if SECRET_KEY == None:
            log.error("Unable to load secret key from user service")
        db_uri = services["aws-rds"][0]["credentials"]["uri"]
    except (json.JSONDecodeError, KeyError) as err:
        log.warning("Unable to load db_uri from VCAP_SERVICES")
        log.debug("Error: %s", str(err))
        db_uri = ""

    # Sqlalchemy requires 'postgresql' as the protocol
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_uri
