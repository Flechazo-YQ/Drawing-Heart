# -*- coding: utf-8 -*-
import base64
import datetime
import threading
import jwt
import requests
import hashlib
import json
import os
import re  # 添加正则表达式模块
import logging
import sys
import secrets
import httpx  # 添加httpx导入
from datetime import timedelta
from flask import render_template, jsonify, send_from_directory, Flask, request, json
from flask import Response, stream_with_context
from flask_cors import CORS  # 添加CORS支持
from flask_socketio import SocketIO, emit, join_room, leave_room  # 添加SocketIO支持
from torchvision import transforms
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from openai import OpenAI
from 封装 import EmotionClassifier
from mongodb_config import init_mongodb
from bson import ObjectId
from Handler.EmailCodeHandler import EmailCodeHandler # 导入邮件处理模块

# 初始化MongoDB（确保在应用启动时就完成初始化）
try:
    init_mongodb()
    logging.info("MongoDB初始化成功")
except Exception as e:
    logging.error(f"MongoDB初始化失败: {str(e)}")
    raise e

# 导入已初始化的管理器
from mongodb_config import user_manager, chat_manager, message_manager, drawing_analysis_manager

# 注册字体 - 注释掉避免文件不存在错误
# pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))  # 确保路径正确，或使用系统字体路径
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
})  # 配置更详细的CORS设置以支持移动端
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)  # 初始化SocketIO
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
API_KEY = "2n6cCLk2oHeKUWVC8oVaNOHM"
SECRET_KEY = "4sL409ZBtELNDfQZcJRACg6lICmUX6zs"
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])
# 配置密钥
has_SECRET_KEY = 'jjj111@'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ip = 'http://n42294i452.wicp.vip'
text_result = ''

# 用于存储验证码和其过期时间
verification_codes = {}

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def sha256_hash(password):
    # 创建一个sha256哈希对象
    sha_signature = hashlib.sha256(password.encode()).hexdigest()
    return sha_signature

# 管理员凭证 - 实际应用中应存储在数据库中并使用哈希密码
ADMIN_CREDENTIALS = {
    'admin': sha256_hash('admin123')
}

# 用于存储危险对话的全局字典
dangerous_chats = {}
active_admins = {}

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, has_SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token):
    try:
        payload = jwt.decode(token, has_SECRET_KEY, algorithms=[ALGORITHM])
        user_id_data = payload['user_id']
        # 确保返回的是ID字符串，无论存储的是元组还是字符串
        if isinstance(user_id_data, list): # 在jwt中元组会变成列表
            return user_id_data # 返回原列表格式以保持兼容性
        # 如果是字符串，包装成列表以保持兼容性
        return [user_id_data]
    except jwt.ExpiredSignatureError:
        return None  # 令牌已过期
    except jwt.InvalidTokenError:
        return None  # 无效的令牌


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 添加全局OPTIONS处理，支持预检请求
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = Response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# 添加错误处理器
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'status': 'error',
        'message': 'Bad Request - 请求格式不正确',
        'code': 400
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error', 
        'message': 'Not Found - 请求的资源不存在',
        'code': 404,
        'available_endpoints': {
            '根路径': '/',
            'API登录': '/api/login',
            'API注册': '/api/register'
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal Server Error - 服务器内部错误', 
        'code': 500
    }), 500


@app.route('/')
def index():
    """API状态检查端点"""
    return jsonify({
        'status': 'success',
        'message': '绘心同学后端API服务正在运行',
        'version': '1.0.0',
        'timestamp': datetime.datetime.now().isoformat(),
        'endpoints': {
            '登录': '/api/login',
            '注册': '/api/register', 
            '绘画分析': '/api/save',
            '心理对话': '/api/stream-chat',
            '用户信息': '/api/user/info',
            '发送验证码': '/api/send-code'
        }
    })


@app.route('/draw')
def draw():
    try:
        with open('templates/draw.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
            # 返回HTML内容作为响应
        return Response(html_content, mimetype='text/html')
    except FileNotFoundError:
        # 如果文件不存在，返回404错误
        return 'File not found', 404


@app.route('/analyse')
def analyse():
    return render_template('index.html')


@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username_or_email = data.get('username')
        password = data.get('password')
        
        # 先尝试用用户名查找
        user = user_manager.get_user_by_username(username_or_email)
        
        # 如果用户名找不到，尝试用邮箱查找
        if not user:
            user = user_manager.get_user_by_email(username_or_email)
        
        # 如果找到用户并且密码正确
        if user and user_manager.verify_password_by_hash(password, user.get('password')):
            token = generate_token(str(user['_id']))
            # 注意：确保返回格式符合前端预期
            return jsonify({
                'code': 0, 
                'message': '登录成功', 
                'token': token,
                'data': {
                    'token': token,
                    'user': {
                        'id': str(user['_id']),
                        'username': user['username'],
                        'email': user['email'],
                        'avatar': user.get('avatar', '')
                    }
                }
            })
        else:
            return jsonify({'code': 1, 'message': '用户名或密码错误'})
    return render_template('login.html')


@app.route('/api/send-code', methods=['POST'])
def send_verification_code():
    """发送注册验证码"""
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'code': 1, 'message': '邮箱不能为空'}), 400

    # 检查邮箱是否已被注册
    if user_manager.get_user_by_email(email):
        return jsonify({'code': 1, 'message': '该邮箱已被注册'}), 400

    code = EmailCodeHandler.sendEmailCode(email)
    if code:
        # 存储验证码和过期时间（例如，10分钟后）
        verification_codes[email] = {
            'code': code,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        }
        logging.info(f"向 {email} 发送验证码: {code}")
        return jsonify({'code': 0, 'message': '验证码已发送，请注意查收'})
    else:
        logging.error(f"向 {email} 发送验证码失败")
        return jsonify({'code': 1, 'message': '验证码发送失败，请稍后重试'}), 500


