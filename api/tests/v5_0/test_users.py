import random
import secrets
import pytest

from api.v5_0.entities import (
    MediaFields, UserGroupFields, MediaTypeFields,
    UserGet, UserUpdate, UserCreate, UserFields, User
)
from api import exceptions


@pytest.mark.asyncio
async def test_get_user(zabbix5, admin_id):
    async with zabbix5 as zapi:
        users = await zapi.get_users()

        assert len(users) != 0

        user_admin = await zapi.get_users(UserGet(
            userids=admin_id,
            selectMedias=MediaFields.extend,
            selectUsrgrps=UserGroupFields.extend,
            selectMediatypes=MediaTypeFields.extend,
        ))

        assert isinstance(user_admin, User)
        assert len(user_admin.mediatypes) != 0
        assert len(user_admin.medias) != 0
        assert len(user_admin.usrgrps) != 0

        non_existing_user = await zapi.get_users(
            UserGet(
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
                UserCreate(
                    passwd=secrets.token_hex(16),
                    alias=alias,
                    usrgrps=[]
                )
            )

        user1 = await zapi.create_user(
            UserCreate(
                passwd=secrets.token_hex(16),
                alias=alias,
                usrgrps=[group_id]
            )
        )

        with pytest.raises(exceptions.InvalidParams):
            await zapi.create_user(
                UserCreate(
                    passwd=secrets.token_hex(16),
                    alias=alias,
                    usrgrps=[group_id]
                )
            )

        user2 = await zapi.create_user(
            UserCreate(
                passwd=secrets.token_hex(16),
                alias=alias + '1',
                usrgrps=[{'usrgrpid': group_id}]
            )
        )

        user_count_after = len(await zapi.get_users())

        assert user_count_before != user_count_after
        await zapi.delete_user(user1.userid)
        await zapi.delete_user(user2.userid)

        user_count_after = len(await zapi.get_users())

        assert user_count_before == user_count_after


@pytest.mark.asyncio
async def test_update_user(zabbix5, group_id):
    async with zabbix5 as zapi:
        alias = 'from_pytest_' + secrets.token_hex(3)

        user = await zapi.create_user(
            UserCreate(
                alias=alias,
                passwd=secrets.token_hex(16),
                usrgrps=[group_id],
                name='pytest',
                surname='pytestov'
            )
        )

        with pytest.raises(exceptions.InvalidParams):
            await zapi.update_user(
                UserUpdate(
                    name='update_pytest'
                )
            )

        try:
            await zapi.update_user(
                UserUpdate(
                    userid=user.userid,
                    name='update_pytest'
                )
            )

            user = await zapi.get_users(
                UserGet(userids=user.userid)
            )

            assert user.name == 'update_pytest'

            with pytest.raises(exceptions.InvalidParams):
                await zapi.update_user(
                    UserUpdate(
                        userid=user.userid,
                        usrgrps=[]
                    )
                )

        except (exceptions.ZabbixException, AssertionError):
            raise
        finally:
            await zapi.delete_user(user.userid)


@pytest.mark.asyncio
async def test_smart_get_user(zabbix5, group_id):
    tags = {
        'tag1': random.randint(3, 4),
        'tag2': random.randint(2, 7),
        'tag3': random.randint(5, 11)
    }

    user_ids = []
    aliases = []
    async with zabbix5 as zapi:
        for tag in tags:
            for _ in range(tags[tag]):
                alias = 'from_pytest_' + secrets.token_hex(3) + '_' + tag
                user = await zapi.create_user(
                    UserCreate(
                        alias=alias,
                        passwd=secrets.token_hex(16),
                        usrgrps=[group_id],
                    )
                )
                user_ids.append(user.userid)
                aliases.append(alias)
        assert len(user_ids) == sum(tags.values())
        assert len(aliases) == sum(tags.values())
        try:
            for tag in tags:
                users = await zapi.get_users(
                    UserGet(
                        search={UserFields.alias: tag}
                    )
                )

                assert len(users) == tags[tag]

            users = await zapi.get_users(
                UserGet(
                    filter={UserFields.alias: aliases}
                )
            )

            assert len(users) == sum(tags.values())

            users = await zapi.get_users(
                UserGet(
                    filter={UserFields.alias: aliases},
                    search={UserFields.alias: 'tag1'},
                )
            )

            assert len(users) == tags['tag1']
        except (exceptions.ZabbixException, AssertionError):
            raise
        finally:
            await zapi.delete_user(user_ids)
