# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()  # 必须在所有 import 之前

import core  # 确保导入所有处理器

from core.handlers.InitHandler import InitHandler
from core.handlers.socket.AdminSocketHandler import AdminSocketHandler
from core.handlers.socket.UserSocketHandler import UserSocketHandler
from core.handlers.socket.ConnectionSocketHandler import ConnectionSocketHandler
from core.states.SocketState import SocketState

app = InitHandler.initAppAndServices()

SocketState.socketio.run(app, host='0.0.0.0', port=5000, debug=True)