@app.route('/api/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        gender = data.get('gender')
        code = data.get('code')

        if not all([username, password, email, gender, code]):
            return jsonify({'code': 1, 'message': '所有字段均为必填项'})

        # 验证验证码
        stored_code_info = verification_codes.get(email)
        if not stored_code_info or stored_code_info['code'] != code:
            return jsonify({'code': 1, 'message': '验证码错误'})
        
        if datetime.datetime.utcnow() > stored_code_info['exp']:
            if email in verification_codes:
                del verification_codes[email]
            return jsonify({'code': 1, 'message': '验证码已过期，请重新发送'})

        if user_manager.get_user_by_username(username):
            return jsonify({'code': 1, 'message': '用户名已存在'})
        if user_manager.get_user_by_email(email):
            return jsonify({'code': 1, 'message': '邮箱已被注册'})
        
        user_manager.create_user(username, password, email, gender)
        
        # 注册成功后删除验证码
        if email in verification_codes:
            del verification_codes[email]
            
        return jsonify({'code': 0, 'message': '注册成功'})
    return render_template('register.html')


@app.route('/api/send-reset-code', methods=['POST'])
def send_reset_code():
    """发送重置密码验证码"""
    try:
        data = request.get_json()
        email = data.get('email')
        if not email:
            return jsonify({'code': 1, 'message': '邮箱不能为空'}), 400

        # 检查邮箱是否存在
        user = user_manager.get_user_by_email(email)
        if not user:
            return jsonify({'code': 1, 'message': '该邮箱未注册'}), 400
        
        code = EmailCodeHandler.sendEmailCode(email)
        if code:
            verification_codes[email] = {
                'code': code,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            }
            return jsonify({'code': 0, 'message': '验证码已发送，请注意查收'})
        else:
            return jsonify({'code': 1, 'message': '验证码发送失败，请稍后重试'}), 500
    except Exception as e:
        return jsonify({'code': 1, 'message': f'验证码发送失败: {str(e)}'}), 500


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return render_template('forgot.html')


@app.route('/privacy')
def privacy():
    # 由于前端已经有Vue路由处理/privacy，我们应该返回前端应用
    return render_template('index.html')  # 返回前端入口文件


@app.route('/api/getusername', methods=['GET'])
def getusername():
    """
    处理获取用户名的请求，并返回JSON格式的响应。
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    try:
        # 从MongoDB获取用户信息
        user = user_manager.get_user_by_id(user_id[0])
        if user:
            return jsonify({'username': user['username']})
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        # 如果发生错误，返回500错误和错误信息
        return jsonify({'error': str(e)}), 500


@app.route('/chat', methods=['GET'])
def chat():
    return render_template('chat.html')


@app.route('/templates/<filename>')
def get_file(filename):
    return send_from_directory('templates', filename)


@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """获取用户详细信息的接口"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        user = user_manager.get_user_by_id(user_id[0])
        if user:
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'chance': user.get('chance', 10),
                    'is_team': user.get('is_team', ''),
                    'avatar': user.get('avatar', ''),
                    'gender': user.get('gender', '')
                }
            })
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        logging.error(f"获取用户信息错误: {str(e)}")
        return jsonify({'message': str(e)}), 500

@app.route('/api/user/analyses', methods=['GET'])
def get_user_analyses():
    """获取用户的绘画分析历史"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        analyses = drawing_analysis_manager.get_user_analyses(user_id[0], limit, page)
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'analyses': analyses,
                'page': page,
                'limit': limit,
                'total': len(analyses)
            }
        })
    except Exception as e:
        logging.error(f"获取用户分析历史错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'获取分析历史失败: {str(e)}'
        }), 500

@app.route('/api/user/today-analysis', methods=['GET'])
def get_today_analysis():
    """获取用户当日的绘画分析结果"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        today_analysis = drawing_analysis_manager.get_today_analysis(user_id[0])
        
        if today_analysis:
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': today_analysis
            })
        else:
            return jsonify({
                'code': 1,
                'message': '今日暂无分析记录'
            }), 404
    except Exception as e:
        logging.error(f"获取当日分析结果错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'获取当日分析结果失败: {str(e)}'
        }), 500

@app.route('/api/user/latest-analysis', methods=['GET'])
def get_latest_analysis():
    """获取用户最新的绘画分析结果（可选择时间限制）"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    # 获取时间限制参数，默认为不限制时间
    time_limit = request.args.get('time_limit', 'none')  # none, today, 4hours
    
    try:
        latest_analysis = None
        
        if time_limit == 'today':
            # 获取当日分析结果
            latest_analysis = drawing_analysis_manager.get_recent_analysis(user_id[0], hours=0)
        elif time_limit == '4hours':
            # 获取4小时内分析结果
            latest_analysis = drawing_analysis_manager.get_recent_analysis(user_id[0], hours=4)
        elif time_limit == 'recent':
            # 获取当日或4小时内的分析结果（优先当日）
            latest_analysis = drawing_analysis_manager.get_recent_analysis(user_id[0], hours=0)
            if not latest_analysis:
                latest_analysis = drawing_analysis_manager.get_recent_analysis(user_id[0], hours=4)
        else:
            # 默认获取最新分析结果（不限时间）
            latest_analysis = drawing_analysis_manager.get_latest_analysis(user_id[0])
        
        if latest_analysis:
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': latest_analysis
            })
        else:
            time_desc = ""
            if time_limit == 'today':
                time_desc = "今日"
            elif time_limit == '4hours':
                time_desc = "4小时内"
            elif time_limit == 'recent':
                time_desc = "当日或4小时内"
            else:
                time_desc = ""
            
            return jsonify({
                'code': 1,
                'message': f'暂无{time_desc}分析记录'
            }), 404
    except Exception as e:
        logging.error(f"获取最新分析结果错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'获取最新分析结果失败: {str(e)}'
        }), 500


url = "https://api.siliconflow.cn/v1/chat/completions"
dangerous = 0
# 使用字典存储每个用户的上下文，避免全局变量混乱
user_contexts = {}
# 存储用户连接的字典
user_connections = {}
# 存储用户当前活跃聊天ID的字典
user_current_chats = {}

# 添加一个API端点，用于清除用户的聊天上下文
@app.route('/api/clear-chat-context', methods=['POST'])
def clear_chat_context():
    # 验证令牌
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
        
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
        
    try:
        user_id_str = str(user_id[0])
        
        # 清除用户特定的上下文
        if user_id_str in user_contexts:
            user_contexts[user_id_str] = []
        
        # 如果用户在危险对话列表中，清除其记录
        if user_id_str in dangerous_chats:
            del dangerous_chats[user_id_str]
            
        # 清除用户的最新图片URL
        if user_id_str in user_latest_images:
            del user_latest_images[user_id_str]
            
        # 注意：不再清除全局text_result，因为现在使用数据库中的分析结果
        
        return jsonify({
            'code': 0,
            'message': '聊天上下文已清除'
        }), 200
        
    except Exception as e:
        print(f"清除聊天上下文错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'清除聊天上下文失败: {str(e)}'
        }), 500

# 新增API：清除用户的当前活跃聊天
@app.route('/api/clear-current-chat', methods=['POST'])
def clear_current_chat():
    """清除用户的当前活跃聊天，下次对话将创建新的聊天"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        user_id_str = str(user_id[0])
        
        # 清除用户的当前活跃聊天
        if user_id_str in user_current_chats:
            old_chat_id = user_current_chats[user_id_str]
            del user_current_chats[user_id_str]
            logging.info(f"清除用户 {user_id_str} 的当前聊天: {old_chat_id}")
        
        # 清除用户的上下文
        if user_id_str in user_contexts:
            user_contexts[user_id_str] = []
        
        return jsonify({
            'code': 0,
            'message': '已清除当前聊天，下次对话将创建新的聊天'
        })
    except Exception as e:
        logging.error(f"清除当前聊天失败: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'清除当前聊天失败: {str(e)}'
        }), 500

