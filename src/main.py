import os
from concurrent.futures import ThreadPoolExecutor

from . import platform
from . import server
from . import tools

logger = tools.Logger()


class Manager:
    def __init__(self):
        self.conf = tools.Config()
        self.pool = ThreadPoolExecutor()

    def entry(self):
        port_name_dict = self.check_port()

        if port_name_dict:
            # If a program does not start successfully, it will try to start every three seconds
            self.fover_server(port_name_dict)

    def check_port(self):
        # returns unstarted services

        if os.name == "nt":
            result_dict: dict[int, str] = platform.NT.get_listen_port()
        else:
            result_dict: dict[int, str] = platform.POSIX.get_listen_port()

        # Find the intersection, if the result intersects with the configured port:name, it proves that the service has been started
        is_exists_serve_port = set.intersection(
            set(result_dict.keys()),
            set(self.conf.net.keys())
        )

        # Find the difference set, if the configured port:name is different from the result, it proves that the configured service item is not started
        not_exists_serve_port = set.difference(
            set(self.conf.net.keys()),
            set(result_dict.keys())
        )

        for port in is_exists_serve_port:
            # process name:
            # - posix: python
            # - nt: python3.exe

            name = result_dict[port].lower()

            if name.find("python") == -1:
                msg = "[{}] port is occupied, the program name is [{}]".format(
                    port, name)

                logger.default.warning(msg)

        for port in not_exists_serve_port:
            name = self.conf.net[port].split("_")[0]
            msg = "[{}] port not listen, starting [{}] emulator".format(
                port, name)

            logger.default.error(msg)

        return {port: self.conf.net[port] for port in not_exists_serve_port}

    def fover_server(self, port_name_dict):

        for port, name in port_name_dict.items():

            # There may be some ports that are not in Listen state, but are occupied
            try:
                tcp_server = server.ThreadingTCPServer(
                    server_name=name,
                    server_address=(self.conf.serve["bind"], port),
                    RequestHandlerClass=server.RequestHandler
                )

            except OSError as e:
                err = "faild: [{}:{}] {}"
                logger.default.error(err.format(name.split("_")[0], port, e))

            self.pool.submit(tcp_server.serve_forever)
