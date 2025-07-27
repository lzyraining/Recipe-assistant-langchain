import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_api_client: Optional["APIClient"] = None


class APIClient:
    _base_url = "https://api.api-ninjas.com/v1/"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_recipe(self, name: str) -> str:
        api_url = f"{self._base_url}recipe?query={name}"
        logger.info(f"Inovke api using endpoint {api_url}")
        response = requests.get(api_url, headers={"X-Api-Key": self._api_key})

        if response.status_code == requests.codes.ok:
            return response.text
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")


def get_api_client() -> APIClient:
    global _api_client
    if _api_client is None:
        _api_client = APIClient(os.getenv("API_NINJA_KEY"))
    return _api_client