# 新增调试API：检查用户的聊天状态
@app.route('/api/debug/chat-status', methods=['GET'])
def debug_chat_status():
    """调试API：检查用户的聊天状态"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        user_id_str = str(user_id[0])
        
        # 获取用户的当前聊天ID
        current_chat = user_current_chats.get(user_id_str, "无")
        
        # 获取用户的上下文长度
        context_length = len(user_contexts.get(user_id_str, []))
        
        # 获取用户的聊天列表
        user_chats = chat_manager.get_user_chats(user_id[0])
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'user_id': user_id_str,
                'current_chat_id': current_chat,
                'context_length': context_length,
                'total_chats': len(user_chats),
                'chat_list': [{'id': str(chat['_id']), 'title': chat['title']} for chat in user_chats[:5]]  # 只显示前5个
            }
        })
    except Exception as e:
        logging.error(f"获取聊天状态失败: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'获取聊天状态失败: {str(e)}'
        }), 500

# 新增聊天管理API
@app.route('/api/chats', methods=['GET'])
def get_user_chats():
    """获取用户的对话列表"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        chats = chat_manager.get_user_chats(user_id[0], page, limit)
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': chats
        })
    except Exception as e:
        logging.error(f"获取对话列表错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'获取对话列表失败: {str(e)}'
        }), 500

@app.route('/api/chats', methods=['POST'])
def create_new_chat():
    """创建新对话"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        data = request.get_json()
        # 初始标题设为空，等第一条消息后再更新
        title = data.get('title', '')
        chat_type = data.get('type', 'normal')  # 新增：支持传入对话类型
        
        chat_id = chat_manager.create_chat(user_id[0], title, chat_type)
        
        # 设置为当前活跃聊天 - 统一使用字符串类型用户ID
        user_id_str = str(user_id[0])
        user_current_chats[user_id_str] = chat_id
        
        # 清除用户的当前上下文，开始新对话
        user_contexts[user_id_str] = []
        
        logging.info(f"用户 {user_id_str} 创建新对话: {chat_id}")
        
        return jsonify({
            'code': 0,
            'message': '创建对话成功',
            'data': {
                'chat_id': chat_id,
                'title': title if title else '新对话'
            }
        })
    except Exception as e:
        logging.error(f"创建新对话错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'创建新对话失败: {str(e)}'
        }), 500

@app.route('/api/chats/<chat_id>', methods=['DELETE'])
def hide_chat(chat_id):
    """隐藏对话（软删除）"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        # 验证对话是否属于当前用户
        chat = chat_manager.get_chat_by_id(chat_id)
        if not chat or chat['user_id'] != user_id[0]:
            return jsonify({
                'code': 1,
                'message': '对话不存在或无权限'
            }), 404
        
        success = chat_manager.hide_chat(chat_id)
        if success:
            return jsonify({
                'code': 0,
                'message': '删除对话成功'
            })
        else:
            return jsonify({
                'code': 1,
                'message': '删除对话失败'
            }), 500
    except Exception as e:
        logging.error(f"删除对话错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'删除对话失败: {str(e)}'
        }), 500

@app.route('/api/chats/<chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id):
    """获取对话的消息历史"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        # 验证对话是否属于当前用户
        chat = chat_manager.get_chat_by_id(chat_id)
        if not chat or chat['user_id'] != user_id[0]:
            return jsonify({
                'code': 1,
                'message': '对话不存在或无权限'
            }), 404
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        group_messages = request.args.get('group', 'false').lower() == 'true'
        
        # 使用新的方法获取完整对话和消息
        full_chat = message_manager.get_chat_with_messages(chat_id)
        if not full_chat:
            return jsonify({
                'code': 1,
                'message': '对话不存在'
            }), 404
        
        all_messages = full_chat.get('messages', [])
        
        # 分页处理
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        messages = all_messages[start_idx:end_idx]
        
        # 如果需要分组消息（用于可折叠显示）
        if group_messages:
            grouped_messages = []
            current_group = None
            
            for msg in messages:
                if current_group is None or current_group['sender'] != msg['sender']:
                    # 开始新的消息组
                    current_group = {
                        'sender': msg['sender'],
                        'timestamp': msg['timestamp'],
                        'messages': [msg],
                        'collapsed': False  # 默认展开
                    }
                    grouped_messages.append(current_group)
                else:
                    # 添加到当前组
                    current_group['messages'].append(msg)
                    current_group['timestamp'] = msg['timestamp']  # 更新为最新时间
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'chat': {
                        '_id': full_chat['_id'],
                        'title': full_chat['title'],
                        'created_at': full_chat['created_at'],
                        'updated_at': full_chat['updated_at'],
                        'message_count': full_chat['message_count']
                    },
                    'messages': grouped_messages,
                    'total_groups': len(grouped_messages),
                    'total_messages': len(all_messages)
                }
            })
        else:
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'chat': {
                        '_id': full_chat['_id'],
                        'title': full_chat['title'],
                        'created_at': full_chat['created_at'],
                        'updated_at': full_chat['updated_at'],
                        'message_count': full_chat['message_count']
                    },
                    'messages': messages,
                    'total_messages': len(all_messages)
                }
            })
    except Exception as e:
        logging.error(f"获取消息历史错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'获取消息历史失败: {str(e)}'
        }), 500

@app.route('/api/chats/<chat_id>/load', methods=['POST'])
def load_chat_context(chat_id):
    """加载对话上下文"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        # 验证对话是否属于当前用户
        chat = chat_manager.get_chat_by_id(chat_id)
        if not chat or chat['user_id'] != user_id[0]:
            return jsonify({
                'code': 1,
                'message': '对话不存在或无权限'
            }), 404
        
        # 设置为当前活跃聊天 - 统一使用字符串类型用户ID
        user_id_str = str(user_id[0])
        user_current_chats[user_id_str] = chat_id
        
        # 获取最近的消息作为上下文
        recent_messages = message_manager.get_latest_messages(chat_id, 10)
        
        logging.info(f"用户 {user_id_str} 切换到对话: {chat_id}")
        
        # 更新用户特定的上下文（user_id_str已在上面定义）
        user_contexts[user_id_str] = []
        
        for msg in recent_messages:
            if msg['sender'] == 'user':
                user_contexts[user_id_str].append({
                    "role": "user",
                    "content": msg['content']
                })
            elif msg['sender'] == 'assistant':
                user_contexts[user_id_str].append({
                    "role": "assistant", 
                    "content": msg['content']
                })
        
        return jsonify({
            'code': 0,
            'message': '对话上下文加载成功',
            'data': {
                'chat': chat,
                'context_loaded': len(user_contexts[user_id_str])
            }
        })
    except Exception as e:
        logging.error(f"加载对话上下文错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'加载对话上下文失败: {str(e)}'
        }), 500

