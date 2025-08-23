from core.utils.type.http.RouteDict import RouteDict

from typing import Final

class UploadsState:
    
    # AvatarUploadHandler
    SERVE_UPLOADS: Final[RouteDict] = {
        'route': '/<path:filename>',
        'method': []
    }