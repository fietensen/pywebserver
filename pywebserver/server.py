from threading import Thread
from pywebserver.connection import Connection
import pywebserver.handler
import socket, time, importlib

# The main server application
class Server(Thread):
    def __init__(self, host="0.0.0.0", port=8080, maxclients=10, timeout=5, handler=None, debug=False):
        assert handler, "ServerHandler(handler) not set."

        super(Server, self).__init__()

        self._socket = None
        self._host = host
        self._port = port
        self._maxclients = maxclients
        self._handler = handler
        self._connections = []
        self._client_handles = []
        self._running = True
        self._timeout = timeout
        self._debug = debug

    def run(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen(self._maxclients)
        self._socket.settimeout(self._timeout)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if self._debug:
            print("[DEBUG] Started server...")

        while self._running:
            try:
                self._connections.append((_:=Connection(self._socket.accept())))
                if self._debug:
                    importlib.reload(pywebserver.handler)
                    client_handler = pywebserver.handler.Handler(_)
                else:
                    client_handler = self._handler(_)
                self._client_handles.append(client_handler)
                client_handler.start()
                if self._debug:
                    print("[DEBUG] Connection created")
            except socket.timeout:
                if self._debug:
                    print("[DEBUG] Timeout while accepting...")
                pass
            except Exception as e:
                print("[Error]: An error occured in the mainserver class while trying to accept connections (%s)" % str(e))
        print("[Info]: Stopped accepting connections.")

    def stop(self):
        print("[Info]: Stopping server....")
        self._running = False
        time.sleep(self._timeout)
        for client in self._connections:
            if not client.close():
                print("[Error]: Not able to close connection to client")
        print("[Info]: Successfully closed Server!")

