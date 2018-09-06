from concurrent.futures import ThreadPoolExecutor
from message_manager import MessageManager
import socket

PING_INTERVAL = 180  # 30分


class ConnectionManager:
    def __init__(self, host, my_port):
        self.host = host
        self.port = my_port
        self.core_node_set = set()
        self.__add_peer((host, my_port))
        self.mm = MessageManager.MessageManager()

    # 待受を開始する際に呼び出される（ServerCore向け
    def start(self):
        return

    # ユーザーが指定した既知のCoreノードへの接続（ServerCore向け
    def join_network(self):
        return

    # 指定されたノードに対してメッセージを送る
    def send_msg(self):
        return

    # Coreノードリストに登録されている全てのノードに対して
    # 同じメッセージをブロードキャストする
    def send_msg_to_all_peer(self):
        return

    # 終了前の処理としてソケットを閉じる（ServerCore向け
    def connection_close(self):
        return

    # 受信したメッセージを確認して、内容に応じた処理をする
    def __handle_message(self, params):

        soc, addr, data_sum = params

        while True:
            data = soc.recv(1024)
            data_sum = data_sum + data.decode('utf-8')

            if not data:
                break

        if not data_sum:
            return

        result, reason, cmd, peer_port, payload = self.mm.parse(data_sum)
        print(result, reason, cmd, peer_port, payload)
        status = (result, reason)

    # 新たに接続されたCoreノードをリストに追加する
    def __add_peer(self, peer):
        print('Adding peer: ', peer)
        self.core_node_set.add(peer)

    # 離脱したCoreノードをリストから削除する
    def __remove_peer(self, peer):
        if peer in self.core_node_set:
            print('Removing peer: ', peer)
            self.core_node_set.remove(peer)
            print('Current Core list: ', self.core_node_set)

    # 接続されているCoreノード全ての接続状況確認を行う
    def __check_peers_connection(self):
        return

    def __wait_for_access(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(0)

        executor = ThreadPoolExecutor(max_workers=10)

        while True:

            print('Waiting for connection...')
            soc, addr = self.socket.accept()
            print('Connected by .. ', addr)
            data_sum = ''

            params = (soc, addr, data_sum)
            executor.submit(self.__handle_message, params)
