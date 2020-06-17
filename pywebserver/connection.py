# Notes:
#   - Handler takes Connection object

# Basically just a wrapper for connections, maybe I'll add something interesting
# later...
class Connection:
    def __init__(self, connection_details, timeout=None):
        self._connection = connection_details[0]
        self._host = connection_details[1][0]
        self._port = connection_details[1][1]

        if timeout:
            self._connection.settimeout(timeout)

    def close(self):
        try:
            self._connection.close()
        except Exception as e:
            return False
        return True

    def get(self, timeout=None):
        msg=b""
        try:
            while (_:=self._connection.recv(4096)):
                msg += _
                if b"\r\n\r\n" in msg or b"\n\n" in msg:
                    break
            return (True, msg)
        except socket.timeout:
            self._connection.close()
            return (False, msg)

    def send(self, msg):
        try:
            self._connection.send(msg)
            return True
        except Exception as e:
            self._connection.close()
            return False
