import logging

from flask import Flask, Blueprint
from typing import Dict

class BlueprintConfig:
    routesToRegister = []
    blueprints: Dict[str, Blueprint] = {}
    
    @classmethod
    def apiRoutes(cls, rule: str, **options):
        def wrapper(func):
            cls.routesToRegister.append(('api', func.__module__, rule, func, options))
            return func
        return wrapper
    
    @classmethod
    def uploadsRoutes(cls, rule: str, **options):
        def wrapper(func):
            cls.routesToRegister.append(('uploads', func.__module__, rule, func, options))
            return func
        return wrapper
    
    @classmethod
    def pageRoutes(cls, rule: str, **options):
        def wrapper(func):
            cls.routesToRegister.append(('page', func.__module__, rule, func, options))
            return func
        return wrapper
    
    @classmethod
    def registerRoutes(cls, app: Flask):
        for (blueprintName, importName, rule, func, options) in cls.routesToRegister:
            match (blueprintName):
                case ('api'):
                    prefix = '/api'
                case ('uploads'):
                    prefix = '/uploads'
                case ('page'):
                    prefix = '/page'
                case _:
                    prefix = None

            blueprint = cls.__getOrCreateBlueprint(blueprintName, importName, url_prefix=prefix)

            blueprint.add_url_rule(rule, view_func=func, **options)

        for blueprint in cls.blueprints.values():
            app.register_blueprint(blueprint)

        logging.info(f"✅ 自动化路由注册完成：成功注册 { len(cls.blueprints) } 个蓝图和 { len(cls.routesToRegister) } 条路由。")

    @classmethod
    def __getOrCreateBlueprint(cls, name: str, importName: str, **kwargs) -> Blueprint:
        if (name not in cls.blueprints):
            cls.blueprints[name] = Blueprint(name, importName, **kwargs)
            return cls.blueprints[name]

        return cls.blueprints[name]