from datetime import datetime

class MsgsStructure:
    text = ""
    senders_name = ""
    senders_time = datetime
    
    def __init__(self, text: str, senders_name: str, senders_time: datetime = None):
        self.text = text
        self.senders_name = senders_name
        if senders_time == None:
            self.senders_time = datetime.utcnow()
        else:
            self.senders_time = senders_time

    def Get_msg(self, enable_time: bool):
        if enable_time == True:
            stringMsg = f">>> {self.senders_name} {self.senders_time} >>> {self.text}"
        else:
            stringMsg = f">>> {self.senders_name} >>> {self.text}"
        return stringMsg