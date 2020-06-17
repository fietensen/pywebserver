from pywebserver.server import Server
from pywebserver.handler import Handler
import webbrowser

host = "127.0.0.1"
port = 8787

server = Server(host=host, port=port, handler=Handler)
try:
    server.start()
    if webbrowser.open("http://{}:{}".format(host, port)):
        print("Opened the webpage in your browser.")
    else:
        print("Failed to open the webpage in your browser.")
        print("Visit http://{}:{}".format(host, port))
    while True:
        pass
except KeyboardInterrupt:
    server.stop()
