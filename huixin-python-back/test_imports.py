#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 简化的测试文件，用于检查主要导入
try:
    import flask
    print("✓ Flask导入成功")
except ImportError as e:
    print(f"✗ Flask导入失败: {e}")

try:
    import flask_socketio
    print("✓ Flask-SocketIO导入成功")
except ImportError as e:
    print(f"✗ Flask-SocketIO导入失败: {e}")

try:
    import flask_cors
    print("✓ Flask-CORS导入成功")
except ImportError as e:
    print(f"✗ Flask-CORS导入失败: {e}")

try:
    import jwt
    print("✓ PyJWT导入成功")
except ImportError as e:
    print(f"✗ PyJWT导入失败: {e}")

try:
    import requests
    print("✓ Requests导入成功")
except ImportError as e:
    print(f"✗ Requests导入失败: {e}")

try:
    from 封装 import EmotionClassifier
    print("✓ 封装模块导入成功")
except ImportError as e:
    print(f"✗ 封装模块导入失败: {e}")

try:
    import sqlite3
    print("✓ SQLite3导入成功")
except ImportError as e:
    print(f"✗ SQLite3导入失败: {e}")

print("所有导入测试完成！")
