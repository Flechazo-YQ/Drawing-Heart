# -*- coding: utf-8 -*-
import core  # 确保导入所有处理器

from core.handlers.InitHandler import InitHandler
from core.states.SocketState import SocketState

app = InitHandler.initAppAndServices()

SocketState.socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
