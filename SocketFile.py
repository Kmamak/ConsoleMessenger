from JsonFile import JsonClass

import socket

class SocketClass(socket.socket):
    def __init__(self):
        super(SocketClass, self).__init__(
            socket.AF_INET, socket.SOCK_STREAM,
        )

        self.jsonClass = JsonClass()
        self.config = self.jsonClass.Deserialize("config.json")
        # self.ip = dictionary["ip"]
        # self.port = dictionary["port"]
        # self.name = dictionary["name"]
        # self.enable_time = dictionary["enable time"]
        # self.save_history = dictionary["save history"]

        self.HEADERSIZE = 7
        self.MAXTEXTSIZE = 10000

    def ServerBind(self):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((self.config["ip"], self.config["port"]))
        print("These are the ports that can be used for internet connection: "+
            ", ".join(socket.gethostbyname_ex(socket.gethostname())[2])+
            ".")
        self.listen()
    
    def ClientConnected(self):
        self.connect((self.config["ip"], self.config["port"]))

    def Recv_data(self, msg_len: int, connection=None):
        try:
            if connection == None:
                data = self.recv(msg_len)
            else:
                data = connection.recv(msg_len)
        except ConnectionResetError as e:
            print(e)
            return False

        if not len(data):
            # if data is not received break
            print("<<< Data is not received!")
            return False
        return data.decode()

    def Recv_msg_header(self, connection=None):
        try:
            mode = self.Recv_data(self.HEADERSIZE, connection)
            if mode == False:
                return False, False
        except Exception as e:
            print(e)
            return False, False

        try:
            msg_header = self.Recv_data(self.HEADERSIZE, connection)
            if msg_header == False:
                return False, False
        except Exception as e:
            print(e)
            return False, False
        return int(mode), int(msg_header)

    def Recv_msg_without_parametrs(self, connection=None):
        try:
            mode, msg_len = self.Recv_msg_header(connection)
            if mode == False and msg_len == False:
                return False, False
        except Exception as e:
            print(e)
            return False, False

        try:
            msg = self.Recv_data(msg_len, connection)
            if mode == False:
                return False, False
        except Exception as e:
            print(e)
            return False, False
        return mode, msg

    # These functions need to be redefined.
    def HandlerData(self, connection, address):
        raise NotImplementedError()
    
    def SendMessage(self, msg, connection):
        raise NotImplementedError()

    def MainLoop(self):
        raise NotImplementedError()
    
    def ClientDisconected(self, connection, address):
        raise NotImplementedError()