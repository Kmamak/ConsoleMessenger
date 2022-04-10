from SocketFile import SocketClass
from Crypt import Crypt
from JsonFile import JsonClass

from MsgsStructure import MsgsStructure
from Mods_of_text import Mods_of_text

from threading import Thread, RLock
from datetime import datetime
from time import sleep


class Client(SocketClass):
    locker = RLock()
    stopReading = True
    string_public_keys = ""

    def __init__(self):
        super(Client, self).__init__()
        try:
            self.crypt = Crypt()

            self.ClientConnected()
            self.stopReading = False
        except  ConnectionRefusedError as e:
            print("<<< ConnectionRefusedError: server not found!")
            print(e)
            self.stopReading = True
            return

    def HandlerData(self, connection = None, address = None):
        """ Получает и записывает data в консоль """
        try:
            while not self.stopReading:
                try:
                    mode, msg_header = self.Recv_msg_header()
                    if mode == False and msg_header == False:
                        self.ClientDisconected()
                        return

                    if mode == Mods_of_text.max_idSymbol:
                        self.crypt.GenerateKeys(msg_header)
                        msg_with_public_key = f"{self.crypt.public_key[0]},{self.crypt.public_key[1]}"
                        self.send((f"{Mods_of_text.public_key:<{self.HEADERSIZE}}"+
                            f"{len(msg_with_public_key):<{self.HEADERSIZE}}"+
                            msg_with_public_key).encode("utf-8"))
                    
                    elif mode == Mods_of_text.public_key:
                        self.locker.acquire()
                        data = self.Recv_data(msg_header)
                        if data == False:
                            self.ClientDisconected()
                            return

                        self.string_public_keys = data
                        self.locker.release()

                    elif mode == Mods_of_text.text:
                        data = self.Recv_data(msg_header)
                        if data == False:
                            self.ClientDisconected()
                            return

                        data = self.crypt.Decryption(data)

                        data = data[data.index("(")+1:]
                        senders_time = data[:data.index(")")]
                        data = data[data.index(")")+1:]
                        senders_name = data[:data.index(":")]
                        text = data[data.index(":")+1:]

                        msg = MsgsStructure(text, senders_name, senders_time)
                        stringMsg = msg.Get_msg(self.config["enable time"])
                        print(stringMsg)

                        self.jsonClass.Serialize_msgs(msg.__dict__)
                except Exception as e:
                    print(e)
                    print("\n<<< Error in HandlerData in class client!")
                    self.ClientDisconected()
                    return

        except ConnectionResetError:
            print("\n<<< ConnectionResetError: server not found!")
            self.ClientDisconected()
            return
        except ConnectionAbortedError:
            print("<<< The program is completed!")
            self.ClientDisconected()
            return
        except AttributeError:
            print("<<< AttributeError: server not found!")
            self.ClientDisconected()
            return

    def SendMessage(self, msg: str, connection = None):
        msg = msg.strip()
        if (msg != ""):
            # send_msg = "((0))(1):".format(datetime.utcnow(), self.config["name"])+msg
            send_msg = "("+str(datetime.utcnow())+")"+self.config["name"]+":"+msg

            if len(send_msg) < self.MAXTEXTSIZE:
                max_id = self.crypt.FindMaxID(send_msg)
                self.send((f"{Mods_of_text.max_idSymbol:<{self.HEADERSIZE}}"+
                    f"{max_id:<{self.HEADERSIZE}}").encode("utf-8"))

                try:
                    while True:
                        sleep(0.025)
                        if self.string_public_keys:
                            break

                    send_msgs = list()
                    public_keys_str = self.string_public_keys.split(";")
                    for i in public_keys_str:
                        id, public_key1, public_key2 = i.split(",")
                        send_msgs.append(
                            f"{id:<{self.HEADERSIZE}}"+
                            self.crypt.Encryption(send_msg, (public_key1, public_key2)))
                except Exception as e:
                    print(e)
                    print("\n<<< Error in SendMessage in class client!")
                    self.ClientDisconected()
                    return

                all_stringMsg = ";".join(send_msgs)
                self.send((f"{Mods_of_text.text:<{self.HEADERSIZE}}"+
                    (f"{len(all_stringMsg):<{self.HEADERSIZE}}"+
                    (all_stringMsg)
                    )).encode("utf-8"))
                
                if msg.lower() == "!ls":
                    # leave server
                    self.ClientDisconected()
                    return
            else:
                print(f"<<< You can not send message that length more {self.MAXTEXTSIZE-1} letters!")
            self.string_public_keys = ""

    def MainLoop(self):
        try:
            readData_thread = Thread(target=self.HandlerData)
            readData_thread.start()

            steps = 10
            for i in range(steps+1):
                sleep(0.05)
                print(f"Loading {int(100 / steps * i)}%...", end="\r")
            print("The program is initialized\n")

            try:
                while not self.stopReading:

                    if self.config["enable time"] == True:
                        stringMsg = input(f">>> You {datetime.utcnow()} >>> ")
                    else:
                        stringMsg = input(f">>> You >>> ")

                    msg = MsgsStructure(stringMsg, self.config["name"])
                    self.SendMessage(stringMsg)
                    self.jsonClass.Serialize_msgs(msg.__dict__)
            except ConnectionResetError as e:
                print(e)
                self.ClientDisconected()
            else:
                lastCheck = input("<<< Click ENTER to end the program >>> ")

        except AttributeError as e:
            print("<<< AttributeError: server not found!")
            print(e)
            self.ClientDisconected()
            return
        
    def ClientDisconected(self, connection = None, address = None):
        self.stopReading = True
        self.close()

if __name__ == "__main__":
    try:
        client = Client()
        if client.stopReading == False:
            client.MainLoop()
    except Exception as e:
        print(e)