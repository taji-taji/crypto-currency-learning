from concurrent.futures import ThreadPoolExecutor
from .message_manager import (
    MessageManager,
    MSG_ADD,
    MSG_CORE_LIST,
    MSG_REMOVE,
    MSG_PING,
    MSG_REQUEST_CORE_LIST,

    ERR_PROTOCOL_UNMATCH,
    ERR_VERSION_UNMATCH,
    OK_WITH_PAYLOAD,
    OK_WITHOUT_PAYLOAD
)
import pickle
import socket
import threading

PING_INTERVAL = 180  # 30分


class ConnectionManager:
    def __init__(self, host, my_port):
        self.host = host
        self.port = my_port
        self.core_node_set = set()
        self.__add_peer((host, my_port))
        self.mm = MessageManager()

    # 待受を開始する際に呼び出される（ServerCore向け
    def start(self):
        return

    # ユーザーが指定した既知のCoreノードへの接続（ServerCore向け
    def join_network(self):
        return

    # 指定されたノードに対してメッセージを送る
    def send_msg(self, peer, msg):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer))
            s.sendall(msg.encode('utf8'))
            s.close()
        except OSError:
            print('Connection failed for peer: ', peer)
            self.__remove_peer(peer)

    # Coreノードリストに登録されている全てのノードに対して
    # 同じメッセージをブロードキャストする
    def send_msg_to_all_peer(self, msg):
        print('send_msg_to_all_peer was called!')
        for peer in self.core_node_set:
            if peer != (self.host, self.port):
                print('message will sent to ... ', peer)
                self.send_msg(peer, msg)

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

        if status == ('error', ERR_PROTOCOL_UNMATCH):
            print('Error: Protocol name is not matched')
            return
        elif status == ('error', ERR_VERSION_UNMATCH):
            print('Error: Protocol version is not matched')
            return
        elif status == ('ok', OK_WITHOUT_PAYLOAD):
            if cmd == MSG_ADD:
                print('Add node request was received!!')
                self.__add_peer((addr[0], peer_port))
                if (addr[0], peer_port) == (self.host, self.port):
                    return
                else:
                    cl = pickle.dumps(self.core_node_set, 0).decode()
                    msg = self.mm.build(MSG_CORE_LIST, self.port, cl)
                    self.send_msg_to_all_peer(msg)
            elif cmd == MSG_REMOVE:
                print('Remove request was received!! from ', addr[0], peer_port)
                self.__remove_peer((addr[0], peer_port))
                cl = pickle.dumps(self.core_node_set, 0).decode()
                msg = self.mm.build(MSG_CORE_LIST, self.port, cl)
                self.send_msg_to_all_peer(msg)
            elif cmd == MSG_PING:
                return
            elif cmd == MSG_REQUEST_CORE_LIST:
                print('List for Core nodes was requested!!')
                cl = pickle.dumps(self.core_node_set, 0).decode()
                msg = self.mm.build(MSG_CORE_LIST, self.port, cl)
                self.send_msg((addr[0], peer_port), msg)
            else:
                print('received unknown command ', cmd)
                return
        elif status == ('ok', OK_WITH_PAYLOAD):
            if cmd == MSG_CORE_LIST:
                # TODO: 受信したリストをただ上書きしてしまうのは
                # 本来セキュリティ的にはよろしくない。
                # 信頼できるノードの鍵とかをセットしとく必要があるかも
                print('Refresh the core node list...')
                new_core_set = pickle.loads(payload.encode('utf8'))
                print('latest code node list: ', new_core_set)
                self.core_node_set = new_core_set
            else:
                print('received unknown command ', cmd)
                return
        else:
            print('Unexpected stauts: ', status)

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
        """
        接続されているCoreノードすべての接続状況確認を行う。
        クラス外からは使用されない想定
        この処理は定期的に実行される
        """
        print('check_peers_to_connection was called!')
        changed = False
        dead_c_node_set = list(filter(lambda p: not self.__is_alive(p), self.core_node_set))

        if dead_c_node_set:
            changed = True
            print('Removing ', dead_c_node_set)
            self.core_node_set = self.core_node_set - set(dead_c_node_set)

        print('current core node list: ', self.core_node_set)

        # 変更があった時だけブロードキャストで伝える
        if changed:
            cl = pickle.dumps(self.core_node_set, 0).decode()
            msg = self.mm.build(MSG_CORE_LIST, self.port, cl)
            self.send_msg_to_all_peer(msg)

        self.ping_timer = threading.Timer(PING_INTERVAL, self.__check_peers_connection)
        self.ping_timer.start()

    def __is_alive(self, peer):
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
