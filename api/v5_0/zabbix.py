import json
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, Union, List

from aiohttp import ClientSession

from api import entities5
from api._base import ZabbixEntity


class _ZbxMethod(Enum):
    version = 'appinfo.version'
    login = 'user.login'
    logout = 'user.logout'
    get_user = 'user.get'


@dataclass
class _ZbxRequest(ZabbixEntity):
    method: _ZbxMethod
    params: object = None
    jsonrpc: str = '2.0'
    id: str = '1'
    auth: str = None


class Zabbix5:
    def __init__(self, url: str, user: str, password: str):
        self.url = url
        self.password = password
        self.user = user
        self._session: Optional[ClientSession] = None
        self._auth = None


    async def get_users(
            self, params: entities5.UserGet = entities5.UserGet()
    ) -> Union[entities5.User, List[entities5.User]]:
        response = await self._do_request(_ZbxMethod.get_user, params)
        if not isinstance(params.userids, str):
            return [entities5.User(**u) for u in response]
        return entities5.User(**response[0])

    async def __aenter__(self) -> "Zabbix5":
        self._session = ClientSession(base_url=self.url, headers={'Content-Type': 'application/json-rpc'})
        response = await self._do_request(_ZbxMethod.login, entities5.UserLogin(self.user, self.password))
        self._auth = response

        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._do_request(_ZbxMethod.logout)
        await self._session.close()

    async def _do_request(self, method: _ZbxMethod, params: Optional[ZabbixEntity] = None):
        data = _ZbxRequest(
            params=params, method=method, auth=self._auth,
        )
        response = await self._session.post(
            '/api_jsonrpc.php', data=data.dump()
        )

        response_json = await response.json()
        if 'result' in response_json:
            return response_json['result']
        return response_json
