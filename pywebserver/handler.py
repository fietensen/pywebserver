from threading import Thread
import pywebserver.config
import os, sys
import importlib

importlib.reload(pywebserver.config)
Configuration = pywebserver.config.Configuration

def getfile(fname, parser):
    if Configuration.parsing["Python"] and fname.endswith(".py"):
        spec = importlib.util.spec_from_file_location("test", fname)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "handle"):
            return mod.handle(parser)
        else:
            with open(fname, "rb") as fp:
                return fp.read()
    elif Configuration.parsing["App"] and fname.endswith(".app"):
        return os.popen(fname).read()

    elif Configuration.parsing["Oxidian"] and fname.endswith(".oxy"):
        return os.popen("Oxidian {}".format(fname)).read()
    else:
        try:
            with open(fname, "r") as fp:
                return fp.read()
        except:
            with open(fname, "rb") as fp:
                return fp.read()

def gen_directory_listing(path, remove):
    if path.endswith("/"):
        path = path[:-1]
    stuff = list(os.walk(path))[0]
    dirs = stuff[1]
    files = stuff[2]
    dirs = "<br/>".join("<a href=\"{1}/{0}\">{0}</a>".format(d, path[len(remove):]) for d in dirs)
    files = "<br/>".join("<a href=\"{1}/{0}\">{0}</a>".format(f, path[len(remove):]) for f in files)
    base = "<html><head><title>Directory listing for {0}</title></head><body><center><h1>Directory listing for {0}</h1></center><h3>Files:</h3>{1}<h3>Directories:</h3>{2}</body></html>".format(path[len(remove):], files, dirs)
    return base

class Parser:
    def __init__(self, request):
        sp = request.split(b"\r\n\r\n")
        try:
            self.data = (dict(key.split('=') for key in sp[1].decode().split('&'))) if len(sp) == 2 and sp[1] != b'' else {}
        except Exception as e:
            self.data = {}
        self._request = request.replace(b"\r\n\r\n", b"")
        self._reqhead = self._request.decode().split("\r\n")[0]
        self._headers = self._request.decode().split("\r\n")[1:]
        self.headers = {}
        for header in self._headers:
            key = header.split(" ")[0][:-1]
            value = " ".join(c for c in header.split(" ")[1:])
            self.headers[key] = value
        self.method, self.path, self.version = self._reqhead.split(" ")

        print("Detailed Info:")
        print("  Method Used: {}".format(self.method))
        print("  File Requested {}".format(self.path))
        print("  Host Requested: {}".format(self.headers["Host"]))
        print("  User-Agent: {}".format(self.headers["User-Agent"]))
    def get(self):
        response = "200 OK"
        code = ""

        if not Configuration.security["PathTraversal"] and ".." in self.path:
            code = getfile(Configuration.filestructure["/"], self)
        elif self.path in Configuration.filestructure.keys():
            code = getfile(Configuration.filestructure[self.path], self)
        else:
            if Configuration.access["PreDefAlternateFile"]:
                code = getfile(Configuration.filestructure[None], self)
            else:
                if os.path.isfile(Configuration.filestructure[None]+self.path):
                    code = getfile(Configuration.filestructure[None]+self.path, self)
                elif os.path.isdir(Configuration.filestructure[None]+self.path):
                    code = gen_directory_listing(Configuration.filestructure[None]+self.path, Configuration.filestructure[None])
                else:
                    response = "404 File Not Found"
                    code = getfile(Configuration.filestructure[404], self)
        return (response, code)

class ServerResponse:
    def __init__(self, code="500 Internal Server Error", content="", headers={}):
        self._headers = "\r\n".join("{}: {}".format(key, headers[key]) for key in headers.keys())
        self._status = code
        self._content = content
        self.response = b"HTTP/1.1 "+self._status.encode()+b"\r\n"+self._headers.encode()+b"\r\n"+self._content.encode() if type(self._content) == str else self._content+b"\r\n"

class Handler(Thread):
    def __init__(self, connection):
        super(Handler, self).__init__()
        self._connection = connection

    def run(self):
        status, content = self._connection.get(timeout=5)
        if not status:
            self._connection.close()
            return

        parser = Parser(content)
        code, response_content = parser.get()

        response = ServerResponse(code=code, content=response_content)
        self._connection.send(response.response)
        self._connection.close()
