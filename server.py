from SocketFile import SocketClass

from Mods_of_text import Mods_of_text

from threading import Thread, RLock
from time import sleep


class Server(SocketClass):
    locker = RLock()
    clientsDict = dict()
    id_last_client = 0

    messagesList = list()
    sender = None

    def __init__(self):
        super(Server, self).__init__()
        try:
            self.ServerBind()
        except OSError:
            print(f"<<< OSError ([WinError 10022]): this port ({self.port}) is busy!")
            return

    def HandlerData(self, connection, address):
        try:
            while True:
                mode, msg_header = self.Recv_msg_header(connection)
                if mode == False and msg_header == False:
                    self.ClientDisconected(connection, address)
                    break
                
                if mode == Mods_of_text.max_idSymbol:
                    self.SendMessage_for_all_clients((f"{mode:<{self.HEADERSIZE}}"+
                        f"{msg_header:<{self.HEADERSIZE}}"), connection)
                    id_and_public_keys = []
                    while True:
                        sleep(0.025)
                        if len(self.messagesList) == len(self.clientsDict)-1:
                            for (client_id, data) in self.messagesList:
                                id_and_public_keys.append(f"{client_id},{data}")
                            text = ";".join(id_and_public_keys)
                            msg = (f"{Mods_of_text.public_key:<{self.HEADERSIZE}}"+
                                f"{len(text):<{self.HEADERSIZE}}"+text)
                            self.messagesList = list()

                            self.SendMessage(msg, connection)
                            break

                elif mode == Mods_of_text.public_key:
                    data = self.Recv_data(int(msg_header), connection)
                    for i in range(len(self.clientsDict)):
                        if connection == self.clientsDict[i]:
                            client_id = self.clientsDict[i]
                            
                            self.locker.acquire()
                            self.messagesList.append((i, data))
                            self.locker.release()
                            break

                elif mode == Mods_of_text.text:
                    data = self.Recv_data(int(msg_header), connection)
                    data = data.split(";")
                    for i in data:
                        id_specific_client, text_for_specific_client = i[:self.HEADERSIZE], i[self.HEADERSIZE:]
                        self.SendMessage(
                            (f"{mode:<{self.HEADERSIZE}}"+
                                f"{len(text_for_specific_client):<{self.HEADERSIZE}}"+
                                text_for_specific_client), 
                            self.clientsDict[int(id_specific_client)])
        except:
            # Occurs when the socket is closed.
            self.ClientDisconected(connection, address)
    
    def SendMessage_for_all_clients(self, msg: str, sendersConnection):
        for i in self.clientsDict.keys():
            if sendersConnection != self.clientsDict[i]:
                self.SendMessage(msg, self.clientsDict[i])
    
    def SendMessage(self, msg: str, connection):
        connection.send(msg.encode("utf-8"))

    def MainLoop(self):
        while True:
            connection, address = self.accept()
            print(f"Connected: (ip = {address[0]}, id = {address[1]})")

            self.clientsDict[self.id_last_client] = connection
            self.id_last_client += 1

            handler_thread = Thread(target=self.HandlerData, args=(connection, address,), daemon=True)
            handler_thread.start()

    def ClientDisconected(self, connection, address):
        for i in list(self.clientsDict.keys()):
            if connection == self.clientsDict[i]:
                self.clientsDict.pop(i)
                print(f"{address[0]} : {address[1]} has disconnected")
                connection.close()

if __name__ == "__main__":
    try:
        server = Server()
        server.MainLoop()
    except Exception as e:
        print(e)