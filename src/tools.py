import os
from logging import config
from logging import getLogger

import yaml

from . import errors


class Singleton:
    def __new__(cls, *args, **kwargs):
        # Ensures that each class will only be instantiated once, they will only run the __init__once method once
        if not hasattr(cls, "ins"):
            ins = super(__class__, cls).__new__(cls)
            setattr(cls, "ins", ins)

            # Fill data for __dict__ in this step, if you use __init__ directly, it will run multiple times
            getattr(
                ins,
                "_" + cls.__name__ + "__init__once"
            )(*args, **kwargs)

        return getattr(cls, "ins")


class Config(Singleton):
    def __init__once(self):
        path = os.path.join(".", "conf", "config.yml")

        if not os.path.exists(path):
            err = "config file is not found, please check conf directory."
            raise errors.ConfigError(err)

        with open(path, "r", encoding="utf-8") as f:
            self._conf = yaml.safe_load(f)

            # Convert {name: port} to {port: name} store
            self._conf["net"] = {ip: name for name, ip in self.net.items()}

    @property
    def net(self):
        return self._conf["net"]

    @property
    def serve(self):
        return self._conf["serve"]

    @property
    def logger(self):
        return self._conf["logger"]


class Logger(Singleton):
    def __init__once(self):
        self.conf = Config().logger
        self.__parse()
        self.__mkdir()
        self.__load_config()

        self.file = getLogger("file")
        self.screen = getLogger("screen")
        self.default = getLogger("default")

    def __mkdir(self):
        dir_name = self.conf["dir"]
        file_name = self.conf["file"]

        dir_path = os.path.join(os.path.dirname("."), dir_name)

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        self.conf["handlers"]["file"]["filename"] = os.path.join(
            dir_path, file_name)

    def __parse(self):
        max_bytes = self.conf["handlers"]["file"]["maxBytes"]

        # YAML gets the str type and calculates it to get int
        self.conf["handlers"]["file"]["maxBytes"] = eval(max_bytes)

    def __load_config(self):
        config.dictConfig(self.conf)
