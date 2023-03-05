from enum import Enum
from dataclasses import dataclass, field
from typing import Union, List, Optional

from api._base import ZabbixEntity


OneOrManyStr = Union[str, List[str]]


@dataclass
class _BaseSearch:
    filters: dict = field(default=None)
    search: dict = field(default=None)


# Media


class MediaStatus(Enum):
    enabled = '0'
    disabled = '1'


class MediaFields(Enum):
    mediatypeid = 'mediatypeid'
    sendto = 'sendto'
    severity = 'severity'
    period = 'period'
    extend = 'extend'


class MediaTypeFields(Enum):
    mediatypeid = 'mediatypeid'
    name = 'name'
    type = 'type'
    extend = 'extend'


class MediaTypeType(Enum):
    email = '0'
    script = '1'
    sms = '2'
    webhook = '4'


class SmtpSecurity(Enum):
    none = '0'
    STARTTLS = '1'
    SSL_TTLS = '2'


class SmtpVerifyHost(Enum):
    no = '0'
    yes = '1'


class SmtpVerifyPeer(Enum):
    no = '0'
    yes = '1'


class SmtpAuth(Enum):
    none = '0'
    normal = '1'


class StatusMediaType(Enum):
    enabled = '0'
    disabled = '1'


class ContentType(Enum):
    plain = '0'
    html = '1'


class ProcessTags(Enum):
    ignore = '0'
    process = '1'


class ShowEventMenu(Enum):
    no = '0'
    yes = '1'


@dataclass
class Media(ZabbixEntity):
    mediatypeid: str
    sendto: OneOrManyStr
    active: MediaStatus
    severity: int
    period: str


@dataclass
class MediaType(ZabbixEntity):
    mediatypeid: str
    name: str
    type: MediaTypeType
    exec_path: str = field(default=None)
    gsm_modem: str = field(default=None)
    passwd: str = field(default=None)
    smtp_email: str = field(default=None)
    smtp_helo: str = field(default=None)
    smtp_server: str = field(default=None)
    smtp_port: int = field(default=None)
    smtp_security: SmtpSecurity = field(default=None)
    smtp_verify_host: SmtpVerifyHost = field(default=None)
    smtp_verify_peer: SmtpVerifyPeer = field(default=None)
    status: StatusMediaType = field(default=None)
    username: str = field(default=None)
    exec_params: str = field(default=None)
    maxsessions: str = field(default=None)
    maxattempts: str = field(default=None)
    attempt_interval: str = field(default=None)
    content_type: ContentType = field(default=None)
    script: str = field(default=None)
    timeout: str = field(default=None)
    process_tags: ProcessTags = field(default=None)
    show_event_menu: ShowEventMenu = field(default=None)
    event_menu_url: str = field(default=None)
    event_menu_name: str = field(default=None)
    parameters: List[str] = field(default=None)
    description: str = field(default=None)


# User group

class DebugMode(Enum):
    disabled = '0'
    enabled = '1'


class UsersStatus(Enum):
    enabled = '0'
    disabled = '1'


class GuiAccess(Enum):
    default = '0'
    internal = '1'
    ldap = '2'
    disable = '3'


class UserGroupFields(Enum):
    usrgrpid = 'usrgrpid'
    name = 'name'
    debug_mode = 'debug_mode'
    gui_access = 'gui_access'
    users_status = 'users_status'
    extend = 'extend'


@dataclass
class UserGroup(ZabbixEntity):
    usrgrpid: str
    name: str
    debug_mode: DebugMode
    gui_access: GuiAccess
    users_status: UsersStatus


# User

class AutoLogin(Enum):
    disabled = '0'
    enabled = '1'


class Theme(Enum):
    default = 'default'
    blue = 'blue-theme'
    dark = 'dark-theme'


class UserType(Enum):
    user = '1'
    admin = '2'
    super = '3'


class UserFields(Enum):
    extend = 'extend'
    userid = 'userid'
    alias = 'alias'
    attempt_clock = 'attempt_clock'
    attempt_failed = 'attempt_failed'
    attempt_ip = 'attempt_ip'
    autologin = 'autologin'
    autologout = 'autologout'
    lang = 'lang'
    name = 'name'
    refresh = 'refresh'
    rows_per_page = 'rows_per_page'
    surname = 'surname'
    theme = 'theme'
    type = 'type'
    url = 'url'


@dataclass
class User(ZabbixEntity):
    userid: str
    alias: str
    attempt_clock: int
    attempt_failed: int
    attempt_ip: str
    autologin: AutoLogin
    autologout: str
    lang: str
    name: str
    refresh: str
    rows_per_page: str
    surname: str
    theme: Theme
    type: UserType
    url: str
    medias: List[Media] = field(default=None)
    usrgrps: List[UserGroup] = field(default=None)
    mediatypes: List[MediaType] = field(default=None)


@dataclass
class UserLogin(ZabbixEntity):
    user: str
    password: str


@dataclass
class UserGet(_BaseSearch, ZabbixEntity):
    output: Union[UserFields, List[UserFields]] = field(default=UserFields.extend)
    mediaids: OneOrManyStr = field(default=None)
    mediatypeids: OneOrManyStr = field(default=None)
    userids: OneOrManyStr = field(default=None)
    usrgrpids: OneOrManyStr = field(default=None)
    selectMedias: Union[MediaFields, List[MediaFields]] = field(default=None)
    selectMediatypes: Union[MediaTypeFields, List[MediaTypeFields]] = field(default=None)
    selectUsrgrps: Union[UserGroupFields, List[UserGroupFields]] = field(default=None)


@dataclass
class UserCreate(ZabbixEntity):
    alias: str
    passwd: str
    usrgrps: Union[List[UserGroup], List[str]]
    url: str = field(default='')
    user_medias: Optional[List[Media]] = field(default_factory=list)
    autologin: AutoLogin = field(default=AutoLogin.disabled)
    autologout: str = field(default='15m')
    lang: str = field(default='en_GB')
    name: str = field(default='')
    refresh: str = field(default='30s')
    rows_per_page: str = field(default='50')
    surname: str = field(default='')
    theme: Theme = field(default=Theme.default)
    type: UserType = field(default=UserType.user)