@app.route('/api/chats/<chat_id>/toggle-group', methods=['POST'])
def toggle_message_group(chat_id):
    """切换消息组的折叠状态"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    
    try:
        # 验证对话是否属于当前用户
        chat = chat_manager.get_chat_by_id(chat_id)
        if not chat or chat['user_id'] != user_id[0]:
            return jsonify({
                'code': 1,
                'message': '对话不存在或无权限'
            }), 404
        
        data = request.get_json()
        group_index = data.get('group_index')
        collapsed = data.get('collapsed', False)
        
        # 这里可以将折叠状态保存到用户偏好设置中
        # 目前只返回成功响应，前端可以本地管理状态
        
        return jsonify({
            'code': 0,
            'message': '状态更新成功',
            'data': {
                'group_index': group_index,
                'collapsed': collapsed
            }
        })
    except Exception as e:
        logging.error(f"切换消息组状态错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'操作失败: {str(e)}'
        }), 500

def process_message(message):
    global dangerous
    try:
        logging.info(f"🔍 开始检测消息危险性: {message[:50]}...")
        
        # 先检查明显的危险关键词
        danger_keywords = ['自杀', '自残', '死', '想死', '活不下去', '结束生命', '轻生']
        has_danger_keyword = any(keyword in message for keyword in danger_keywords)
        
        if has_danger_keyword:
            logging.warning(f"🚨 检测到危险关键词: {message}")
            dangerous = 0.9  # 强制设置为高危险级别
            label = "危险"
        else:
            # 使用模型进行预测
            label, probs = classifier.predict(message)
            # probs是一个数组[危险概率, 负面概率, 其他概率]
            # 根据模型定义：0: "危险", 1: "负面", 2: "其他"
            dangerous = probs[0]  # 危险类别的概率
        
        logging.info(f"🎯 危险检测结果: label={label}, dangerous_prob={dangerous:.4f}")
        return dangerous
    except Exception as e:
        logging.error(f"❌ 情感分析模型预测失败: {str(e)}")
        # 如果模型预测失败，但包含危险关键词，仍然标记为危险
        danger_keywords = ['自杀', '自残', '死', '想死', '活不下去', '结束生命', '轻生']
        if any(keyword in message for keyword in danger_keywords):
            dangerous = 0.9
        else:
            dangerous = 0.0
        return dangerous


@app.route('/api/test-danger-detection', methods=['POST'])
def test_danger_detection():
    """测试危险检测功能的API端点"""
    try:
        data = request.get_json()
        test_message = data.get('message', '')
        
        if not test_message:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 直接调用危险检测函数
        danger_score = process_message(test_message)
        
        return jsonify({
            'message': test_message,
            'danger_score': float(danger_score),
            'is_dangerous': danger_score > 0.3,
            'threshold': 0.3
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stream-chat', methods=['POST'])
def stream_chat():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
    user = request.json
    if not user:
        return Response("Invalid JSON or missing request body", status=400)
    user_message = user.get('message', '')

    # 检测消息是否危险
    logging.info(f"📝 开始处理用户消息: {user_message[:30]}...")
    
    # 启用危险检测
    thread = threading.Thread(target=process_message, args=(user_message,))
    thread.start()
    thread.join()  # 等待线程完成
    
    logging.info(f"⚠️ 危险检测完成，dangerous值: {dangerous}")
    
    # 获取或创建当前聊天 - 统一使用字符串类型的用户ID
    # 兼容 user_id 可能为字符串或列表
    if isinstance(user_id, (list, tuple)):
        user_id_str = str(user_id[0])
        username = user_id[1] if len(user_id) > 1 else "未知用户"
    else:
        user_id_str = str(user_id)
        username = "未知用户"

    current_chat_id = user_current_chats.get(user_id_str)

    if not current_chat_id:
        chat_type = "dangerous" if dangerous > 0.5 else "normal"
        current_chat_id = chat_manager.create_chat(user_id_str, "新对话", chat_type)
        user_current_chats[user_id_str] = current_chat_id
        logging.info(f"为用户 {user_id_str} 创建新对话: {current_chat_id}")
    else:
        logging.info(f"用户 {user_id_str} 使用现有对话: {current_chat_id}")

    if dangerous > 0.3:
        logging.warning(f"🚨 触发危险检测: dangerous={dangerous:.4f} > 0.3")
        chat_manager.update_chat(current_chat_id, {"type": "dangerous"})
        logging.warning(f'🚨 检测到危险消息，需要人工干预: {user_message}')
        user_context = user_contexts.get(user_id_str, [])
        if user_id_str not in dangerous_chats:
            dangerous_chats[user_id_str] = {
                'username': username,
                'chat_id': current_chat_id,
                'messages': user_context.copy() + [
                    {"role": "user", "content": user_message}
                ],
                'is_active': True,
                'admin_id': None,
                'last_updated': datetime.datetime.now().isoformat()
            }
        else:
            dangerous_chats[user_id_str]['messages'].append({
                "role": "user",
                "content": user_message
            })
            dangerous_chats[user_id_str]['last_updated'] = datetime.datetime.now().isoformat()
        
        # 保存用户消息到MongoDB
        try:
            message_manager.add_message(
                chat_id=current_chat_id,
                message_type="text",
                content=user_message,
                sender="user",
                danger_level=dangerous
            )
        except Exception as e:
            logging.error(f"保存危险消息失败: {str(e)}")
        
        # 通知所有在线管理员有新的危险对话
        logging.info(f"🔔 准备通知管理员危险对话，user_id: {user_id_str}")
        socketio.emit('dangerous_chat_alert', {
            'user': {
                'userId': user_id_str,
                'username': username,
                'lastMessage': user_message
            }
        }, room='admin_room')
        logging.info(f"✅ 已发送危险对话通知到admin_room")
        
        # 检查是否有管理员在线
        admin_message = "系统检测到您的内容可能存在风险，已切换到人工客服模式。请稍等片刻，管理员正在审核您的对话..."
        
        # 添加系统消息到危险对话记录
        dangerous_chats[user_id_str]['messages'].append({
            "role": "admin", 
            "content": admin_message,
            "time": datetime.datetime.now().isoformat(),
            "is_system": True,
            "messageId": "system_risk_alert"  # 添加固定messageId用于前端去重
        })
        
        # 保存系统消息到MongoDB
        try:
            message_manager.add_message(
                chat_id=current_chat_id,
                message_type="text",
                content=admin_message,
                sender="system",
                danger_level=dangerous
            )
        except Exception as e:
            logging.error(f"保存系统消息失败: {str(e)}")
        
        # 返回流式格式的系统提示，确保前端能正确处理
        def generate_admin_message():
            for char in admin_message:
                yield char
        
        return Response(
            stream_with_context(generate_admin_message()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )
    
    # 如果消息不危险，正常处理
    # 每次对话都重新获取用户在当日或4小时内的最新绘画分析结果
    latest_analysis = None
    analysis_fetch_time = datetime.datetime.utcnow()
    
    try:
        logging.info(f"开始获取用户 {user_id[0]} 的最新分析结果...")
        
        # 首先尝试获取当日的分析结果
        latest_analysis = drawing_analysis_manager.get_recent_analysis(user_id[0], hours=0)
        
        if not latest_analysis:
            # 如果当日没有分析结果，尝试获取4小时内的分析结果
            latest_analysis = drawing_analysis_manager.get_recent_analysis(user_id[0], hours=4)
        
        if latest_analysis:
            analysis_date = latest_analysis['analysis_date']
            analysis_time = latest_analysis['created_at']
            analysis_id = latest_analysis.get('_id', 'unknown')
            logging.info(f"✅ 成功获取用户 {user_id[0]} 的分析结果 - ID: {analysis_id}, 日期: {analysis_date}, 创建时间: {analysis_time}")
        else:
            logging.info(f"ℹ️  用户 {user_id[0]} 在当日或4小时内暂无分析记录")
    except Exception as e:
        logging.error(f"❌ 获取用户 {user_id[0]} 的分析结果失败: {str(e)}")
    
    # 构建系统消息 - 完全基于数据库中的最新分析结果
    if latest_analysis:
        analysis_date = latest_analysis['analysis_date']
        analysis_result = latest_analysis['analysis_result']
        system_content = f"你现在是一名心理医师，你的名字叫绘心同学。用户在{analysis_date}完成了心理绘画测试，以下是最新的分析结果：{analysis_result} \n\n请结合这个分析结果帮助用户，用通俗易懂的语言与用户交流，用多轮对话的形式，每次别说太多。如果用户的问题与绘画分析相关，请参考分析结果给出建议。"
        logging.info(f"🎯 AI将基于 {analysis_date} 的分析结果进行对话")
    else:
        # 如果没有符合时间条件的分析结果，不参考任何分析内容
        system_content = "你现在是一名心理医师，你的名字叫绘心同学。请用温暖、专业的语言与用户交流，用多轮对话的形式，每次别说太多。如果用户需要心理绘画分析，请引导他们先完成绘画测试。"
        logging.info("🔄 AI将不参考任何分析结果进行对话（无符合时间条件的分析）")
    
    # 获取用户的上下文
    user_id_str = str(user_id[0])
    user_context = user_contexts.get(user_id_str, [])
    
    messages = [
        {
            "content": system_content,
            "role": "system"
        }
    ] + user_context.copy() + [
        {"content": user_message, "role": "user"}
    ]
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",
        "stream": True,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "stop": [],
        "messages": messages
    }
    headers = {
        "Authorization": "Bearer sk-bhgbmuxblqtroypztkuonssqqkitngencupdofitajnmvbtv",
        "Content-Type": "application/json"
    }

    def generate():
        assistant_reply = ''
        try:
            # 先保存用户消息到MongoDB
            user_message_id = message_manager.add_message(
                chat_id=current_chat_id,
                message_type="text",
                content=user_message,
                sender="user"
            )
            
            # 发起 POST 请求，启用流式响应
            with requests.post(url, json=payload, headers=headers, stream=True) as response:
                response.raise_for_status()  # 检查响应状态码
                response.encoding = 'utf-8'  # 明确指定编码

                # 逐行读取响应内容
                for line in response.iter_lines(decode_unicode=True):
                    if line:  # 跳过空行
                        # 假设 API 返回的是 SSE 格式，每行以 "data: " 开头
                        if line.startswith("data: "):
                            try:
                                # 提取数据部分并解析为 JSON
                                data = line[len("data: "):].strip()
                                if data == "[DONE]":
                                    # 如果遇到 [DONE]，结束生成器
                                    break
                                json_data = json.loads(data)

                                # 提取所需字段（根据 API 响应格式调整）
                                # 假设响应中有 'choices[0]['delta']['content']'
                                content = json_data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                assistant_reply += content
                                if content:
                                    yield f"{content}"
                            except json.JSONDecodeError:
                                # 如果 JSON 解析失败，记录错误（或跳过）
                                print(f"Failed to parse JSON: {line}")
            
            # 成功获取完整回复后保存助手消息到MongoDB
            if assistant_reply:
                assistant_message_id = message_manager.add_message(
                    chat_id=current_chat_id,
                    message_type="text",
                    content=assistant_reply,
                    sender="assistant"
                )
            
            # 更新用户特定的上下文
            if user_id_str not in user_contexts:
                user_contexts[user_id_str] = []
            
            user_contexts[user_id_str].extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_reply}
            ])
            # 保留最多5轮对话（10条消息）
            if len(user_contexts[user_id_str]) > 10:
                user_contexts[user_id_str] = user_contexts[user_id_str][-10:]
            
            # 始终更新对话标题为用户的最新消息（对话结束前的最后一条语言）
            try:
                # 截取用户消息的前20个字符作为标题
                new_title = user_message[:20] + "..." if len(user_message) > 20 else user_message
                chat_manager.update_chat_title(current_chat_id, new_title)
            except Exception as e:
                logging.error(f"更新对话标题失败: {str(e)}")
                
        except requests.RequestException as e:
            # 处理请求异常，例如网络错误或 API 返回错误状态码
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            # 处理其他异常，如数据库保存错误
            logging.error(f"聊天处理错误: {str(e)}")
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    # 返回流式响应
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )


# 保存绘画的文件夹
SAVE_DIR = "saved_drawings"
os.makedirs(SAVE_DIR, exist_ok=True)

def image_to_data_url(file_path):
    """将图片文件转换为 data URL"""
    try:
        # 确定文件的 MIME 类型
        mime_type = "image/jpeg"  # 默认值
        if file_path.lower().endswith('.png'):
            mime_type = "image/png"
        elif file_path.lower().endswith('.gif'):
            mime_type = "image/gif"
        elif file_path.lower().endswith('.webp'):
            mime_type = "image/webp"

        # 读取文件并转换为 base64
        with open(file_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # 返回完整的 data URL
        return f"data:{mime_type};base64,{encoded_image}"
    except Exception as e:
        print(f"Error converting image to data URL: {str(e)}")
        return None

# 添加一个字典来存储用户的最新图片URL
user_latest_images = {}

@app.route('/api/save', methods=['POST'])
def save_drawing():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token!'}), 401
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': '没有接收到数据'}), 400
            
        image_data = data.get('image', '')
        is_uploaded = data.get('isUploaded', False)
        
        if not image_data:
            return jsonify({'message': '未接收到图像数据'}), 400
            
        try:
            # 处理 Base64 数据
            logging.info(f"Processing image data, size: {len(image_data)} characters")
            
            if 'base64,' in image_data:
                header, image_data = image_data.split('base64,', 1)
                logging.info(f"Extracted base64 data from header: {header[:50]}...")
            
            # 清理Base64字符串，移除任何非base64字符
            original_length = len(image_data)
            image_data = re.sub(r'[^A-Za-z0-9+/=]', '', image_data)
            if len(image_data) != original_length:
                logging.info(f"Cleaned base64 string, removed {original_length - len(image_data)} invalid characters")
            
            # 补充缺失的填充
            missing_padding = len(image_data) % 4
            if missing_padding:
                padding = '=' * (4 - missing_padding)
                image_data += padding
                logging.info(f"Added {len(padding)} padding characters")
                
            # 解码 Base64 数据
            try:
                image_bytes = base64.b64decode(image_data)
                logging.info(f"Successfully decoded base64 data to {len(image_bytes)} bytes")
            except Exception as decode_error:
                logging.error(f"Base64 decode failed: {str(decode_error)}")
                return jsonify({'message': f'图像数据解码失败: {str(decode_error)}'}), 400
            
            # 验证图像数据
            if len(image_bytes) < 100:  # 太小的文件可能不是有效图像
                logging.error(f"Image data too small: {len(image_bytes)} bytes")
                return jsonify({'message': '图像数据太小，可能无效'}), 400
            
            # 生成文件名和保存图片
            file_name = f"drawing_{len(os.listdir(SAVE_DIR)) + 1}.png"
            file_path = os.path.join(SAVE_DIR, file_name)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            logging.info(f"Image saved successfully: {file_path}")
                
            # 保存用户最新的图片URL
            user_latest_images[str(user_id[0])] = file_path
            
            # 如果是分析请求，则进行AI分析
            should_analyze = data.get('analyze', False)
            if should_analyze:
                logging.info(f"Starting analysis for image: {file_name}")
                try:
                    return analyze_image(file_path, file_name, user_id[0])  # 传递用户ID
                except Exception as analysis_error:
                    logging.error(f"Analysis failed for {file_name}: {str(analysis_error)}")
                    # 即使分析失败，图片已经保存成功，返回文件信息
                    return jsonify({
                        'message': f'图片保存成功，但分析失败: {str(analysis_error)}',
                        'file_name': file_name,
                        'error': str(analysis_error)
                    }), 200  # 使用200状态码，因为保存成功了
                
            # 否则只返回保存成功的消息
            return jsonify({
                'message': '图像保存成功',
                'file_name': file_name
            }), 200
                
        except Exception as e:
            logging.error(f"Image processing error: {str(e)}")
            return jsonify({'message': f'图像处理失败: {str(e)}'}), 400
            
    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({'message': f'保存失败: {str(e)}'}), 500

def analyze_image(file_path, file_name, user_id=None):
    """分析图片的函数"""
    logging.info(f"Starting analyze_image function for {file_name} at {file_path}, user_id: {user_id}")
    
    try:
        if not os.path.exists(file_path):
            logging.error(f"File not found for analysis: {file_path}")
            return jsonify({'message': '找不到要分析的图片文件'}), 404
            
        # 验证文件大小
        file_size = os.path.getsize(file_path)
        logging.info(f"Analyzing image {file_name}, size: {file_size} bytes")
        
        if file_size == 0:
            return jsonify({'message': '图片文件为空'}), 400
        
        if file_size > 10 * 1024 * 1024:  # 10MB限制
            return jsonify({'message': '图片文件太大，请压缩后重试'}), 400
            
        # 初始化AI客户端
        try:
            # 创建自定义httpx客户端避免代理问题
            http_client = httpx.Client()
            client = OpenAI(
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                api_key="d618ffd5-dd7c-4548-8cde-a82ba550f808",
                http_client=http_client
            )
            logging.info("AI client initialized successfully")
        except Exception as client_error:
            logging.error(f"Failed to initialize AI client: {str(client_error)}")
            return jsonify({'message': f'AI客户端初始化失败: {str(client_error)}'}), 500
        
        data_url = image_to_data_url(file_path)
        if not data_url:
            logging.error(f"Failed to convert image to data URL: {file_path}")
            return jsonify({'message': '图片转换失败'}), 500
        
        logging.info(f"Starting AI analysis for image: {file_name}")
        
        try:
            response = client.chat.completions.create(
                model="doubao-1-5-vision-pro-32k-250115",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url}
                        },
                        {"type": "text", "text": '''
                        你是一个专业的心理分析师，请根据绘画静态数据：
                        房、树、人的高清图像（需包含笔触细节）或以下结构化描述：
                        尺寸/布局：各元素在纸上的位置、比例（如房屋占纸面50%、人物位于右下角）。
                        线条特征：轻/重笔压、断续线条、反复涂抹区域。
                        细节程度：门窗结构、树叶纹理、人物五官/手指等是否完整。
                        特殊符号：天气（雨，太阳）、附加物（围墙，动物）
                        进行专业分析用户的房树人绘画，并参考以下可以涉及的分析方面：
                        
                        ### 绘画描述
                        请详细描述画面中的内容，包括房屋、树木、人物的位置、大小和特征。
                        
                        ### 分析概述  
                        基于绘画内容进行整体心理状态评估。
                        
                        ### 具体分析
                        从以下几个维度进行分析：
                        1. 情绪状态：通过线条力度、色彩选择等判断
                        2. 人际关系：通过元素间距离、比例关系等分析
                        3. 自我认知：通过人物描绘的详细程度等评估
                        
                        ### 用户心理画像
                        综合分析结果，给出用户当前的心理状态评估和建议。
                        
                        若图片不是房树人相关绘画，请温和地引导用户重新绘制房树人作品。
                        '''}
                    ]
                }],
                max_tokens=4000,
                temperature=0.7
            )
            
            # 检查响应
            if not response or not response.choices:
                logging.error("AI service returned empty response")
                return jsonify({'message': 'AI分析服务返回空响应，请稍后重试'}), 500
            
            # 获取分析结果
            analysis_result = response.choices[0].message.content
            
            if not analysis_result or len(analysis_result.strip()) == 0:
                logging.error("AI analysis returned empty content")
                return jsonify({'message': 'AI分析返回空内容，请稍后重试'}), 500
            
            # 更新全局变量
            global text_result
            text_result = analysis_result
            
            # 保存分析结果到数据库
            if user_id:
                try:
                    analysis_id = drawing_analysis_manager.save_analysis(
                        user_id=user_id,
                        image_path=file_path,
                        analysis_result=analysis_result,
                        image_size=f"{len(open(file_path, 'rb').read())} bytes",
                        analysis_type="house_tree_person",
                        ai_model="doubao-1-5-vision-pro-32k",
                    )
                    logging.info(f"Analysis result saved to database with ID: {analysis_id}")
                except Exception as db_error:
                    logging.error(f"Failed to save analysis to database: {str(db_error)}")
                    # 继续执行，不因为数据库保存失败而影响返回结果
            
            logging.info(f"Analysis completed successfully for image: {file_name}, result length: {len(analysis_result)}")
            
            # 构建返回数据
            return_data = {
                'message': '分析完成',
                'analysis': analysis_result,
                'file_name': file_name
            }
            
            logging.info(f"Returning analysis result: {return_data}")
            
            return jsonify(return_data), 200
            
        except Exception as api_error:
            logging.error(f"AI API error for {file_name}: {str(api_error)}")
            return jsonify({
                'message': 'AI分析服务暂时不可用，请稍后重试',
                'file_name': file_name
            }), 503
        
    except Exception as e:
        logging.error(f"General analysis error for {file_name}: {str(e)}")
        return jsonify({
            'message': f'分析过程中出现错误，请稍后重试', 
            'file_name': file_name
        }), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')
    
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'code': 1, 'message': '无效或过期的链接'})
    
    try:
        user_manager.update_password_by_id(user_id, new_password)
        return jsonify({'code': 0, 'message': '密码重置成功'})
    except Exception as e:
        return jsonify({'code': 1, 'message': f'密码重置失败: {str(e)}'})

@app.route('/api/update-password', methods=['POST'])
def update_password():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'code': 1, 'message': '未提供授权码'}), 401
    
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'code': 1, 'message': '无效或过期的授权码'}), 401
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    try:
        user = user_manager.get_user_by_id(user_id)
        if not user_manager.verify_password(user['username'], old_password):
            return jsonify({'code': 1, 'message': '旧密码不正确'})
        
        user_manager.update_password_by_id(user_id, new_password)
        return jsonify({'code': 0, 'message': '密码更新成功'})
    except Exception as e:
        return jsonify({'code': 1, 'message': f'密码更新失败: {str(e)}'})

@app.route('/api/reset-password-direct', methods=['POST'])
def reset_password_direct():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    code = data.get('code')

    if not all([email, password, code]):
        return jsonify({'code': 1, 'message': '所有字段均为必填项'})

    # 验证验证码
    stored_code_info = verification_codes.get(email)
    if not stored_code_info or stored_code_info['code'] != code:
        return jsonify({'code': 1, 'message': '验证码错误'})

    if datetime.datetime.utcnow() > stored_code_info['exp']:
        if email in verification_codes:
            del verification_codes[email]
        return jsonify({'code': 1, 'message': '验证码已过期，请重新发送'})

    user = user_manager.get_user_by_email(email)
    if not user:
        return jsonify({'code': 1, 'message': '该邮箱未注册'})
    
    try:
        user_id = str(user['_id'])
        result = user_manager.update_password_by_id(user_id, password)
        
        if result:
            # 成功后删除验证码
            if email in verification_codes:
                del verification_codes[email]
            return jsonify({'code': 0, 'message': '密码重置成功'})
        else:
            return jsonify({'code': 1, 'message': '密码重置失败，请稍后再试'})
    except Exception as e:
        return jsonify({'code': 1, 'message': f'密码重置失败: {str(e)}'})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'code': 1,
            'message': '请提供用户名和密码'
        }), 400
    
    # 验证管理员凭证
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == sha256_hash(password):
        # 生成管理员令牌
        token = generate_admin_token(username)
        
        return jsonify({
            'code': 0,
            'message': '登录成功',
            'token': token
        }), 200
    else:
        return jsonify({
            'code': 1,
            'message': '用户名或密码错误'
        }), 401

# 生成管理员令牌
def generate_admin_token(admin_username):
    payload = {
        'admin_username': admin_username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, has_SECRET_KEY, algorithm=ALGORITHM)

# 验证管理员令牌
def verify_admin_token(token):
    try:
        payload = jwt.decode(token, has_SECRET_KEY, algorithms=[ALGORITHM])
        admin_username = payload['admin_username']
        return admin_username if admin_username in ADMIN_CREDENTIALS else None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# 添加管理员回复接口
@app.route('/api/admin/reply', methods=['POST'])
def admin_reply():
    # 验证管理员权限
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    
    admin_username = verify_admin_token(token)
    if not admin_username:
        return jsonify({'message': 'Invalid admin token!'}), 401
    
    # 获取请求数据
    data = request.get_json()
    user_id = data.get('userId')
    admin_message = data.get('message')
    
    if not user_id or not admin_message:
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # 检查用户是否在危险对话列表中
    if user_id not in dangerous_chats:
        return jsonify({'message': 'User not found in dangerous chats!'}), 404
    
    # 添加管理员回复到对话记录
    dangerous_chats[user_id]['messages'].append({
        "role": "admin",
        "content": admin_message
    })
    
    # 返回成功响应
    return jsonify({
        'code': 0,
        'message': '回复成功'
    }), 200

# 获取危险对话列表
@app.route('/api/admin/dangerous-chats', methods=['GET'])
def get_dangerous_chats():
    # 验证管理员权限
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    
    admin_username = verify_admin_token(token)
    if not admin_username:
        return jsonify({'message': 'Invalid admin token!'}), 401
    
    # 准备返回数据
    chat_list = []
    for user_id, chat_data in dangerous_chats.items():
        # 只获取最近一条消息作为预览
        last_message = ""
        if chat_data['messages']:
            last_message = chat_data['messages'][-1]['content']
        
        chat_list.append({
            'userId': user_id,
            'username': chat_data['username'],
            'lastMessage': last_message[:50] + "..." if len(last_message) > 50 else last_message,
            'isActive': chat_data['is_active']
        })
    
    return jsonify({
        'code': 0,
        'chats': chat_list
    }), 200

# 获取特定用户的对话历史
@app.route('/api/admin/chat-history/<user_id>', methods=['GET'])
def get_chat_history(user_id):
    # 验证管理员权限
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    
    admin_username = verify_admin_token(token)
    if not admin_username:
        return jsonify({'message': 'Invalid admin token!'}), 401
    
    # 检查用户是否在危险对话列表中
    if user_id not in dangerous_chats:
        return jsonify({'message': 'User not found in dangerous chats!'}), 404
    
    # 返回对话历史
    return jsonify({
        'code': 0,
        'messages': dangerous_chats[user_id]['messages']
    }), 200

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    # 如果是管理员断开连接，更新状态
    sid = request.sid
    for admin_id, data in active_admins.items():
        if data.get('sid') == sid:
            del active_admins[admin_id]
            print(f'Admin {admin_id} disconnected')
            break

# 管理员认证
@socketio.on('admin_auth')
def handle_admin_auth(data):
    token = data.get('token')
    if not token:
        emit('auth_response', {'status': 'error', 'message': 'Token is missing'})
        return
    
    admin_username = verify_admin_token(token)
    if not admin_username:
        emit('auth_response', {'status': 'error', 'message': 'Invalid token'})
        return
    
    # 保存管理员的会话ID
    sid = request.sid
    active_admins[admin_username] = {
        'sid': sid,
        'connected_at': datetime.datetime.now().isoformat()
    }
    
    # 将管理员加入管理员房间
    join_room('admin_room')
    
    # 发送认证成功响应
    emit('auth_response', {'status': 'success', 'message': 'Authentication successful'})
    
    # 发送当前所有危险对话列表
    chat_list = []
    for user_id, chat_data in dangerous_chats.items():
        # 只获取最近一条消息作为预览
        last_message = ""
        if chat_data['messages']:
            last_message = chat_data['messages'][-1]['content']
        
        chat_list.append({
            'userId': user_id,
            'username': chat_data['username'],
            'lastMessage': last_message[:50] + "..." if len(last_message) > 50 else last_message,
            'isActive': chat_data['is_active']
        })
    
    emit('dangerous_chats_list', {'chats': chat_list})

# 请求用户聊天历史
@socketio.on('request_history')
def handle_request_history(data):
    # 验证是否为管理员
    sid = request.sid
    admin_username = None
    for username, admin_data in active_admins.items():
        if admin_data.get('sid') == sid:
            admin_username = username
            break
    
    if not admin_username:
        emit('error', {'message': 'Unauthorized'})
        return
    
    user_id = data.get('userId')
    if not user_id or user_id not in dangerous_chats:
        emit('error', {'message': 'User not found'})
        return
    
    # 发送历史记录
    emit('chat_history', {
        'userId': user_id,
        'username': dangerous_chats[user_id]['username'],
        'messages': dangerous_chats[user_id]['messages']
    })
    
    # 设置该管理员为当前处理该用户的管理员
    dangerous_chats[user_id]['admin_id'] = admin_username

# 用户WebSocket连接事件
@socketio.on('user_connect')
def handle_user_connect(data):
    token = data.get('token')
    user_id = None
    username = None
    # 优先使用前端传递的 userId 和 username
    if 'userId' in data and 'username' in data:
        user_id_str = str(data['userId'])
        username = data['username']
        # 校验token有效性
        if token:
            user_id_check = verify_token(token)
            if not user_id_check or (isinstance(user_id_check, (list, tuple)) and str(user_id_check[0]) != user_id_str):
                emit('error', {'message': 'Invalid token'})
                return
    else:
        if not token:
            emit('error', {'message': 'Token is missing'})
            return
        user_id = verify_token(token)
        if not user_id:
            emit('error', {'message': 'Invalid token'})
            return
        if isinstance(user_id, (list, tuple)):
            user_id_str = str(user_id[0])
            username = user_id[1] if len(user_id) > 1 else "未知用户"
        else:
            user_id_str = str(user_id)
            username = "未知用户"

    user_connections[user_id_str] = {
        'sid': request.sid,
        'username': username,
        'connected_at': datetime.datetime.now().isoformat()
    }

    join_room(f'user_{user_id_str}')
    emit('connect_response', {'status': 'success', 'message': 'Connection successful'})

    if user_id_str in dangerous_chats:
        admin_messages = [
            msg for msg in dangerous_chats[user_id_str]['messages']
            if msg.get('role') == 'admin' and (
                (msg.get('messageId') != 'system_risk_alert') or
                not msg.get('is_system', False)
            )
        ]
        if admin_messages:
            recent_messages = admin_messages[-3:] if len(admin_messages) > 3 else admin_messages
            for msg in recent_messages:
                socketio.emit('admin_reply', {
                    'role': 'admin',
                    'content': msg.get('content'),
                    'time': msg.get('time', datetime.datetime.now().isoformat()),
                    'messageId': msg.get('messageId')
                }, room=f'user_{user_id_str}')

    print(f'User {username} connected with SID: {request.sid}')

# 管理员发送消息给用户
@socketio.on('admin_message')
def handle_admin_message(data):
    # 验证是否为管理员
    sid = request.sid
    admin_username = None
    for username, admin_data in active_admins.items():
        if admin_data.get('sid') == sid:
            admin_username = username
            break
    
    if not admin_username:
        emit('error', {'message': 'Unauthorized'})
        return
    
    user_id = str(data.get('userId'))
    content = data.get('content')
    message_id = data.get('messageId')  # 获取消息ID
    
    if not user_id or not content or user_id not in dangerous_chats:
        emit('error', {'message': 'Invalid request'})
        return
    
    current_time = datetime.datetime.now().isoformat()
    
    # 添加消息到危险对话记录
    dangerous_chats[user_id]['messages'].append({
        'role': 'admin',
        'content': content,
        'time': current_time,
        'messageId': message_id  # 存储消息ID
    })
    
    # 保存管理员消息到数据库
    try:
        chat_id = dangerous_chats[user_id].get('chat_id')
        if chat_id:
            message_manager.add_message(
                chat_id=chat_id,
                message_type="text",
                content=content,
                sender="admin"
            )
    except Exception as e:
        logging.error(f"保存管理员消息失败: {str(e)}")
    
    # 发送消息给所有管理员，更新聊天状态
    emit('new_message', {
        'userId': user_id,
        'role': 'admin',
        'content': content,
        'sender': admin_username,
        'time': current_time,
        'messageId': message_id  # 添加消息ID
    }, room='admin_room')
    
    # 向用户发送消息 - 检查用户是否有活跃的会话
    if user_id in user_connections:
        # 向用户的房间发送消息
        socketio.emit('admin_reply', {
            'role': 'admin',
            'content': content,
            'time': current_time,
            'messageId': message_id  # 添加消息ID
        }, room=f'user_{user_id}')
    else:
        # 如果用户不在线，将消息标记为未读，等用户重连时发送
        print(f"User {user_id} is not connected, message will be delivered when they reconnect")

# 用户发送消息
@socketio.on('user_message')
def handle_user_message(data):
    # 获取用户ID
    sid = request.sid
    user_id_str = None
    
    # 查找用户ID
    for uid, conn_data in user_connections.items():
        if conn_data.get('sid') == sid:
            user_id_str = uid
            break
    
    if not user_id_str:
        emit('error', {'message': 'User not identified'})
        return
    
    content = data.get('content')
    if not content:
        emit('error', {'message': 'No message content'})
        return
    
    current_time = datetime.datetime.now().isoformat()
    
    # 添加消息到危险对话记录
    if user_id_str in dangerous_chats:
        dangerous_chats[user_id_str]['messages'].append({
            'role': 'user',
            'content': content,
            'time': current_time
        })
        
        # 保存用户消息到数据库
        try:
            chat_id = dangerous_chats[user_id_str].get('chat_id')
            if chat_id:
                message_manager.add_message(
                    chat_id=chat_id,
                    message_type="text",
                    content=content,
                    sender="user"
                )
        except Exception as e:
            logging.error(f"保存用户危险对话消息失败: {str(e)}")
        
        # 查找处理该用户的管理员
        admin_id = dangerous_chats[user_id_str].get('admin_id')
        
        # 如果有管理员在处理，发送消息给管理员
        if admin_id and admin_id in active_admins:
            socketio.emit('new_message', {
                'userId': user_id_str,
                'role': 'user',
                'content': content,
                'time': current_time
            }, room='admin_room')
        else:
            # 没有管理员处理，向所有管理员发送提醒
            socketio.emit('dangerous_chat_alert', {
                'user': {
                    'userId': user_id_str,
                    'username': user_connections[user_id_str]['username'],
                    'lastMessage': content
                }
            }, room='admin_room')
    else:
        # 创建新的危险对话记录
        # 获取用户当前的chat_id，如果没有则创建新的chat - 统一使用字符串类型
        current_chat_id = user_current_chats.get(user_id_str)
        if not current_chat_id:
            # 为用户创建新的危险对话
            current_chat_id = chat_manager.create_chat(int(user_id_str), "危险对话", "dangerous")
            user_current_chats[user_id_str] = current_chat_id
        else:
            # 更新现有对话为危险类型
            chat_manager.update_chat(current_chat_id, {"type": "dangerous"})
        
        dangerous_chats[user_id_str] = {
            'username': user_connections[user_id_str]['username'],
            'chat_id': current_chat_id,  # 添加chat_id
            'messages': [{
                'role': 'user',
                'content': content,
                'time': current_time
            }],
            'is_active': True,
            'admin_id': None
        }
        
        # 保存用户消息到数据库
        try:
            message_manager.add_message(
                chat_id=current_chat_id,
                message_type="text",
                content=content,
                sender="user"
            )
        except Exception as e:
            logging.error(f"保存WebSocket用户危险消息失败: {str(e)}")
        
        # 通知所有管理员有新的危险对话
        socketio.emit('dangerous_chat_alert', {
            'user': {
                'userId': user_id_str,
                'username': user_connections[user_id_str]['username'],
                'lastMessage': content
            }
        }, room='admin_room')

if __name__ == '__main__':
    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'
    
    # 初始化情感分析模型
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        classifier = EmotionClassifier(
            model_path=os.path.join(current_dir, "emotion_model"), 
            slang_file=os.path.join(current_dir, "slang_map.csv")
        )
        logging.info("✅ 情感分析模型初始化成功")
    except Exception as e:
        logging.error(f"❌ 情感分析模型初始化失败: {str(e)}")
        # 创建一个简单的假分类器用于测试
        class DummyClassifier:
            def predict(self, text):
                return ("normal", [0.1])  # 默认返回安全级别
        classifier = DummyClassifier()
        logging.warning("⚠️ 使用虚拟分类器，危险检测功能不可用")
    
    # 通过SocketIO启动应用
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, log_output=True)
