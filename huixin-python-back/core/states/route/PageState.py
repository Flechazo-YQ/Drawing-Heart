from core.utils.type.http.RouteDict import RouteDict

class PageState:
    ROOT = RouteDict(
        route='/root',
        method=[]
    )

    INDEX = RouteDict(
        route='',
        method=[]
    )

    REGISTER = RouteDict(
        route='/register',
        method=['GET']
    )

    FORGOT = RouteDict(
        route='/forgot',
        method=['GET']
    )

    DRAW = RouteDict(
        route='/draw',
        method=[]
    )

    ANALYSE = RouteDict(
        route='/analyse',
        method=[]
    )

    PRIVACY = RouteDict(
        route='/privacy',
        method=[]
    )

    CHAT = RouteDict(
        route='/chat',
        method=['GET']
    )
    
    TEMPLATES_FILE = RouteDict(
        route='/templates/<path:filename>',
        method=[]
    )