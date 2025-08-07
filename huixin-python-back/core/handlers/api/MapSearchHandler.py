import requests, flask

from core.configs.BlueprintConfig import BlueprintConfig

from typing import Final

class MapSearchHandler:
    GAODE_API_KEY: Final[str] = '1253afe42c5a16a5c4764fc2086f3f62'
    SEARCH_KEYWORDS: Final[list[str]] = ['心理咨询', '心理医院', '精神卫生', '心理健康', '心理治疗', '心理门诊']
    SEARCH_RADIUS: Final[int] = 50000  # 搜索半径扩大到50km, 单位为米
    SEARCH_URL: Final[str] = 'https://restapi.amap.com/v3/place/around'
    IP_LOCATION_URL: Final[str] = 'https://restapi.amap.com/v3/ip'  # 高德IP定位API
    AUTOCOMPLETE_URL: Final[str] = 'https://restapi.amap.com/v3/assistant/inputtips'
    GEOCODE_URL: Final[str] = 'https://restapi.amap.com/v3/geocode/geo'

    # 后端辅助方法
    @classmethod
    def searchNearbyInstitutions(cls, latitude: float, longitude: float, radius: int | None = None):
        allPois = []
        processedIds = set()
        
        # 如果前端没有提供搜索半径，则使用默认的大范围半径
        searchRadius = radius if radius is not None else cls.SEARCH_RADIUS

        for keyword in cls.SEARCH_KEYWORDS:
            params = {
                'key': cls.GAODE_API_KEY,
                'location': f'{longitude},{latitude}',  # 高德API经度在前，纬度在后
                'keywords': keyword,
                'radius': searchRadius,
                'offset': 20,
                'page': 1,
                'extensions': 'all'
            }
            try:
                response = requests.get(cls.SEARCH_URL, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()

                if data.get('status') == '1':
                    for poi in data.get('pois', []):
                        if poi.get('id') not in processedIds:
                            processedPoi = {
                                'id': poi.get('id'),
                                'name': poi.get('name'),
                                'address': poi.get('address'),
                                'distance': int(poi.get('distance', 0)),
                                'latitude': float(poi.get('location', '0,0').split(',')[1]),
                                'longitude': float(poi.get('location', '0,0').split(',')[0]),
                                'tel': poi.get('tel', ''),
                                'rating': poi.get('biz_ext', {}).get('rating', None),
                                'avgPrice': poi.get('biz_ext', {}).get('cost', None),
                                'image': cls.getPoiImage(poi),
                                'photos': cls.getPoiPhotos(poi)
                            }
                            allPois.append(processedPoi)
                            processedIds.add(poi.get('id'))
            except requests.exceptions.RequestException as e:
                print(f"请求高德API时出错 (关键字: {keyword}): {e}")
                continue
        
        # 按距离排序
        return sorted(allPois, key=lambda x: x['distance'])
    
    # 前端调用方法, 直接搜索心理机构
    @staticmethod
    @BlueprintConfig.apiRoutes('/map/search', methods=['POST'])
    def mapSearch():
        requestData = flask.request.get_json()
        latitude = requestData.get('latitude')
        longitude = requestData.get('longitude')
        radius = requestData.get('radius')  # 接收前端传来的搜索半径

        if (not latitude or not longitude):
            return flask.jsonify({
                'error': '缺少经纬度参数'
            }), 400
        
        institutions = MapSearchHandler.searchNearbyInstitutions(latitude, longitude, radius)

        return flask.jsonify({
            'code': 0,
            'status': 'success',
            'data': institutions
        }), 200
    
    # 获取POI的主要图片
    @classmethod
    def getPoiImage(cls, poi: dict):
        # 优先级：POI详情图 > 店铺图片 > 默认图片
        photos = poi.get('photos', [])

        if (photos and len(photos) > 0):
            return photos[0].get('url', '/default-clinic.jpg')
        
        # 尝试获取店铺图片
        bizExt = poi.get('biz_ext', {})

        if ('image' in bizExt):
            return bizExt['image']

        # 根据类型返回默认图片
        return '/default-clinic.jpg'
    
    # 获取POI的所有照片
    @classmethod
    def getPoiPhotos(cls, poi: dict):
        photos = poi.get('photos', [])
        photoUrls = []

        for photo in photos[:5]:  # 最多取5张图片
            if (photo.get('url')):
                photoUrls.append(photo['url'])

        return photoUrls
    
    @staticmethod
    @BlueprintConfig.apiRoutes('/map/location', methods=['GET'])
    def locationByIp():
    
        # 获取客户端IP，优先从 X-Forwarded-For 获取，适用于反向代理
        if ('X-Forwarded-For' in flask.request.headers):
            clientIp = flask.request.headers['X-Forwarded-For'].split(',')[0].strip()
        else:
            clientIp = flask.request.remote_addr

        # 如果是本地开发环境，IP可能是127.0.0.1，高德无法定位，给一个公共IP测试
        if (clientIp == '127.0.0.1'):
            clientIp = '120.42.46.138' # 杭州的公共IP

        params = {
            'key': MapSearchHandler.GAODE_API_KEY,
            'ip': clientIp
        }
        
        try:
            response = requests.get(MapSearchHandler.IP_LOCATION_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if (data.get('status') == '1' and data.get('rectangle')):

                # 高德返回的是一个矩形范围 "lon1,lat1;lon2,lat2"，我们取中心点
                rectangle = data.get('rectangle').split(';')
                lon1, lat1 = map(float, rectangle[0].split(','))
                lon2, lat2 = map(float, rectangle[1].split(','))

                centerLongitude = (lon1 + lon2) / 2
                centerLatitude = (lat1 + lat2) / 2

                return flask.jsonify({
                    'code': 0,
                    'status': 'success',
                    'data': { 'latitude': centerLatitude, 'longitude': centerLongitude }
                }), 200
            
            # 如果定位失败，返回一个默认位置（浙江科技大学）并告知前端
            return flask.jsonify({
                'code': 1,
                'status': 'ip_location_failed',
                'message': data.get('info', 'IP定位失败'),
                'data': { 
                    'latitude': 30.227846, 
                    'longitude': 120.033056 
                }
            }), 200

        except requests.exceptions.RequestException as e:
            print(f"请求高德IP定位API时出错: { str(e) }")
            return flask.jsonify({
                'error': 'IP定位服务暂时不可用'
            }), 500
        
    # 前端调用方法, 处理地址输入时的智能提示
    @staticmethod
    @BlueprintConfig.apiRoutes('/map/autocomplete', methods=['POST'])
    def geocodeAutocomplete():
        requestData = flask.request.get_json()
        keywords = requestData.get('keywords')

        if (not keywords):
            return flask.jsonify({
                'error': '缺少关键字参数'
            }), 400

        params = {
            'key': MapSearchHandler.GAODE_API_KEY,
            'keywords': keywords,
        }

        try:
            response = requests.get(MapSearchHandler.AUTOCOMPLETE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if (data.get('status') == '1'):
                tips = data.get('tips', [])
                # 过滤掉没有地址的建议，并组合成 "名称 (区域)" 的格式
                suggestions = [
                    f"{tip.get('name')} ({tip.get('district')})" 
                    for tip in tips if tip.get('name') and tip.get('district')
                ]

                return flask.jsonify({
                    'code': 0,
                    'status': 'success',
                    'data': suggestions
                }), 200
            
            return flask.jsonify({
                'code': 1,
                'status': 'autocomplete_failed',
                'message': '获取输入建议失败'
            }), 200
        except requests.exceptions.RequestException as e:
            print(f"请求高德输入提示API时出错: { str(e) }")
            return flask.jsonify({'error': '输入提示服务暂时不可用'}), 500
        
    # 前端调用方法, 用于地址解析
    @staticmethod
    @BlueprintConfig.apiRoutes('/map/geocode', methods=['POST'])
    def geocodeAddress():
        requestData = flask.request.get_json()
        address = requestData.get('address')

        if (not address):
            return flask.jsonify({
                'error': '缺少地址参数'
            }), 400

        params = {
            'key': MapSearchHandler.GAODE_API_KEY,
            'address': address
        }

        try:
            response = requests.get(MapSearchHandler.GEOCODE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if (data.get('status') == '1' and data.get('geocodes')):
                location = data['geocodes'][0]['location']
                lon, lat = map(float, location.split(','))

                return flask.jsonify({
                    'code': 0,
                    'status': 'success',
                    'data': {'latitude': lat, 'longitude': lon}
                }), 200

            return flask.jsonify({
                'code': 1,
                'status': 'geocode_failed',
                'message': '地址解析失败，请尝试更详细的地址'
            }), 200
        except requests.exceptions.RequestException as e:
            print(f"请求高德地址解析API时出错: { str(e) }")
            return flask.jsonify({
                'error': '地址解析服务暂时不可用'
            }), 500