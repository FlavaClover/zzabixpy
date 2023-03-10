from enum import Enum
from dataclasses import dataclass
from typing import Optional, Union, List

from aiohttp import ClientSession

from api import entities5
from api.exceptions import ZabbixExceptionFactory, ZabbixException
from api._base import ZabbixEntity, _ZbxRequest, _ZbxMethod


UserType = Optional[Union[entities5.User, List[entities5.User]]]


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

    async def create_user(self, params: entities5.UserCreate) -> entities5.User:
        response = await self._do_request(_ZbxMethod.create_user, params=params)

        return await self.get_users(entities5.UserGet(
            userids=response['userids'][0]
        ))

    async def update_user(self, params: entities5.UserUpdate) -> entities5.User:
        response = await self._do_request(_ZbxMethod.update_user, params)

        return await self.get_users(entities5.UserGet(
            userids=response['userids'][0]
        ))

    async def delete_user(self, user_ids: Union[str, List[str]]):
        await self._do_request(
            _ZbxMethod.delete_user, params=user_ids if isinstance(user_ids, list) else [user_ids]
        )

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

    async def _do_request(
            self, method: _ZbxMethod, params: Optional[Union[ZabbixEntity, list, dict]] = None
    ):
        if not params:
            params = {}

        data = _ZbxRequest(
            params=params, method=method, auth=self._auth,
        )

        data = data.dump()
        response = await self._session.post(
            '/api_jsonrpc.php', data=data
        )

        response_json = await response.json()
        if 'error' in response_json:
            exception_factory = ZabbixExceptionFactory(response_json['error']['code'])
            exception = exception_factory.exception()
            if exception is None:
                raise ZabbixException(**response_json['error'])
            raise exception(data=response_json['error']['data'])

        if 'result' in response_json:
            return response_json['result']

        return response_json
