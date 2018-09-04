STATE_INIT = 0
STATE_STANDBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3


class ServerCore:
    def __init__(self):
        self.server_state = STATE_INIT
        print('Initializing server....')

    def start(self):
        self.server_state = STATE_STANDBY

    def join_network(self):
        self.server_state = STATE_CONNECTED_TO_NETWORK

    def shutdown(self):
        self.server_state = STATE_SHUTTING_DOWN

    def get_my_current_state(self):
        return self.server_state
