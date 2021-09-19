import socket
from clientHandler import *
from ConfigHandler import *
from Logger import *
LOCALHOST = "127.0.0.1"

class Server():
    def __init__(self, configFile):
        self.configFile = configFile
        self.configHandler = ConfigHandler(configFile)
        self.commandChannelPort = self.configHandler.getCommandChannelPort()
        self.dataChannelPort = self.configHandler.getDataChannelPort()
        self.setLogging()

    def setLogging(self):
        self.logger = Logger(self.configHandler.loggingPath(), self.configHandler.isLoggingEnable())

    def runServer(self):
        serverCmdSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverCmdSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverCmdSocket.bind((LOCALHOST, self.commandChannelPort))

        serverDataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverDataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverDataSocket.bind((LOCALHOST, self.dataChannelPort))
        self.logger.log("SERVER", ["STARTED"])
        print("Server started")
        print("Waiting for client request..")
        while True:
            serverCmdSocket.listen(1)
            clientCmdSocket, clientAddressOnCmd = serverCmdSocket.accept()
            clientCmdSocket.send(bytes("Hello", 'UTF-8'))

            serverDataSocket.listen(1)
            clientDataSocket, clientAddressOnData = serverDataSocket.accept()
            clientDataSocket.send(bytes("Hello, welcome to FTP server", 'UTF-8'))
            newthread = ClientHandler(clientAddressOnCmd, clientCmdSocket, clientDataSocket, self.configHandler, self.logger)
            newthread.start()




server = Server("config.json")
server.runServer()
