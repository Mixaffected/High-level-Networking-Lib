import socket
import threading


class Server:
    """
    The server side class.

    Functions:\n
    .start() starts the server.
    .stop() stops the server.
    """

    serverRunning = True
    serverStopped = False

    encoding = "utf-8"
    closeMsg = "/CLOSECON"
    serverThreads = {}

    activeConnections = {}
    recvedMsg = {}

    address = ()

    def __init__(self, address=socket.gethostbyname(socket.gethostname()), port=5050, maxConnections=0, defaultBufferSize=64):
        self.serverIp = str(address)
        self.serverPort = int(port)
        self.address = (str(address), int(port))
        self.serverMaxConnections = int(maxConnections)
        self.serverDefaultBufferSize = int(defaultBufferSize)

    # Start the server instance
    def start(self):
        """
        Start the server instance
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"[SERVER] Server starting...")

        self.server.bind(self.address)
        self.server.listen(self.serverMaxConnections)

        print(f"[SERVER] Server started")
        print(f"[SERVER] Listening on {self.serverIp}:{self.serverPort}")

        thread = threading.Thread(target=self.__waitForConnection)
        self.serverThreads["waitForConThread"] = thread
        thread.start()

    def __waitForConnection(self):
        """
        Do not use!
        """
        while self.serverRunning:
            connection, address = self.server.accept()

            if self.serverRunning:
                thread = threading.Thread(
                    target=self.__handleConnection, args=(connection, address))
                thread.start()

    def __handleConnection(self, connection, address):
        """
        Do not use!
        """
        print(f"[CONNECTION] Got connection from {address}")
        self.activeConnections[address[0]] = [address, connection]
        self.recvedMsg[address[0]] = {}
        print(f"[ACTIVE CONNECTIONS] {len(self.activeConnections)}")

        connected = True

        while self.serverRunning and connected:
            messageSize = connection.recv(
                self.serverDefaultBufferSize).decode(self.encoding)

            if messageSize:
                messageSize = int(messageSize)

                msg = connection.recv(messageSize).decode(self.encoding)
                msg = str(msg)

                print(f"[{address}] {msg}")

                splitMsg = msg.split("|")
                if splitMsg[1] == self.closeMsg:
                    connected = False

                # convert to send type
                if splitMsg[0] == "str":
                    splitMsg[1] = str(splitMsg[1])
                elif splitMsg[0] == "int":
                    splitMsg[1] = int(splitMsg[1])
                elif splitMsg[0] == "float":
                    splitMsg[1] = float(splitMsg[1])
                elif splitMsg[0] == "complex":
                    splitMsg[1] = complex(splitMsg[1])
                elif splitMsg[0] == "list":
                    splitMsg[1] = list(splitMsg[1])
                elif splitMsg[0] == "tuple":
                    splitMsg[1] = tuple(splitMsg[1])
                elif splitMsg[0] == "range":
                    splitMsg[1] = range(splitMsg[1])
                elif splitMsg[0] == "dict":
                    splitMsg[1] = splitMsg[1]
                elif splitMsg[0] == "set":
                    splitMsg[1] = set(splitMsg[1])
                elif splitMsg[0] == "frozenset":
                    splitMsg[1] = frozenset(splitMsg[1])
                elif splitMsg[0] == "bool":
                    splitMsg[1] = bool(splitMsg[1])
                elif splitMsg[0] == "bytes":
                    splitMsg[1] = bytes(splitMsg[1])
                elif splitMsg[0] == "bytearray":
                    splitMsg[1] = bytearray(splitMsg[1])
                elif splitMsg[0] == "memoryview":
                    splitMsg[1] = memoryview(splitMsg[1])
                elif splitMsg[0] == "None":
                    splitMsg[1] = None

                self.recvedMsg[address[0]][len(
                    self.recvedMsg[address[0]])] = splitMsg[1]

        if self.serverRunning and not self.serverStopped:
            self.__sendAll(self.closeMsg, address[0])

        connection.close()
        print(f"[CONNECTION] Lost connection from {address}")
        del self.activeConnections[address[0]]
        print(f"[ACTIVE CONNECTIONS] {len(self.activeConnections)}")

    def send(self, msg, address="all"):
        """
        Send data to the connected client.

        Forbidden sing: |
        """
        thread = threading.Thread(target=self.__sendAll, args=(msg, address))
        thread.start()

    def __sendAll(self, msg, address="all"):
        """
        Do not use!
        """
        if len(self.activeConnections) < 0:
            return

        connection = {}
        print(self.activeConnections)
        if address != "all":
            for con in self.activeConnections:
                if address == con:
                    connection = self.activeConnections[address][1]
        else:
            connection = "all"

        typeOf = "None"

        # get send type
        tMsg = type(msg)
        if tMsg == str:
            typeOf = "str"
        elif tMsg == int:
            typeOf = "int"
        elif tMsg == float:
            typeOf = "float"
        elif tMsg == complex:
            typeOf = "complex"
        elif tMsg == list:
            typeOf = "list"
        elif tMsg == tuple:
            typeOf = "tuple"
        elif tMsg == range:
            typeOf = "range"
        elif tMsg == dict:
            typeOf = "dict"
        elif tMsg == set:
            typeOf = "set"
        elif tMsg == frozenset:
            typeOf = "frozenset"
        elif tMsg == bool:
            typeOf = "bool"
        elif tMsg == bytes:
            typeOf = "bytes"
        elif tMsg == bytearray:
            typeOf = "bytearray"
        elif tMsg == memoryview:
            typeOf = "memoryview"
        elif tMsg == None:
            typeOf = "None"
        else:
            typeOf = ""

        if type(typeOf) == str:
            message = f"{typeOf}|{msg}"
        else:
            message = f"{msg}"

        message = message.encode(self.encoding)
        msgLenght = len(message)
        sendLenght = str(msgLenght).encode(self.encoding)
        sendLenght += b" " * (self.serverDefaultBufferSize - len(sendLenght))

        if connection != "all":
            connection.send(sendLenght)
            connection.send(message)
        elif connection == "all":
            for con in self.activeConnections:
                self.activeConnections[con][1].send(sendLenght)
                self.activeConnections[con][1].send(message)

    def getRecivedMsg(self):
        recvMsg = dict(self.recvedMsg)
        for element in self.recvedMsg:
            self.recvedMsg[element] = {}

        return recvMsg

    def getConnections(self):
        return self.activeConnections

    # Stop the server
    def stop(self):
        """
        Stop the server instance and disconnect all clients
        """
        self.__sendAll(self.closeMsg)
        self.serverRunning = False
        self.serverStopped = True


class Client:
    """
    The client class

    Functions:\n
    .connect() connects to the specified server.
    """

    clientRunning = True

    encoding = "utf-8"
    closeMsg = "/CLOSECON"

    address = ()
    defaultBufferSize = int

    receivedMessages = {}

    def __init__(self, address=str, port=5050, defaultBufferSize=64):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.serverAddress = address
        self.serverPort = port
        self.address = (address, port)
        self.defaultBufferSize = int(defaultBufferSize)
        self.clientAddress = socket.gethostbyname(socket.gethostname())

    def connect(self):
        """
        Connect to the specified server
        """
        isConnected = False

        try:
            self.client.connect(self.address)
        except Exception as e:
            # print(f"{e}")
            isConnected = False
            raise e

        if isConnected:
            thread = threading.Thread(target=self.__handleServerConnection)
            thread.start()

    def send(self, msg):
        """
        Send data to the connected server.

        Forbidden sing: |
        """
        typeOf = "None"

        # get send type
        tMsg = type(msg)
        if tMsg == str:
            typeOf = "str"
        elif tMsg == int:
            typeOf = "int"
        elif tMsg == float:
            typeOf = "float"
        elif tMsg == complex:
            typeOf = "complex"
        elif tMsg == list:
            typeOf = "list"
        elif tMsg == tuple:
            typeOf = "tuple"
        elif tMsg == range:
            typeOf = "range"
        elif tMsg == dict:
            typeOf = "dict"
        elif tMsg == set:
            typeOf = "set"
        elif tMsg == frozenset:
            typeOf = "frozenset"
        elif tMsg == bool:
            typeOf = "bool"
        elif tMsg == bytes:
            typeOf = "bytes"
        elif tMsg == bytearray:
            typeOf = "bytearray"
        elif tMsg == memoryview:
            typeOf = "memoryview"
        elif tMsg == None:
            typeOf = "None"
        else:
            typeOf = ""

        if type(typeOf) == str:
            message = f"{typeOf}|{msg}"
        else:
            message = f"{msg}"

        message = message.encode(self.encoding)
        msgLenght = len(message)
        sendLenght = str(msgLenght).encode(self.encoding)
        sendLenght += b" " * (self.defaultBufferSize - len(sendLenght))

        self.client.send(sendLenght)
        self.client.send(message)

    def __handleServerConnection(self):
        while self.clientRunning:
            messageSize = self.client.recv(
                self.defaultBufferSize).decode(self.encoding)

            if messageSize:
                messageSize = int(messageSize)

                msg = self.client.recv(messageSize).decode(self.encoding)
                msg = str(msg)

                print(f"[SERVER] {msg}")

                splitMsg = msg.split("|")
                if splitMsg[1] == self.closeMsg:
                    print("[CONNECTION CLOSED] Connection closed from Server")
                    self.clientRunning = False

                # convert to send type
                if splitMsg[0] == "str":
                    splitMsg[1] = str(splitMsg[1])
                elif splitMsg[0] == "int":
                    splitMsg[1] = int(splitMsg[1])
                elif splitMsg[0] == "float":
                    splitMsg[1] = float(splitMsg[1])
                elif splitMsg[0] == "complex":
                    splitMsg[1] = complex(splitMsg[1])
                elif splitMsg[0] == "list":
                    splitMsg[1] = list(splitMsg[1])
                elif splitMsg[0] == "tuple":
                    splitMsg[1] = tuple(splitMsg[1])
                elif splitMsg[0] == "range":
                    splitMsg[1] = range(splitMsg[1])
                elif splitMsg[0] == "dict":
                    splitMsg[1] = splitMsg[1]
                elif splitMsg[0] == "set":
                    splitMsg[1] = set(splitMsg[1])
                elif splitMsg[0] == "frozenset":
                    splitMsg[1] = frozenset(splitMsg[1])
                elif splitMsg[0] == "bool":
                    splitMsg[1] = bool(splitMsg[1])
                elif splitMsg[0] == "bytes":
                    splitMsg[1] = bytes(splitMsg[1])
                elif splitMsg[0] == "bytearray":
                    splitMsg[1] = bytearray(splitMsg[1])
                elif splitMsg[0] == "memoryview":
                    splitMsg[1] = memoryview(splitMsg[1])
                elif splitMsg[0] == "None":
                    splitMsg[1] = None

                self.receivedMessages[len(self.receivedMessages)] = splitMsg[1]

    def getRecvedMsg(self):
        return self.receivedMessages

    def getServerAddress(self):
        return self.address

    def getClientAddress(self):
        return self.clientAddress

    def isConnected(self):
        return self.clientRunning

    def disconnect(self):
        """
        Disconnect from the current server and stop all running functions.
        """
        self.send(self.closeMsg)
        self.client.close()
        self.clientRunning = False
