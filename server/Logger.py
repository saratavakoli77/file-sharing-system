import datetime

class Logger():
    def __init__(self, logFileAdr, isEnable):
        self.isEnable = isEnable
        self.logFileAdr = logFileAdr
        
    def log(self, adr, message):
        if not self.isEnable:
            return
        
        logFile = open(self.logFileAdr, "a+")
        
        date = datetime.datetime.now().strftime("%c")
        logMessage = "AT {} :: {} :\n\t {} \n"
        logFile.write(logMessage.format(date, adr, " ".join(message)))
        logFile.close()
