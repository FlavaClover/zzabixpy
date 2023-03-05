import secrets
import pytest

from api import entities5
from api import exceptions


@pytest.mark.asyncio
async def test_get_user(zabbix5, admin_id):
    async with zabbix5 as zapi:
        users = await zapi.get_users()

        assert len(users) != 0

        user_admin = await zapi.get_users(entities5.UserGet(
            userids=admin_id,
            selectMedias=entities5.MediaFields.extend,
            selectUsrgrps=entities5.UserGroupFields.extend,
            selectMediatypes=entities5.MediaTypeFields.extend,
        ))

        assert isinstance(user_admin, entities5.User)
        assert len(user_admin.mediatypes) != 0
        assert len(user_admin.medias) != 0
        assert len(user_admin.usrgrps) != 0

        non_existing_user = await zapi.get_users(
            entities5.UserGet(
                userids='kek',
            )
        )

        assert non_existing_user is None


@pytest.mark.asyncio
async def test_create_delete_user(zabbix5, group_id):
    async with zabbix5 as zapi:
        alias = 'from_pytest_' + secrets.token_hex(3)

        user_count_before = len(await zapi.get_users())

        with pytest.raises(exceptions.InvalidParams):
            await zapi.create_user(
                entities5.UserCreate(
                    passwd=secrets.token_hex(16),
                    alias=alias,
                    usrgrps=[]
                )
            )

        user = await zapi.create_user(
            entities5.UserCreate(
                passwd=secrets.token_hex(16),
                alias=alias,
                usrgrps=[group_id]
            )
        )

        with pytest.raises(exceptions.InvalidParams):
            user = await zapi.create_user(
                entities5.UserCreate(
                    passwd=secrets.token_hex(16),
                    alias=alias,
                    usrgrps=[group_id]
                )
            )

        user_count_after = len(await zapi.get_users())

        assert user_count_before != user_count_after
        await zapi.delete_user(user.userid)

        user_count_after = len(await zapi.get_users())

        assert user_count_before == user_count_after
