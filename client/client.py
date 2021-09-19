 
import socket, pickle
SERVER = "127.0.0.1"
PORT = 8000
CMD_LIST = "LIST"
CMD_QUIT = "QUIT"
CMD_DL = "DL"
CMD_LS = "LS"
CMD_UP = "UP"

DIRECTORIES = "DIRECTORIES:"
FILES = "FILES:"

HEADERSIZE = 10
BUFFER_SIZE = 2048

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def receiveData(dataSocket):
    fullMessage = b''
    dataSocket.settimeout(2)
    newMessage = True
    while True:
        try:
            msg = dataSocket.recv(BUFFER_SIZE)
        except:
            break
        if newMessage:
            msglen = int(msg[:HEADERSIZE])
            newMessage = False
            fullMessage += msg
        if len(fullMessage)-HEADERSIZE == msglen:
            fullMessage = pickle.loads(fullMessage[HEADERSIZE:])
            newMessage = True
            break
    return fullMessage

def downloadFile(dataSocket, fileName):
    dataSocket.settimeout(2)
    try:
        data = dataSocket.recv(BUFFER_SIZE)
    except:
        return
    file = open(fileName, 'wb')
    file.write(data)
    while True:
        try:
            data = dataSocket.recv(BUFFER_SIZE)
        except:
            break
        file.write(data)
    file.close()

def sendFile(fileName):
    dataSocket.settimeout(2)
    try:
        file = open(fileName, 'rb')
    except:
        return
    partOfFile = file.read(BUFFER_SIZE)
    while (partOfFile):
        dataSocket.send(partOfFile)
        partOfFile = file.read(BUFFER_SIZE)
    file.close()

def printList(inList):
    for item in inList:
        if item == DIRECTORIES or item == FILES:
            print(bcolors.FAIL + bcolors.BOLD + item + bcolors.ENDC)
        print(bcolors.WARNING + item + bcolors.ENDC)

cmdSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cmdSocket.connect((SERVER, PORT))
inData =  cmdSocket.recv(BUFFER_SIZE)

dataSocket.connect((SERVER, 8001))
inData = dataSocket.recv(BUFFER_SIZE)
print(bcolors.WARNING + bcolors.BOLD + inData.decode() + bcolors.ENDC)

cmdSocket.sendall(bytes("This is from Client", 'UTF-8'))
while True:
    outData = input()
    outDataSplitted = outData.split()
    cmdSocket.sendall(bytes(outData,'UTF-8'))
    if outDataSplitted[0] == CMD_LIST:
        printList(receiveData(dataSocket))
        dataSocket.settimeout(None)
    elif outDataSplitted[0] == CMD_DL:
        downloadFile(dataSocket, outDataSplitted[1])
        dataSocket.settimeout(None)
    elif outDataSplitted[0] == CMD_LS:
        printList(receiveData(dataSocket))
        dataSocket.settimeout(None)
    elif outDataSplitted[0] == CMD_UP:
        if not len(outDataSplitted) < 2:
            sendFile(outDataSplitted[1])
            dataSocket.settimeout(None)
    elif outDataSplitted[0] == CMD_QUIT:
        inData = cmdSocket.recv(BUFFER_SIZE)
        print(inData.decode())
        break
    inData = cmdSocket.recv(BUFFER_SIZE)
    print(bcolors.OKBLUE + bcolors.BOLD + inData.decode() + bcolors.ENDC)

  
cmdSocket.close()
dataSocket.close()