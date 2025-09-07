from core.utils.type.http.RouteDict import RouteDict

class UploadsState:
    
    # AvatarUploadHandler
    SERVE_UPLOADS = RouteDict(
        route='/<path:filename>',
        method=[]
    )