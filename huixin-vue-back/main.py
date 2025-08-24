# -*- coding: utf-8 -*-
import base64
import datetime
import threading
import jwt
from flask import render_template, jsonify, send_from_directory, Flask, request, json
from flask_cors import CORS  # 添加CORS支持
from flask_socketio import SocketIO, emit, join_room, leave_room  # 添加SocketIO支持

import requests
from torchvision import transforms
import hashlib
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import os
from flask import Response, stream_with_context
from openai import OpenAI
from 封装 import EmotionClassifier
import logging
import sys
from datetime import timedelta
import secrets
from mongodb_config import init_mongodb
from bson import ObjectId

# 初始化MongoDB（确保在应用启动时就完成初始化）
try:
    init_mongodb()
    logging.info("MongoDB初始化成功")
except Exception as e:
    logging.error(f"MongoDB初始化失败: {str(e)}")
    raise e

# 导入已初始化的管理器
from mongodb_config import user_manager, chat_manager, message_manager

# 注册字体 - 注释掉避免文件不存在错误
# pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))  # 确保路径正确，或使用系统字体路径
app = Flask(__name__)
CORS(app)  # 启用CORS
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
        user_id = payload['user_id']
        return user_id
    except jwt.ExpiredSignatureError:
        return None  # 令牌已过期
    except jwt.InvalidTokenError:
        return None  # 无效的令牌


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    try:
        with open('templates/Home.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
            # 返回HTML内容作为响应
        return Response(html_content, mimetype='text/html')
    except FileNotFoundError:
        # 如果文件不存在，返回404错误
        return 'File not found', 404


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username_or_email = data.get('username')  # 前端传来的可能是用户名或邮箱
        password = data.get('password')
        
        try:
            # 先尝试按邮箱查找
            user = user_manager.get_user_by_email(username_or_email)
            
            # 如果按邮箱没找到，尝试按用户名查找
            if not user:
                # 由于MongoDB中没有直接按用户名查找的方法，需要扩展
                from mongodb_config import mongodb
                user = mongodb.users.find_one({
                    "$or": [
                        {"username": username_or_email},
                        {"email": username_or_email}
                    ],
                    "is_active": True
                })
            
            if user and user['password'] == sha256_hash(password):
                token = generate_token([str(user['_id']), user['username']])
                return jsonify({
                    'code': 0,
                    'message': '登录成功',
                    'data': {
                        'token': token,
                        'user': {
                            'id': str(user['_id']),
                            'username': user['username'],
                            'email': user['email'],
                            'avatar': user.get('avatar', ''),
                            'chance': user.get('chance', 10)
                        }
                    }
                }), 200
            else:
                return jsonify({
                    'code': 1,
                    'message': '用户名/邮箱或密码错误'
                }), 401
        except Exception as e:
            logging.error(f"登录错误: {str(e)}")
            return jsonify({
                'code': 1,
                'message': '登录失败，请稍后重试'
            }), 500
    return render_template('login.html')





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            gender = data.get('gender')

            if not all([username, password, email, gender]):
                return jsonify({
                    'code': 1,
                    'message': '请填写所有必需的字段'
                }), 400

            # 检查邮箱是否已存在
            existing_user = user_manager.get_user_by_email(email)
            if existing_user:
                return jsonify({
                    'code': 1,
                    'message': '邮箱已被注册'
                }), 400
            
            # 检查用户名是否已存在
            from mongodb_config import mongodb
            existing_username = mongodb.users.find_one({"username": username, "is_active": True})
            if existing_username:
                return jsonify({
                    'code': 1,
                    'message': '用户名已存在'
                }), 400

            # 创建新用户
            user_id = user_manager.create_user(
                username=username,
                email=email,
                password=sha256_hash(password),
                gender=gender,
                chance=5,
                is_team='false'
            )
            
            return jsonify({
                'code': 0,
                'message': '注册成功'
            }), 200
                
        except Exception as e:
            logging.error(f"注册错误: {str(e)}")
            return jsonify({
                'code': 1,
                'message': '注册失败，请稍后重试'
            }), 500
            
    return render_template('register.html')





@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return render_template('forgot.html')


@app.route('/privacy')
def privacy():
    # 由于前端已经有Vue路由处理/privacy，我们应该返回前端应用
    return render_template('index.html')  # 返回前端入口文件


@app.route('/getusername', methods=['GET'])
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


url = "https://api.siliconflow.cn/v1/chat/completions"
dangerous = 0
current_context = []
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
        
        # 清除全局变量中的上下文
        global current_context
        current_context = []
        
        # 如果用户在危险对话列表中，清除其记录
        if user_id_str in dangerous_chats:
            del dangerous_chats[user_id_str]
            
        # 清除用户的最新图片URL
        if user_id_str in user_latest_images:
            del user_latest_images[user_id_str]
            
        # 清除全局的文本结果
        global text_result
        text_result = ''
        
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
        
        # 设置为当前活跃聊天
        user_current_chats[user_id[0]] = chat_id
        
        # 清除当前上下文，开始新对话
        global current_context
        current_context = []
        
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
        
        # 设置为当前活跃聊天
        user_current_chats[user_id[0]] = chat_id
        
        # 获取最近的消息作为上下文
        recent_messages = message_manager.get_latest_messages(chat_id, 10)
        
        # 更新全局上下文
        global current_context
        current_context = []
        
        for msg in recent_messages:
            if msg['sender'] == 'user':
                current_context.append({
                    "role": "user",
                    "content": msg['content']
                })
            elif msg['sender'] == 'assistant':
                current_context.append({
                    "role": "assistant", 
                    "content": msg['content']
                })
        
        return jsonify({
            'code': 0,
            'message': '对话上下文加载成功',
            'data': {
                'chat': chat,
                'context_loaded': len(current_context)
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
    label, dangerous = classifier.predict(message)
    dangerous = dangerous[0]
    return dangerous


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
    thread = threading.Thread(target=process_message, args=(user_message,))
    thread.start()
    thread.join()  # 等待线程完成
    
    # 获取或创建当前聊天
    current_chat_id = user_current_chats.get(user_id[0])
    if not current_chat_id:
        # 如果没有当前聊天，根据消息危险性创建不同类型的对话
        chat_type = "dangerous" if dangerous > 0.5 else "normal"
        current_chat_id = chat_manager.create_chat(user_id[0], "新对话", chat_type)
        user_current_chats[user_id[0]] = current_chat_id
    
    # 如果检测到危险消息，更新对话类型
    if dangerous > 0.5:
        # 更新现有对话为危险类型
        chat_manager.update_chat(current_chat_id, {"type": "dangerous"})
        
        print('检测到危险消息，需要人工干预:', user_message)
        # 将聊天内容记录到危险对话字典
        user_id_str = str(user_id[0])
        
        if user_id_str not in dangerous_chats:
            # 初始化用户的危险聊天记录
            dangerous_chats[user_id_str] = {
                'username': user_id[1],
                'chat_id': current_chat_id,  # 添加chat_id以便后续消息保存到数据库
                'messages': current_context.copy() + [
                    {"role": "user", "content": user_message}
                ],
                'is_active': True,
                'admin_id': None,
                'last_updated': datetime.datetime.now().isoformat()
            }
        else:
            # 更新现有聊天记录
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
        socketio.emit('dangerous_chat_alert', {
            'user': {
                'userId': user_id_str,
                'username': user_id[1],
                'lastMessage': user_message
            }
        }, room='admin_room')
        
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
        
        # 返回一个固定提示
        return admin_message
    
    # 如果消息不危险，正常处理
    messages = [
        {
            "content": "你现在是一名心理医师，你的名字叫绘心同学，结合下面用户的心理绘图分析结果帮助用户，请用通俗易懂的语言与用户交流，用多轮对话的形式，每次别说太多：" + text_result,
            "role": "system"
        }
    ] + current_context.copy() + [
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
            
            # 更新上下文
            current_context.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_reply}
            ])
            # 保留最多5轮对话（10条消息）
            if len(current_context) > 10:
                current_context[:] = current_context[-10:]
            
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

@app.route('/save', methods=['POST'])
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
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            # 补充缺失的填充
            missing_padding = len(image_data) % 4
            if missing_padding:
                image_data += '=' * (4 - missing_padding)
                
            # 解码 Base64 数据
            image_bytes = base64.b64decode(image_data.encode())
            
            # 生成文件名和保存图片
            file_name = f"drawing_{len(os.listdir(SAVE_DIR)) + 1}.png"
            file_path = os.path.join(SAVE_DIR, file_name)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
                
            # 保存用户最新的图片URL
            user_latest_images[str(user_id[0])] = file_path
            
            # 如果是分析请求，则进行AI分析
            should_analyze = data.get('analyze', False)
            if should_analyze:
                return analyze_image(file_path)
                
            # 否则只返回保存成功的消息
            return jsonify({
                'message': '图像保存成功',
                'file_name': file_name
            }), 200
                
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return jsonify({'message': f'图像处理失败: {str(e)}'}), 400
            
    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({'message': f'保存失败: {str(e)}'}), 500

def analyze_image(file_path):
    """分析图片的函数"""
    try:
        if not os.path.exists(file_path):
            logging.error(f"File not found for analysis: {file_path}")
            return jsonify({'message': '找不到要分析的图片文件'}), 404
            
        client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key="d618ffd5-dd7c-4548-8cde-a82ba550f808"
        )
        
        data_url = image_to_data_url(file_path)
        if not data_url:
            return jsonify({'message': '图片转换失败'}), 500
        
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
                    阶段1：符号特征优先级分类
                    高风险信号标记：
                    人物无五官或躯体残缺 → 潜在身份认同障碍或抑郁倾向。
                    树根缺失/悬浮或严重倾斜 → 缺乏安全感或情绪不稳定。
                    房屋全封闭（无门窗）+ 尖刺状屋顶 → 防御性人格或创伤后应激可能。
                    文化适配调节：
                    若画纸边缘多次被线条穿透 → 在东亚文化中可能暗示压力，而在西方可能关联外向性（需标记此差异）。
                    阶段2：生成心理画像框架
                    核心维度与权重：
                    情绪状态（权重高）：
                    阴云/雨水+重压线条 → 焦虑/抑郁概率↑。
                    明亮太阳+曲线线条 → 情绪稳定概率↑。
                    人际关系模式（权重中）：
                    房屋与人物距离＞画面1/3 → 家庭疏离感假设。
                    树木孤立于角落 → 社会支持薄弱假设。
                    自我认知（权重中）：
                    人物大小异常（如极小） → 自卑或退缩倾向↑。
                    矛盾点与可信度：
                    若房屋细节丰富但人物极其简略 → 可能"重视家庭角色而忽视自我"，标注逻辑一致性矛盾（可信度↓）。
                    最后生成用户的心理画像，判断用户心理状况是否健康和可能潜在的问题，若图片不是房树人相关，请使用温柔和蔼委婉地拒绝并引导用户重新绘画，适量使用语气词。
                    最后输出包含：绘画描述、分析概述、具体分析、用户心理画像。                
                    '''}
                ]
            }]
        )
        
        # 获取分析结果
        analysis_result = response.choices[0].message.content
        
        # 更新全局变量
        global text_result
        text_result = analysis_result
        
        return jsonify({
            'message': '分析完成',
            'analysis': analysis_result
        }), 200
        
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        return jsonify({'message': '分析过程中出现错误', 'error': str(e)}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'code': 1,
                'message': '请提供邮箱地址'
            }), 400
            
        user = user_manager.get_user_by_email(email)
        if not user:
            return jsonify({
                'code': 1,
                'message': '该邮箱未注册'
            }), 404
                
        # 生成重置密码的token
        reset_token = generate_token([str(user['_id']), user['username']])
        
        # TODO: 发送重置密码邮件
        # 这里应该实现发送邮件的功能
        # 为了演示，我们直接返回成功
        
        return jsonify({
            'code': 0,
            'message': '重置密码链接已发送到您的邮箱'
        }), 200
            
    except Exception as e:
        logging.error(f"重置密码错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': '重置密码失败，请稍后重试'
        }), 500

@app.route('/api/update-password', methods=['POST'])
def update_password():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not all([token, new_password]):
            return jsonify({
                'code': 1,
                'message': '请提供所有必需的字段'
            }), 400
            
        # 验证token
        user_id = verify_token(token)
        if not user_id:
            return jsonify({
                'code': 1,
                'message': '无效或过期的重置链接'
            }), 401
            
        # 更新密码
        success = user_manager.update_user(user_id[0], {
            'password': sha256_hash(new_password)
        })
        
        if success:
            return jsonify({
                'code': 0,
                'message': '密码更新成功'
            }), 200
        else:
            return jsonify({
                'code': 1,
                'message': '用户不存在或更新失败'
            }), 404
            
    except Exception as e:
        logging.error(f"更新密码错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': '更新密码失败，请稍后重试'
        }), 500

@app.route('/api/reset-password-direct', methods=['POST'])
def reset_password_direct():
    try:
        data = request.get_json()
        email = data.get('email')
        new_password = data.get('password')
        
        if not all([email, new_password]):
            return jsonify({
                'code': 1,
                'message': '请提供邮箱和新密码'
            }), 400
            
        # 检查邮箱是否存在
        user = user_manager.get_user_by_email(email)
        if not user:
            return jsonify({
                'code': 1,
                'message': '该邮箱未注册'
            }), 404
            
        # 更新密码
        success = user_manager.update_user(str(user['_id']), {
            'password': sha256_hash(new_password)
        })
        
        if success:
            return jsonify({
                'code': 0,
                'message': '密码重置成功'
            }), 200
        else:
            return jsonify({
                'code': 1,
                'message': '密码重置失败'
            }), 500
            
    except Exception as e:
        logging.error(f"重置密码错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': '重置密码失败，请稍后重试'
        }), 500

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
    if not token:
        emit('error', {'message': 'Token is missing'})
        return
    
    user_id = verify_token(token)
    if not user_id:
        emit('error', {'message': 'Invalid token'})
        return
    
    # 保存用户的连接信息
    user_id_str = str(user_id[0])
    user_connections[user_id_str] = {
        'sid': request.sid,
        'username': user_id[1],
        'connected_at': datetime.datetime.now().isoformat()
    }
    
    # 将用户加入以用户ID命名的房间
    join_room(f'user_{user_id_str}')
    
    # 发送连接成功响应
    emit('connect_response', {'status': 'success', 'message': 'Connection successful'})
    
    # 检查是否有未处理的消息需要发送给用户
    if user_id_str in dangerous_chats:
        # 获取最近的管理员回复，排除系统自动生成的提示消息
        admin_messages = [
            msg for msg in dangerous_chats[user_id_str]['messages'] 
            if msg.get('role') == 'admin' and (
                # 如果有messageId且不是系统风险提示，或者没有is_system标记，则包含
                (msg.get('messageId') != 'system_risk_alert') or 
                not msg.get('is_system', False)
            )
        ]
        
        if admin_messages:
            # 发送最近的几条管理员消息
            recent_messages = admin_messages[-3:] if len(admin_messages) > 3 else admin_messages
            for msg in recent_messages:
                socketio.emit('admin_reply', {
                    'role': 'admin',
                    'content': msg.get('content'),
                    'time': msg.get('time', datetime.datetime.now().isoformat()),
                    'messageId': msg.get('messageId')  # 添加消息ID
                }, room=f'user_{user_id_str}')
    
    print(f'User {user_id[1]} connected with SID: {request.sid}')

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
    
    user_id = data.get('userId')
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
        # 获取用户当前的chat_id，如果没有则创建新的chat
        current_chat_id = user_current_chats.get(int(user_id_str))
        if not current_chat_id:
            # 为用户创建新的危险对话
            current_chat_id = chat_manager.create_chat(int(user_id_str), "危险对话", "dangerous")
            user_current_chats[int(user_id_str)] = current_chat_id
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
    classifier = EmotionClassifier(
        model_path=os.path.join(current_dir, "emotion_model"), 
        slang_file=os.path.join(current_dir, "slang_map.csv")
    )
    
    # 通过SocketIO启动应用
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, log_output=True)
