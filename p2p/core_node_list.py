import threading

class CoreNodeList:
    def __init__(self):
        self.lock = threading.Lock()
        self.list = set()

    def add(self, peer):
        """
        Coreノードをリストに追加する
        :param peer: 追加するCoreノード
        :return:
        """
        with self.lock:
            print('Adding peer: ', peer)
            self.list.add((peer))
            print('Current Core List: ', self.list)

    def remove(self, peer):
        """
        離脱したと判断されるCoreノードをリストから削除する
        :param peer: 削除するCoreノード
        :return:
        """
        with self.lock:
            if peer in self.list:
                print('Removing peer: ', peer)
                self.list.remove(peer)
                print('Current Core List: ', self.list)

    def override(self, new_list):
        """
        複数のpeerの接続状況確認を行なった後で一括での上書き処理をしたいような場合はこちら
        :param new_list: 上書きするCoreノードリスト
        :return:
        """
        with self.lock:
            print('core node list will be going to overwrite')
            self.list = new_list
            print('Current Core List: ', self.list)

    def get_list(self):
        """
        現在接続状態にあるPeerの一覧を返却する
        """
        return self.list