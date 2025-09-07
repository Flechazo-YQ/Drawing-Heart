from core.utils.type.http.RouteDict import RouteDict

class ApiState:
    NEW_CHAT = RouteDict(
        route='/chats',
        method=['POST']
    )

    HIDE_CHAT = RouteDict(
        route='/chats/<chatId>/hide',
        method=['DELETE']
    )

    CHAT_MESSAGES = RouteDict(
        route='/chats/<chatId>/messages',
        method=['GET', 'POST']
    )

    CHAT_STREAM = RouteDict(
        route='/chats/stream',
        method=['POST']
    )

    CHAT_MESSAGES = RouteDict(
        route='/chats/<chatId>/messages',
        method=['GET', 'POST']
    )

    CHAT_STREAM = RouteDict(
        route='/chats/stream',
        method=['POST']
    )

    CHAT_LIST = RouteDict(
        route='/chats/list',
        method=['GET']
    )

    ADMIN_LOGIN = RouteDict(
        route='/admin/login',
        method=['POST']
    )

    ADMIN_INFO = RouteDict(
        route='/admin/info',
        method=['GET', 'POST']
    )

    UPLOAD_AVATAR = RouteDict(
        route='/avatar/upload',
        method=['POST']
    )

    DEBUG_PATH = RouteDict(
        route='/debug/paths',
        method=['GET']
    )

    SAVE_DRAWINGS = RouteDict(
        route='/save',
        method=['POST']
    )

    MAP_SEARCH = RouteDict(
        route='/map/search',
        method=['POST']
    )

    MAP_LOCATION = RouteDict(
        route='/map/location',
        method=['GET']
    )

    MAP_AUTOCOMPLETE = RouteDict(
        route='/map/autocomplete',
        method=['POST']
    )

    MAP_GEOCODE = RouteDict(
        route='/map/geocode',
        method=['POST']
    )

    PASSWORD_RESET = RouteDict(
        route='/password/reset',
        method=['POST']
    )

    PASSWORD_UPDATE = RouteDict(
        route='/password/update',
        method=['POST']
    )

    PASSWORD_RESET_DIRECT = RouteDict(
        route='/password/reset/directory',
        method=['POST']
    )

    SEND_REGISTER_CODE = RouteDict(
        route='/code/register',
        method=['POST']
    )

    SEND_RESET_CODE = RouteDict(
        route='/code/reset',
        method=['POST']
    )

    ANALYSES_HISTORY = RouteDict(
        route='/analyses/history',
        method=['GET']
    )

    ANALYSES_TODAY = RouteDict(
        route='/analyses/today',
        method=['GET']
    )

    ANALYSES_LATEST = RouteDict(
        route='/analyses/latest',
        method=['GET']
    )

    USER_LOGIN = RouteDict(
        route='/login',
        method=['POST']
    )

    USER_REGISTER = RouteDict(
        route='/register',
        method=['POST']
    )

    PROFILE_NAME = RouteDict(
        route='/name',
        method=['GET']
    )

    PROFILE_INFO = RouteDict(
        route='/info',
        method=['GET']
    )