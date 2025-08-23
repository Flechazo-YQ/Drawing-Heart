from core.utils.type.http.RouteDict import RouteDict

from typing import Final

class ApiState:

    # UserChatHandler
    NEW_CHAT: Final[RouteDict] = {
        'route': '/chats',
        'method': ['POST']
    }
    HIDE_CHAT: Final[RouteDict] = {
        'route': '/chats/<chatId>/hide',
        'method': ['DELETE']
    }
    CHAT_MESSAGES: Final[RouteDict] = {
        'route': '/chats/<chatId>/messages',
        'method': ['GET', 'POST']
    }
    CHAT_STREAM: Final[RouteDict] = {
        'route': '/chats/stream',
        'method': ['POST']
    }
    CHAT_LIST: Final[RouteDict] = {
        'route': '/chats/list',
        'method': ['GET']
    }

    # AdminHandler
    ADMIN_LOGIN: Final[RouteDict] = {
        'route': '/admin/login',
        'method': ['POST']
    }
    ADMIN_INFO: Final[RouteDict] = {
        'route': '/admin/info',
        'method': ["GET", "POST"]
    }

    # AvatarUploadHandler
    UPLOAD_AVATAR: Final[RouteDict] = {
        'route': '/avatar/upload',
        'method': ['POST']
    }

    # DebugHandler
    DEBUG_PATH: Final[RouteDict] = {
        'route': '/debug/paths',
        'method': ['GET']
    }

    # DrawingSaveHandler
    SAVE_DRAWINGS: Final[RouteDict] = {
        'route': '/save',
        'method': ['POST']
    }

    # MapSearchHandler
    MAP_SEARCH: Final[RouteDict] = {
        'route': '/map/search',
        'method': ['POST']
    }
    MAP_LOCATION: Final[RouteDict] = {
        'route': '/map/location',
        'method': ['GET']
    }
    MAP_AUTOCOMPLETE: Final[RouteDict] = {
        'route': '/map/autocomplete',
        'method': ['POST']
    }
    MAP_GEOCODE: Final[RouteDict] = {
        'route': '/map/geocode',
        'method': ['POST']
    }

    # PasswordHandler
    PASSWORD_RESET: Final[RouteDict] = {
        'route': '/password/reset',
        'method': ['POST']
    }
    PASSWORD_UPDATE: Final[RouteDict] = {
        'route': '/password/update',
        'method': ['POST']
    }
    PASSWORD_RESET_DIRECT: Final[RouteDict] = {
        'route': '/password/reset/directory',
        'method': ['POST']
    }

    # UserHandler
    SEND_REGISTER_CODE: Final[RouteDict] = {
        'route': '/code/register',
        'method': ['POST']
    }
    SEND_RESET_CODE: Final[RouteDict] = {
        'route': '/code/reset',
        'method': ['POST']
    }

    ANALYSES_HISTORY: Final[RouteDict] = {
        'route': '/analyses/history',
        'method': ['GET']
    }
    ANALYSES_TODAY: Final[RouteDict] = {
        'route': '/analyses/today',
        'method': ['GET']
    }
    ANALYSES_LATEST: Final[RouteDict] = {
        'route': '/analyses/latest',
        'method': ['GET']
    }

    USER_LOGIN: Final[RouteDict] = {
        'route': '/login',
        'method': ['POST']
    }
    USER_REGISTER: Final[RouteDict] = {
        'route': '/register',
        'method': ['POST']
    }

    PROFILE_NAME: Final[RouteDict] = {
        'route': '/name',
        'method': ['GET']
    }
    PROFILE_INFO: Final[RouteDict] = {
        'route': '/info',
        'method': ['GET']
    }