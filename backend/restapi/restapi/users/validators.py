import os
import requests
import json
import time
from rest_framework.exceptions import APIException
import logging

logger = logging.getLogger(__name__)

__all__ = ["validate_email"]


def validate_email(email: str) -> bool:
    """
    Validates emails from hunter.io
    I could have written a separate service for this, but I am lazy)
    """
    api_key = os.getenv("HUNTERIO_API_KEY")
    verifier_url = os.getenv("HUNTERIO_EMAILVERIFIER_URL")
    valid_status = os.getenv("HUNTERIO_VALID_STATUS_LIST")

    if any((api_key, verifier_url)) is None:
        msg = "hunter io api_key or verifier url not found in the env"
        logger.error(msg)  # TODO: configure logging
        raise APIException(msg)

    valid_status = [
        i.strip() for i in valid_status.split("/") if len(i) > 0
    ]

    url = f"{verifier_url}?email={email}&api_key={api_key}"

    tries = 0
    success = False
    while tries < 3:
        response = requests.get(url)
        if response.status_code == 200:  # could be 202
            success = True
            break
        logger.warning("hunter io responded with error\n "+str(response.text))
        time.sleep(1)
        tries += 1

    if success:
        # only check if it is a valid email
        validation_status = (
            json.loads(response.text).get("data", {}).get("status", None)
        )

        if validation_status is None:
            raise APIException("Hunter io is not responding")
        elif validation_status in valid_status:
            return True
        else:
            return False
    else:
        raise APIException("Hunter io is not responding")
