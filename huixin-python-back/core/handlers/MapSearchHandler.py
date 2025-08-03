import requests, flask

from flask import Blueprint
from typing import Final

class MapSearchHandler:
    GAODE_API_KEY: Final[str] = '替换为高德API密钥'
    SEARCH_KEYWORD: Final[str] = '替换为搜索关键词'
    SEARCH_RADIUS: Final[int] = 1000  # 搜索半径, 单位为米
    SEARCH_URL: Final[str] = 'https://restapi.amap.com/v3/place/around'

    mapSearchBlueprint = Blueprint('map_search', __name__)
    
    # 后端辅助方法
    @classmethod
    def searchNearbyInstitutions(cls, latitude, longitude):
        params = {
            'key': cls.GAODE_API_KEY,
            'location': f'{ longitude },{ latitude }',  # 高德API经度在前，纬度在后
            'keywords': cls.SEARCH_KEYWORD,
            'radius': cls.SEARCH_RADIUS,
            'types': '',  # 可指定类型，也可留空
            'offset': 20,
            'page': 1,
            'extensions': 'all'
        }
        response = requests.get(cls.SEARCH_URL, params=params)
        data = response.json()

        if (data.get('status') == '1'):
            return data.get('pois', [])
        
        return []
    
    # 前端调用方法, 直接搜索心理机构
    @classmethod
    @mapSearchBlueprint.route('/api/map/search', methods=['POST'])
    def mapSearch(cls):
        requestData = flask.request.get_json()
        latitude = requestData.get('latitude')
        longitude = requestData.get('longitude')

        if (not latitude or not longitude):
            return flask.jsonify({'error': '缺少经纬度参数'}), 400
        
        institutions = cls.searchNearbyInstitutions(latitude, longitude)

        return flask.jsonify({
            'code': 0,
            'status': 'success',
            'data': institutions
        }), 200