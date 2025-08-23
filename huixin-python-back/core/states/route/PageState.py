from core.utils.type.http.RouteDict import RouteDict

from typing import Final

class PageState:
    ROOT: Final[RouteDict] = {
        'route': '/root',
        'method': []
    }
    INDEX: Final[RouteDict] = {
        'route': '',
        'method': []
    }
    REGISTER: Final[RouteDict] = {
        'route': '/register',
        'method': ['GET']
    }
    FORGOT: Final[RouteDict] = {
        'route': '/forgot',
        'method': ['GET']
    }
    DRAW: Final[RouteDict] = {
        'route': '/draw',
        'method': []
    }
    ANALYSE: Final[RouteDict] = {
        'route': '/analyse',
        'method': []
    }
    PRIVACY: Final[RouteDict] = {
        'route': '/privacy',
        'method': []
    }
    CHAT: Final[RouteDict] = {
        'route': '/chat',
        'method': ['GET']
    }
    TEMPLATES_FILE: Final[RouteDict] = {
        'route': '/templates/<path:filename>',
        'method': []
    }