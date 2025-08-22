import logging, time

from core.states.SocketState import SocketState

from typing import Any

class SocketQueueHandler:
    
    @staticmethod
    def socketioBackgroundThread():
        logging.info("✅ Socket.IO后台线程已启动")

        while(True):
            try:
                task = SocketState.socketioTaskQueue.get()
                event = task.get("event")
                data = task.get("data")
                config = task.get("config", {})

                if (event and data):
                    SocketState.socketio.emit(event, data, **config)

                SocketState.socketioTaskQueue.task_done()
            except Exception as e:
                logging.error(f"❌ Socket.IO后台线程错误: { str(e) }")
                time.sleep(1)

    @staticmethod
    def queueEmit(event: str, data: Any, room: str | None = None, sid: str | None = None):
        try:
            config = {}
            config["room"] = room if (room) else sid if (sid) else None

            task = {
                "event": event,
                "data": data,
                "config": config
            }

            SocketState.socketioTaskQueue.put(task)
        except Exception as e:
            logging.error(f"❌ 放入Emit任务到队列时失败: { str(e) }")