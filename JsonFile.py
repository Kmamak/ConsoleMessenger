import ujson as json
from pathlib import Path

class JsonClass:
    msgs_path = Path.cwd() / "Data" / "messages.json"
    config_path = Path.cwd() / "Data" / "config.json"

    def Deserialize(self, name_file="messages.json"):
        try:
            if name_file == "messages.json":
                msgs = json.load(self.msgs_path.open("r"))
            elif name_file == "config.json":
                msgs = json.load(self.config_path.open("r"))
            else:
                raise ValueError()
        except Exception as e:
            print(f"Json file \"{name_file}\" not found or corrupted.")
            print(e)
            return

        return msgs

    def Serialize_msgs(self, dictionary: dict):
        data = self.Deserialize()
        data["Messages"].append(dictionary)

        with open(self.msgs_path, 'w') as file:
            json.dump(data, file, default = str, indent = 4)