import json

class ConfigHandler():
    def __init__(self, configFile):
        self.configFile = configFile
        self.configDict = self.readConfig()
        self.setConfig(self.configDict)
        
    def readConfig(self):
        with open(self.configFile, 'r') as file:
            configDict = json.load(file)
        return configDict

    def setConfig(self, configDict):
        self.commandChannelPort = configDict["commandChannelPort"]
        self.dataChannelPort = configDict["dataChannelPort"]
        self.users = configDict["users"]
        self.accounting = configDict["accounting"]
        self.logging = configDict["logging"]
        self.authorization = configDict["authorization"]
        
    def getUsers(self):
        return self.users
    
    def getCommandChannelPort(self):
        return self.commandChannelPort

    def getDataChannelPort(self):
        return self.dataChannelPort
    
    def isAccountingEnable(self):
        return self.accounting["enable"]
    
    def accountingThreshold(self):
        return int(self.accounting["threshold"])
    
    def accountingUsers(self):
        return self.accounting["users"]
    
    def isLoggingEnable(self):
        return self.logging["enable"]
    
    def loggingPath(self):
        return self.logging["path"]

    def isAuthorizationEnable(self):
        return self.authorization["enable"]
    
    def authorizationAdmins(self):
        return self.authorization["admins"]
    
    def authorizationFiles(self):
        return self.authorization["files"]
    
    def setSizeInAccounting(self, size, username):
        index = 0
        for user in self.configDict["accounting"]["users"]:
            print("user", user)
            print("user", user["user"])
            if user["user"] == username:
                break
            index += 1
        print("index", index)
        self.configDict["accounting"]["users"][index]["size"] = str(size)
        print(self.configDict)
        with open(self.configFile, "w") as file:
            json.dump(self.configDict, file, indent=2)
        self.updateAccounting()
    
    def updateAccounting(self):
        self.accounting = self.configDict["accounting"]