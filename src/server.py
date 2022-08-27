import socketserver

from . import tools

logger = tools.Logger()


class ThreadingTCPServer(socketserver.ThreadingTCPServer):

    allow_reuse_address = True

    # Override the __init__ method of TCPServer and pass in server_name
    def __init__(self, server_name, *args, **kwargs):
        self.server_name = server_name.split("_")[0]

        super(__class__, self).__init__(*args, **kwargs)

    # Override the last step of TCPServer and record the information that the service was started successfully
    def server_activate(self):
        super(__class__, self).server_activate()

        msg = "simulation [{}:{}] started successfully".format(
            self.server_name, self.server_address[1])

        logger.default.info(msg)


class RequestHandler(socketserver.BaseRequestHandler):

    @property
    def server_host(self):
        return self.server.server_address[0]

    @property
    def server_port(self):
        return self.server.server_address[1]

    @property
    def server_name(self):
        return self.server.server_name

    @property
    def client_addr(self):
        return self.client_address[0]

    @property
    def client_port(self):
        return self.client_address[1]

    def handle(self):

        # self.request == conn  ❶
        # self.client_address = client_address  ❷
        # self.server == ThreadingTCPServer

        logger.screen.info("[{}] connect server [{}:{}]".format(
            self.client_addr, self.server_name, self.server_port))

        while 1:
            try:
                data = self.request.recv(1024)
                if not data:
                    break

                logger.screen.info("received input from client")
                self.request.send(data.upper())

            except ConnectionResetError:
                break

        logger.screen.info("%s close connect" % self.client_address[0])
        self.request.close()
