import asyncio
import aiohttp
import logging
from urllib.parse import urljoin
from http import HTTPStatus
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

class Alist():
    def __init__(self, hass, config) -> None:
        self.name = config[CONF_NAME]
        self.host = config[CONF_HOST]
        self.username = config[CONF_USERNAME]
        self.password = config[CONF_PASSWORD]
        self.session = async_get_clientsession(hass)
        self.token = ''
    
    async def async_login(self) -> bool:
        try:
            async with asyncio.timeout(10):
                response = await self.session.post(
                    urljoin(self.host, "/api/auth/login/hash"),
                    json={
                        "username": self.username,
                        "password": self.password,
                        "otp_code": ""
                    }
                )
            
            if response.status != HTTPStatus.OK:
                _LOGGER.error("Error to get auth token")
                return False
            
            response_json = await response.json()

            if (code:= response_json.get("code")) != 200:
                _LOGGER.error(f"Error to get auth token, code:{code}")
                return False
            
            self.token = response_json["data"]["token"]

            return True

        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Timeout to get auth token")
        except Exception as e:
            _LOGGER.error(e)
        
        return False

    async def async_list(self, path="/", auto_login=True) -> list:
        try:
            async with asyncio.timeout(10):
                response = await self.session.post(
                    urljoin(self.host, "/api/fs/list"),
                    headers={"Authorization": self.token},
                    json={
                        "path": path,
                        "password": "",
                        "page": 1,
                        "per_page": 0,
                        "refresh": False
                    }
                )
            
            if response.status != HTTPStatus.OK:
                _LOGGER.error("Error to list dir")
                return []
            
            response_json = await response.json()

            code = response_json.get("code")

            if code == 401 and auto_login:
                await self.async_login()
                return await self.async_list(path, False)

            if code != 200:
                _LOGGER.error(f"Error to list dir, code:{code}")
                return []
            
            return response_json["data"]["content"]

        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Timeout to get auth token")
        except Exception as e:
            _LOGGER.error(e)
        
        return []
    
    async def async_resolve_download_url(self, path: str):
        return urljoin(self.host, f'/d{path}')

