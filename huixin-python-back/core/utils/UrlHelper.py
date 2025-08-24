import flask

class UrlHelper:
    
    # 将相对路径转换为绝对URL
    @staticmethod
    def getAbsoluteUrl(path: str):
        if (not path or path.startswith(('http://', 'https://'))):
            return path
        
        if (not path.startswith('/')):
            path = '/' + path

        # request必须在请求上下文中可用
        baseUrl = flask.request.host_url.rstrip('/')
        return f"{ baseUrl }{ path }"