from core.utils.TypedDictionaryHelper import TypedDictionaryHelper

from typing import Final

class RouteState:
    class Api:

        # UserChatHandler
        NEW_CHAT: Final[TypedDictionaryHelper.Route] = {
            'route': '/chats',
            'method': ['POST']
        }
        HIDE_CHAT: Final[TypedDictionaryHelper.Route] = {
            'route': '/chats/<chatId>/hide',
            'method': ['DELETE']
        }
        CHAT_MESSAGES: Final[TypedDictionaryHelper.Route] = {
            'route': '/chats/<chatId>/messages',
            'method': ['GET', 'POST']
        }
        CHAT_STREAM: Final[TypedDictionaryHelper.Route] = {
            'route': '/chats/stream',
            'method': ['POST']
        }
        CHAT_LIST: Final[TypedDictionaryHelper.Route] = {
            'route': '/chats/list',
            'method': ['GET']
        }

        # AdminHandler
        ADMIN_LOGIN: Final[TypedDictionaryHelper.Route] = {
            'route': '/admin/login',
            'method': ['POST']
        }
        ADMIN_INFO: Final[TypedDictionaryHelper.Route] = {
            'route': '/admin/info',
            'method': ["GET", "POST"]
        }

        # AvatarUploadHandler
        UPLOAD_AVATAR: Final[TypedDictionaryHelper.Route] = {
            'route': '/avatar/upload',
            'method': ['POST']
        }

        # DebugHandler
        DEBUG_PATH: Final[TypedDictionaryHelper.Route] = {
            'route': '/debug/paths',
            'method': ['GET']
        }

        # DrawingSaveHandler
        SAVE_DRAWINGS: Final[TypedDictionaryHelper.Route] = {
            'route': '/save',
            'method': ['POST']
        }

        # MapSearchHandler
        MAP_SEARCH: Final[TypedDictionaryHelper.Route] = {
            'route': '/map/search',
            'method': ['POST']
        }
        MAP_LOCATION: Final[TypedDictionaryHelper.Route] = {
            'route': '/map/location',
            'method': ['GET']
        }
        MAP_AUTOCOMPLETE: Final[TypedDictionaryHelper.Route] = {
            'route': '/map/autocomplete',
            'method': ['POST']
        }
        MAP_GEOCODE: Final[TypedDictionaryHelper.Route] = {
            'route': '/map/geocode',
            'method': ['POST']
        }

        # PasswordHandler
        PASSWORD_RESET: Final[TypedDictionaryHelper.Route] = {
            'route': '/password/reset',
            'method': ['POST']
        }
        PASSWORD_UPDATE: Final[TypedDictionaryHelper.Route] = {
            'route': '/password/update',
            'method': ['POST']
        }
        PASSWORD_RESET_DIRECT: Final[TypedDictionaryHelper.Route] = {
            'route': '/password/reset/directory',
            'method': ['POST']
        }

        # UserHandler
        SEND_REGISTER_CODE: Final[TypedDictionaryHelper.Route] = {
            'route': '/code/register',
            'method': ['POST']
        }
        SEND_RESET_CODE: Final[TypedDictionaryHelper.Route] = {
            'route': '/code/reset',
            'method': ['POST']
        }

        ANALYSES_HISTORY: Final[TypedDictionaryHelper.Route] = {
            'route': '/analyses/history',
            'method': ['GET']
        }
        ANALYSES_TODAY: Final[TypedDictionaryHelper.Route] = {
            'route': '/analyses/today',
            'method': ['GET']
        }
        ANALYSES_LATEST: Final[TypedDictionaryHelper.Route] = {
            'route': '/analyses/latest',
            'method': ['GET']
        }

        USER_LOGIN: Final[TypedDictionaryHelper.Route] = {
            'route': '/login',
            'method': ['POST']
        }
        USER_REGISTER: Final[TypedDictionaryHelper.Route] = {
            'route': '/register',
            'method': ['POST']
        }

        PROFILE_NAME: Final[TypedDictionaryHelper.Route] = {
            'route': '/name',
            'method': ['GET']
        }
        PROFILE_INFO: Final[TypedDictionaryHelper.Route] = {
            'route': '/info',
            'method': ['GET']
        }

    class Uploads:

        # AvatarUploadHandler
        SERVE_UPLOADS: Final[TypedDictionaryHelper.Route] = {
            'route': '/<path:filename>',
            'method': []
        }

    class Page:

        # PageHandler
        ROOT: Final[TypedDictionaryHelper.Route] = {
            'route': '/root',
            'method': []
        }
        INDEX: Final[TypedDictionaryHelper.Route] = {
            'route': '',
            'method': []
        }
        REGISTER: Final[TypedDictionaryHelper.Route] = {
            'route': '/register',
            'method': ['GET']
        }
        FORGOT: Final[TypedDictionaryHelper.Route] = {
            'route': '/forgot',
            'method': ['GET']
        }
        DRAW: Final[TypedDictionaryHelper.Route] = {
            'route': '/draw',
            'method': []
        }
        ANALYSE: Final[TypedDictionaryHelper.Route] = {
            'route': '/analyse',
            'method': []
        }
        PRIVACY: Final[TypedDictionaryHelper.Route] = {
            'route': '/privacy',
            'method': []
        }
        CHAT: Final[TypedDictionaryHelper.Route] = {
            'route': '/chat',
            'method': ['GET']
        }
        TEMPLATES_FILE: Final[TypedDictionaryHelper.Route] = {
            'route': '/templates/<path:filename>',
            'method': []
        }

