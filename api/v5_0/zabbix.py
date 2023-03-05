from enum import Enum
from dataclasses import dataclass
from typing import Optional, Union, List

from aiohttp import ClientSession

from api import entities5
from api._base import ZabbixEntity


UserType = Optional[Union[entities5.User, List[entities5.User]]]


class _ZbxMethod(Enum):
    version = 'appinfo.version'
    login = 'user.login'
    logout = 'user.logout'
    get_user = 'user.get'
    create_user = 'user.create'


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

    async def get_users(self, params: entities5.UserGet = entities5.UserGet()) -> UserType:
        response = await self._do_request(_ZbxMethod.get_user, params)
        if not isinstance(params.userids, str):
            return [entities5.User(**u) for u in response]

        if len(response) == 0:
            return None

        return entities5.User(**response[0])

    async def create_user(
            self, params: entities5.UserCreate
    ) -> entities5.User:

        params.usrgrps = [
            {'usrgrpid': g.usrgrpid} if isinstance(g, entities5.UserGroup) else {'usrgrpid': g}
            for g in params.usrgrps
        ]

        response = await self._do_request(_ZbxMethod.create_user, params=params)

        return await self.get_users(entities5.UserGet(
            userids=response['userids'][0]
        ))

    async def delete_user(self, user_id: str):
        pass

    async def connect(self):
        self._session = ClientSession(
            base_url=self.url, headers={'Content-Type': 'application/json-rpc'}
        )
        response = await self._do_request(
            _ZbxMethod.login, entities5.UserLogin(self.user, self.password)
        )
        self._auth = response

    async def disconnect(self):
        await self._do_request(_ZbxMethod.logout)
        self._auth = None
        await self._session.close()

    async def __aenter__(self) -> "Zabbix5":
        if self._auth is None:
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def _do_request(self, method: _ZbxMethod, params: Optional[ZabbixEntity] = None):
        if not params:
            params = {}

        data = _ZbxRequest(
            params=params, method=method, auth=self._auth,
        )

        response = await self._session.post(
            '/api_jsonrpc.php', data=data.dump()
        )

        response_json = await response.json()
        if 'error' in response_json:
            raise Exception(str(response_json['error']))
        if 'result' in response_json:
            return response_json['result']
        return response_json
