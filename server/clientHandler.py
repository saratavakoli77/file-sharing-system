import threading, os, pickle, shutil
from constants import *
from ConfigHandler import *
from Logger import *
from sendMail import sendEmail

class ClientHandler(threading.Thread):
    status = CLIENT_INITIATION_STATUS
    clientType = CLIENT_NORMALUSER_TYPE

    def __init__(self, clientAddress, cmdSocket, dataSocket, configHandler, logger):
        threading.Thread.__init__(self)
        self.configHandler = configHandler
        self.cmdSocket = cmdSocket
        self.dataSocket = dataSocket
        self.clientAddress = clientAddress
        self.user = None
        self.status = CLIENT_INITIATION_STATUS
        self.currentPath = INITIAL_DIRECTORY
        self.isAccountingAvailable = False
        self.userAccounting = None
        self.availableSize = 0
        self.logger = logger
        self.logger.log(clientAddress, ["connected"])
        print ("New connection added: ", clientAddress)

    def run(self):
        hello = self.cmdSocket.recv(MAX_BUFFER).decode()
        while True:
            try:
                parsedCmd = self.cmdSocket.recv(MAX_BUFFER).decode().rstrip().split(" ")
                response = self.commandHandler(parsedCmd)
                self.cmdSocket.sendall(bytes(response,'UTF-8'))
                if response == RESPONSE_QUIT:
                    break
            except:
                self.cmdSocket.sendall(bytes(RESPONSE_ERROR,'UTF-8'))
        self.logger.log(self.clientAddress, ["disconnected..."])
        print ("Client at ", self.clientAddress , " disconnected...")
    
    def commandHandler(self, parsedCmd):
        validation = self.validateCommand(parsedCmd)
        if validation:
            return validation
            
        if parsedCmd[0] == CMD_QUIT:
            return RESPONSE_QUIT
        elif parsedCmd[0] == CMD_USER:
            try:
                self.validateUser(parsedCmd[1])
                self.setStatus(CLIENT_NEEDPASSWORD_STATUS)
                self.logger.log(self.clientAddress, [parsedCmd[1], "need pass"])
                return RESPONSE_USER_OK
            except:
                return RESPONSE_INVALID_USER_PASS
        elif parsedCmd[0] == CMD_PASS:
            try:
                self.validatePassword(parsedCmd[1])
                self.setStatus(CLIENT_LOGGEDIN_STATUS)
                self.setType()
                self.setAccountingData()
                self.logger.log(self.clientAddress, [self.user["user"], "logged in", self.clientType])
                return RESPONSE_LOGGED_IN
            except:
                self.logger.log(self.clientAddress, [self.user["user"], "wrong pass"])
                return RESPONSE_INVALID_USER_PASS
        elif parsedCmd[0] == CMD_PWD:
            try:
                self.logger.log(self.clientAddress, [self.user["user"], "PWD requested", "in", self.currentPath])
                return RESPONSE_DIRECTORY.format(self.currentPath)
            except:
                return RESPONSE_ERROR
        elif parsedCmd[0] == CMD_MKD:
            name = ""
            try:
                if len(parsedCmd) == 2:
                    name = parsedCmd[1]
                    self.makeDirectory(name)
                    self.logger.log(self.clientAddress, [self.user["user"], CMD_MKD, self.currentPath + "/" + name])
                    return RESPONSE_DIRECTORY_CREATED.format(self.currentPath + "/" + name)
                else:
                    name = parsedCmd[2]
                    self.makeFile(name)
                    self.logger.log(self.clientAddress, [self.user["user"], CMD_MKD, name])
                    return RESPONSE_DIRECTORY_CREATED.format(name)
            except:
                return RESPONSE_ERROR
        elif parsedCmd[0] == CMD_RMD:
            name = ""
            try:
                if len(parsedCmd) == 2:
                    name = parsedCmd[1]
                    self.removeFile(name)
                else:
                    name = parsedCmd[2]
                    self.removeDirectory(name)
                self.logger.log(self.clientAddress, [self.user["user"], CMD_RMD, self.currentPath + name])
                return RESPONSE_DIRECTORY_DELETED.format(self.currentPath + name)
            except:
                return RESPONSE_ERROR
        elif parsedCmd[0] == CMD_LIST:
            try:
                listOfFiles = self.listFilesInDirectory()
                self.dataSocket.send(listOfFiles)
                self.logger.log(self.clientAddress, [self.user["user"], "LIST requested", "in", self.currentPath])
                return RESPONSE_LIST_TRANSFER
            except:
                return RESPONSE_ERROR
        elif parsedCmd[0] == CMD_CWD:
            name = ""
            try:
                if len(parsedCmd) == 1:
                    self.changeDirectory()
                else:
                    self.changeDirectory(parsedCmd[1])
                self.logger.log(self.clientAddress, [self.user["user"], CMD_CWD, "to", self.currentPath])
                return RESPONSE_DIRECTORY_CHANGE.format(self.currentPath)
            except:
                return RESPONSE_ERROR
        elif parsedCmd[0] == CMD_DL:
            try:
                if self.configHandler.isAuthorizationEnable():
                    if not self.isUserAuthorized(parsedCmd[1]):
                        self.logger.log(self.clientAddress, [self.user["user"], "Download Failed", "not authorized",  parsedCmd[1], "from", self.currentPath])
                        return RESPONSE_FILE_UNAVAILABLE
                if self.isAccountingAvailable:
                    if not self.haveEnoughSize(parsedCmd[1]):
                        self.handleAlert()
                        self.logger.log(self.clientAddress, [self.user["user"], "Download Failed", "not enough size",  parsedCmd[1], "from", self.currentPath])
                        return RESPONSE_CANT_OPEN
                res = self.sendFile(parsedCmd[1])
                if res:
                    self.logger.log(self.clientAddress, [self.user["user"], "Download Failed", "not such file", parsedCmd[1], "from", self.currentPath])
                    return RESPONSE_FILE_UNAVAILABLE
                self.updateSize(parsedCmd[1])
                self.handleAlert()
                self.logger.log(self.clientAddress, [self.user["user"], "Downloaded", parsedCmd[1], "from", self.currentPath])
                return RESPONSE_DOWNLOAD
            except:
                self.logger.log(self.clientAddress, [self.user["user"], "Download Failed", parsedCmd[1], "from", self.currentPath])
                return RESPONSE_ERROR
        elif parsedCmd[0] == CMD_HELP:
            try:
                self.logger.log(self.clientAddress, [self.user["user"], "HELP requested"])
                return self.sendHelp()
            except:
                return RESPONSE_ERROR
        elif parsedCmd[0] == CMD_LS:
            try:
                listOfAllFilesAndDirectories = self.lsInDirectory()
                self.dataSocket.send(listOfAllFilesAndDirectories)
                self.logger.log(self.clientAddress, [self.user["user"], "LS requested", "in", self.currentPath])
                return RESPONSE_LS_TRANSFER
            except:
                return RESPONSE_ERROR
        elif parsedCmd[0] == CMD_UP:
            try:
                res = self.downloadFile(parsedCmd[1])
                self.logger.log(self.clientAddress, [self.user["user"], "Uploaded", parsedCmd[1], "to", self.currentPath])
                return res
            except:
                self.logger.log(self.clientAddress, [self.user["user"], "Upload failed", parsedCmd[1], "to", self.currentPath])
                return RESPONSE_ERROR
        else:
            return RESPONSE_ERROR

    def validateCommand(self, command):
        validateParametersResult = self.validateParameters(command)
        if validateParametersResult:
            return validateParametersResult
        return self.validateStatus(command[0])

    def validateParameters(self, command):
        if command[0] == CMD_QUIT:
            if len(command) != 1:
                return RESPONSE_SYNTAX_ERROR
        
        elif command[0] == CMD_USER:
            if len(command) != 2:
                return RESPONSE_SYNTAX_ERROR
        
        elif command[0] == CMD_PASS:
            if len(command) != 2:
                return RESPONSE_SYNTAX_ERROR
        
        elif command[0] == CMD_PWD:
            if len(command) != 1:
                return RESPONSE_SYNTAX_ERROR
        
        elif command[0] == CMD_MKD:
            if len(command) == 3:
                if command[1] != MAKE_FILE_FLAG:
                    return RESPONSE_SYNTAX_ERROR
            elif len(command) != 2:
                return RESPONSE_SYNTAX_ERROR
        
        elif command[0] == CMD_RMD:
            if len(command) == 3:
                if command[1] != REMOVE_DIR_FLAG:
                    return RESPONSE_SYNTAX_ERROR
 
            elif len(command) != 2:
                return RESPONSE_SYNTAX_ERROR
        
        elif command[0] == CMD_LIST:
            if len(command) != 1:
                return RESPONSE_SYNTAX_ERROR
        
        elif command[0] == CMD_CWD:
            if len(command) > 2:
                return RESPONSE_SYNTAX_ERROR
        
        elif command[0] == CMD_DL:
            if len(command) != 2:
                return RESPONSE_SYNTAX_ERROR
        
        elif command[0] == CMD_UP:
            if len(command) != 2:
                return RESPONSE_SYNTAX_ERROR

        elif command[0] == CMD_HELP:
            if len(command) != 1:
                return RESPONSE_SYNTAX_ERROR

        elif command[0] == CMD_LS:
            if len(command) != 1:
                return RESPONSE_SYNTAX_ERROR

        else:
            return RESPONSE_SYNTAX_ERROR

    def validateStatus(self, command):
        if command in CMD_IN_INITIATION_STATUS and self.status != CLIENT_INITIATION_STATUS:
            raise "logged in before"

        elif command in CMD_IN_LOGGEDIN_STATUS and self.status != CLIENT_LOGGEDIN_STATUS:
            return RESPONSE_NEED_LOGIN

        elif command in CMD_IN_NEEDPASSWORD_STATUS and self.status != CLIENT_NEEDPASSWORD_STATUS:
            return RESPONSE_BAD_SEQUENCE


    def validateUser(self, username):
        users = self.configHandler.getUsers()
        for user in users:
            if user["user"] == username:
                self.user = user
                return
        raise "username not find"
    

    def validatePassword(self, password):
        if self.user["password"] != password:
            raise "wrong pass"

    def setStatus(self, newStatus):
        self.status = newStatus
    
    def setType(self):
        admins = self.configHandler.authorizationAdmins()
        if self.user["user"] in admins:
            self.clientType = CLIENT_ADMINUSER_TYPE
    
    def setAccountingData(self):
        if not self.configHandler.isAccountingEnable():
            return
        accountingUsers = self.configHandler.accountingUsers()
        for accountingUser in accountingUsers:
            if accountingUser["user"] == self.user["user"]:
                self.userAccounting = accountingUser
                self.isAccountingAvailable = True
                self.availableSize = int(accountingUser["size"])
    
    def makeFile(self, name):
        file = open(self.getAbsolutePath()+ "/" +name, 'x')
        file.close()

    def makeDirectory(self, name):
        os.mkdir(self.getAbsolutePath()+ "/" +name)

    def setPath(self, newName):
        self.currentPath = os.path.join(self.currentPath, newName)

    def getAbsolutePath(self):
        if self.currentPath == "/":
            return os.getcwd()
        return os.getcwd() + self.currentPath
    
    def removeFile(self, name):
        os.remove(name)

    def removeDirectory(self, name):
        shutil.rmtree(name)
    
    def listFilesInDirectory(self):
        files = [f for f in os.listdir(self.getAbsolutePath()) if os.path.isfile(os.path.join(self.getAbsolutePath(), f))]
        msg = pickle.dumps(files)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'UTF-8') + msg
        return msg

    def changeDirectory(self, path = None):
        if path is None:
            self.currentPath = INITIAL_DIRECTORY
            return
        if path[0] == '/':
            path = path[1:]
        relativePath = os.path.join(self.currentPath, path)
        relativePath = os.path.normpath(relativePath)
        self.setPath(relativePath)
        absPath = self.getAbsolutePath()
        if os.path.isdir(absPath):
            self.currentPath = relativePath
            return
        raise "path not available"

    def sendFile(self, fileName):
        try:
            path = os.path.join(self.currentPath, fileName)
            path = os.getcwd() + path
            file = open(path,'rb')
        except:
            return RESPONSE_FILE_UNAVAILABLE
        partOfFile = file.read(MAX_BUFFER)
        while (partOfFile):
            self.dataSocket.send(partOfFile)
            partOfFile = file.read(MAX_BUFFER)
        file.close()
    
    def isUserAuthorized(self, fileName):
        if self.isUserAdmin():
            return True
        if not self.isFileProtected(fileName):
            return True
        return False
    
    def isUserAdmin(self):
        return self.clientType == CLIENT_ADMINUSER_TYPE
    
    def isFileProtected(self, fileName):
        authorizationFiles = self.configHandler.authorizationFiles()
        return self.getPathToFile(fileName) in authorizationFiles
        
    def getPathToFile(self, fileName):
        if self.currentPath == "/":
            return "." + self.currentPath + fileName
        return "." + self.currentPath + "/" + fileName
    
    def haveEnoughSize(self, fileName):
        fileSize = self.getFileSize(fileName)
        return self.availableSize >= fileSize
        
    def updateSize(self, fileName):
        if not self.isAccountingAvailable:
            return
        self.availableSize -= self.getFileSize(fileName)
        self.configHandler.setSizeInAccounting(self.availableSize, self.user["user"])

    def handleAlert(self):
        if not self.isAccountingAvailable:
            return
        if self.userAccounting["alert"]:
            if self.availableSize < self.configHandler.accountingThreshold():
                sendEmail(self.userAccounting["email"], EMAIL_SUBJECT, EMAIL_BODY.format(self.user["user"], self.availableSize))
                self.logger.log(self.clientAddress, [self.user["user"], "mail sent", "to", self.userAccounting["email"]])
    
    def getFileSize(self, fileName):
        return os.path.getsize(os.path.join(self.getAbsolutePath(), fileName))
    
    def sendHelp(self):
        return HELP_MESSAGE

    def lsInDirectory(self):
        files = [f for f in os.listdir(self.getAbsolutePath()) if os.path.isfile(os.path.join(self.getAbsolutePath(), f))]
        os.walk(self.getAbsolutePath())
        pathOfDirectories = [x[0] for x in os.walk(self.getAbsolutePath())]
        pathOfDirectories = pathOfDirectories[1:]
        allFilesAndDirectories = []
        allFilesAndDirectories.append(DIRECTORIES)
        for directory in pathOfDirectories:
            allFilesAndDirectories.append(os.path.basename(directory))
        allFilesAndDirectories.append(FILES)
        for file in files:
            allFilesAndDirectories.append(file)
        msg = pickle.dumps(allFilesAndDirectories)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'UTF-8') + msg
        return msg
    
    def downloadFile(self, fileName):
        self.dataSocket.settimeout(2)
        try:
            data = self.dataSocket.recv(MAX_BUFFER)
        except:
            return RESPONSE_ERROR
        file = open(self.getPathToFile(fileName), 'wb')
        file.write(data)
        while True:
            try:
                data = self.dataSocket.recv(MAX_BUFFER)
            except:
                break
            file.write(data)
        file.close()
        self.dataSocket.settimeout(None)
        return RESPONSE_UPLOAD