"""
This high level libary makes setting up a client and a server super easy.
"""
import socket
import threading
import multiprocessing
from time import time
from threading import current_thread


class Server:
    """
    The server side class.\n
    \n
    Functions:\n
        .start() start the server.\n
        .stop() stop the server.\n
        .send() send data to one or all clients.\n
        .getRecivedMsg() get all received messages.\n
        .getConnections() get all connections.
    """

    serverRunning = False
    serverStopped = False
    startTime = -1

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
        if self.serverRunning:
            print("[WARNING] Server already started!")
            return
        elif multiprocessing.current_process().name != "MainProcess":
            return

        self.startTime = time()
        self.serverRunning = True

        # set up the socket to IPv4 and TCP Stream
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"[SERVER] Server starting...")

        # bind to the given address and set max Connections
        self.server.bind(self.address)
        print(f"[SERVER] Server started")

        self.server.listen(self.serverMaxConnections)
        print(f"[SERVER] Listening on {self.serverIp}:{self.serverPort}")

        # start new thread to handle incoming connections add it to the serverThreads dict
        thread = self.__startNewProcess(target=self._waitForConnection)
        self.serverThreads["waitForConThread"] = thread
        thread.start()

    def __startNewProcess(self, target, args=(), name="") -> multiprocessing.Process:
        """
        Do not use!
        """
        if multiprocessing.current_process().name == "MainProcess" or "processHandler":
            if name != "":
                thread = multiprocessing.Process(
                    target=target, args=args, name=name)
            else:
                thread = multiprocessing.Process(target=target, args=args)

            return thread

    def _waitForConnection(self):
        """
        Do not use!
        """

        currProcess = multiprocessing.current_process()
        currProcess.name = "processHandler"

        # run while the server is running
        while self.serverRunning:
            # if incoming connection accept it WARNING BLOCKING FUNCTION
            connection, address = self.server.accept()

            # backchecks if server is running to prevent errors
            if self.serverRunning:
                # start new thread to handle Connection
                thread = multiprocessing.Process(
                    target=self.__handleConnection, args=(connection, address))
                thread.start()

    def __handleConnection(self, connection, address):
        """
        Do not use!
        """
        # The first message is the lenght of the second message

        print(f"[CONNECTION] Got connection from {address}")
        # add the address and connection to the activeConnections dict
        self.activeConnections[address[0]] = (address, connection)
        # add the message object to the recvedMsg dict
        self.recvedMsg[address[0]] = {}
        print(f"[ACTIVE CONNECTIONS] {len(self.activeConnections)}")

        connected = True

        # run as long the server should run and the client is connected
        while self.serverRunning and connected:
            # recve the first message WARNING NEW CONNECTIONS SEND ONE EMPTY MESSAGE: ""
            messageSize = connection.recv(
                self.serverDefaultBufferSize).decode(self.encoding)

            # check if message isnt empty
            if messageSize:

                # converts the message to an int
                messageSize = int(messageSize)

                # recve the actual message with the size of the
                msg = connection.recv(messageSize).decode(self.encoding)
                msg = str(msg)

                print(f"[{address}] {msg}")

                # convert the message back to its original type
                splitMsg = msg.split("|")

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

                if splitMsg[1] == self.closeMsg:
                    connected = False
                else:
                    self.recvedMsg[address[0]][len(
                        self.recvedMsg[address[0]])] = splitMsg[1]

        if not self.serverRunning and not self.serverStopped:
            self.__sendDirect(self.closeMsg, address[0])

        connection.close()
        print(f"[CONNECTION] Lost connection from {address}")
        self.activeConnections.pop(address[0])
        print(f"[ACTIVE CONNECTIONS] {len(self.activeConnections)}")

    def send(self, msg: str, address="all"):
        """
        Send data to the connected client.

        Forbidden sing: |
        """
        # start a thread to send data asynchronous
        thread = multiprocessing.Process(
            target=self.__sendDirect, args=(msg, address))
        thread.start()

    def __sendDirect(self, msg: str, address="all"):
        """
        Do not use!
        """
        # check if some client is connected
        if len(self.activeConnections) <= 0:
            return

        connection = {}
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

        # message get encoded
        message = message.encode(self.encoding)
        # the byte lengh
        msgLenght = len(message)
        # byte lengh get encoded
        sendLenght = str(msgLenght).encode(self.encoding)
        # the buffer get filled with empty bytes
        sendLenght += b" " * (self.serverDefaultBufferSize - len(sendLenght))

        # check if for one or for all
        if connection != "all":
            # send to one client
            connection.send(sendLenght)
            connection.send(message)
        elif connection == "all":
            # send to all clients
            for con in self.activeConnections:
                self.activeConnections[con][1].send(sendLenght)
                self.activeConnections[con][1].send(message)

    def getRecivedMsg(self) -> dict:
        """
        Get all received messages
        """

        # remove all left clients from recvedMsg dict
        def removeElementFromList(self, leftClients):
            for el in leftClients:
                if el in self.recvedMsg.keys():
                    self.recvedMsg.pop(el)

        # get all recved messages
        recvMsg = dict(self.recvedMsg)
        leftClients = []
        for element in self.recvedMsg.keys():
            if element in self.activeConnections:
                self.recvedMsg[element] = {}
            else:
                leftClients.append(element)

        if leftClients != []:
            thread = multiprocessing.Process(
                target=removeElementFromList, args=(self, leftClients))
            thread.start()

        return recvMsg

    # return all connections
    def getConnections(self) -> dict:
        """
        Get dict of all active connections
        """
        return self.activeConnections

    # Stop the server
    def stop(self):
        """
        Stop the server instance and disconnect all clients
        """
        print("[SERVER] Stopping...")
        self.__sendDirect(self.closeMsg, "all")
        self.serverRunning = False
        self.serverStopped = True

        for thread in self.serverThreads.items():
            if thread.is_alive():
                thread.terminate()

            thread.close()

        print("[SERVER] Stopped")


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
        isConnected = True

        try:
            self.client.connect(self.address)
        except Exception as e:
            isConnected = False
            raise e

        if isConnected:
            thread = threading.Thread(target=self.__handleServerConnection)
            thread.start()

    def send(self, msg):
        """
        Asyncronous send data to the server.

        Forbidden sing: |
        """
        thread = threading.Thread(target=self.__sendDirect, args=(msg))
        thread.start()

    def __sendDirect(self, msg):
        """
        Send data to the server wait on complete data send.

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
            message = f"|{msg}"

        message = message.encode(self.encoding)
        msgLenght = len(message)
        sendLenght = str(msgLenght).encode(self.encoding)
        sendLenght += b" " * (self.defaultBufferSize - len(sendLenght))

        self.client.send(sendLenght)
        self.client.send(message)

    def __handleServerConnection(self):
        """
        Do not use!
        """
        while self.clientRunning:
            messageSize = self.client.recv(
                self.defaultBufferSize).decode(self.encoding)

            if messageSize:
                messageSize = int(messageSize)

                msg = self.client.recv(messageSize).decode(self.encoding)
                msg = str(msg)

                print(f"[MESSAGE] {msg}")

                splitMsg = msg.split("|")

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

                if splitMsg[1] == self.closeMsg:
                    print("[CONNECTION CLOSED] Connection closed from Server")
                    self.clientRunning = False
                else:
                    self.receivedMessages[len(
                        self.receivedMessages)] = splitMsg[1]

    def getRecvedMsg(self):
        recvMsg = dict(self.receivedMessages)
        self.receivedMessages = {}

        return recvMsg

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
