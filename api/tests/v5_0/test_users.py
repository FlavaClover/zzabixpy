import pytest

from api import entities5


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

