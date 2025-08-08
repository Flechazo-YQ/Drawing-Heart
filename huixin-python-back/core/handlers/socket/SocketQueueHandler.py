import logging, time

from regex import E

from core.states.SocketState import SocketState

class SocketQueueHandler:
    
    @staticmethod
    def socketioBackgroundThread():
        logging.info("Socket.IO后台线程已启动")

        while(True):
            try:
                task = SocketState.socketioTaskQueue.get()
                event = task.get('event')
                data = task.get('data')

                if (event and data):
                    SocketState.socketio.emit(event, data)
                    logging.info(f"后台任务: 已发送Socket.IO事件 '{ event }'")

                SocketState.socketioTaskQueue.task_done()
            except Exception as e:
                logging.error(f"Socket.IO后台线程错误: { str(e) }")
                time.sleep(1)

    @staticmethod
    def queueEmit(event: str, data: dict, room: str | None = None, sid: str | None = None):
        try:
            task = {
                'event': event,
                'data': data,
                'room': room,
                'sid': sid
            }

            SocketState.socketioTaskQueue.put(task)
        except Exception as e:
            logging.error(f"❌ 放入Emit任务到队列时失败: { str(e) }")