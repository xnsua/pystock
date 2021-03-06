import queue
import threading

from common.data_structures.object_cabinet import ObjectPool
from project_config.logbook_logger import mylog
from trading.abstract_context import AbstractContext
from trading.account_manager import AccountManager
from trading.base_structure.trade_constants import TradeId, MsgSetRealTimeStocks, MsgQuitLoop
from trading.base_structure.trade_message import TradeMessage


class TradeContext(AbstractContext):
    def __init__(self, queue_dict):
        super().__init__()
        self.account = AccountManager()

        self.queue_dict = queue_dict
        self.queue_cabinet = ObjectPool(queue.Queue, None)
        self.thread_local = threading.local()
        self.thread_local.name = None

    def post_msg(self, dest, operation):
        assert self.thread_local.name
        dest_queue = self.queue_dict[dest]
        msg = TradeMessage(self.thread_local.name, operation, result_queue=None)
        mylog.notice(dest_queue)
        mylog.notice(operation)
        dest_queue.put(msg)

    def send_msg(self, dest, operation):
        assert self.thread_local.name
        dest_queue = self.queue_dict[dest]
        with self.queue_cabinet.use_and_return() as result_queue:
            msg = TradeMessage(self.thread_local.name, operation, result_queue=result_queue)
            dest_queue.put(msg)
            result = result_queue.get()
            msg.result = result
        return result

    def send_oper(self, operation):
        return self.send_msg(TradeId.trade_manager, operation)

    @property
    def current_thread_queue(self):
        assert self.thread_local.name
        return self.queue_dict[self.thread_local.name]

    def set_realtime_stocks(self, stocks):
        self.send_msg(TradeId.data_server, MsgSetRealTimeStocks(stocks))

    def quit_all(self):
        for key in self.queue_dict:
            self.post_msg(key, MsgQuitLoop())

    def _is_model_queue(self, queue_name):
        return queue_name != TradeId.data_server and queue_name != TradeId.trade_manager
