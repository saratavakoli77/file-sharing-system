from socket import *
import base64, ssl
from constants import *

def sendEmail(emailTo, subject, content):
    try:
        mailServer = (MAIL_ADDR, MAIL_ADDR_SERVER)
        hostSocket = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))
        hostSocket.connect(mailServer)
        receivedMessageFromServer = hostSocket.recv(1024).decode()
        hostSocket.send(HELO_COMMAND.encode())
        receivedMessageFromServer = hostSocket.recv(1024).decode()
        authRequirements = ("\x00" + SENDER_EMAIL + "\x00" + SENDER_PASSWORD).encode()
        authRequirementsBase64 = base64.b64encode(authRequirements)
        authCommand = "AUTH PLAIN ".encode() + authRequirementsBase64 + "\r\n".encode()
        hostSocket.send(authCommand)
        receivedMessageFromServer = hostSocket.recv(1024).decode()
        mailFromCommand = "MAIL FROM:<" + SENDER_EMAIL + MAIL_DOMAIN + ">\r\n"
        hostSocket.send(mailFromCommand.encode())
        receivedMessageFromServer = hostSocket.recv(1024).decode()
        receiverEmailAddrCommand = "RCPT TO:<" + emailTo + ">\r\n"
        hostSocket.send(receiverEmailAddrCommand.encode())
        receivedMessageFromServer = hostSocket.recv(1024).decode()
        dataCommand = "DATA\r\n"
        hostSocket.send(dataCommand.encode())
        receivedMessageFromServer = hostSocket.recv(1024).decode()

        subject = "Subject: " + subject + "\r\n\r\n"
        hostSocket.send(subject.encode())
        content = "\r\n" + content + "\r\n.\r\n"
        hostSocket.send(content.encode())
        receivedMessageFromServer = hostSocket.recv(1024).decode()

        quit = "QUIT\r\n"
        hostSocket.send(quit.encode())

        receivedMessageFromServer = hostSocket.recv(1024).decode()
        hostSocket.close()
    except:
        print("sth went wrong")
