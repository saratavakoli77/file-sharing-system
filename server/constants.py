HEADERSIZE = 10
MAX_BUFFER = 2048
INITIAL_DIRECTORY = '/'

CLIENT_INITIATION_STATUS = "initiation"
CLIENT_NEEDPASSWORD_STATUS = "needPassword"
CLIENT_LOGGEDIN_STATUS = "loggedIn"

CLIENT_NORMALUSER_TYPE = "normalUser"
CLIENT_ADMINUSER_TYPE = "adminUser"

CMD_QUIT = "QUIT"
CMD_USER = "USER"
CMD_PASS = "PASS"
CMD_PWD = "PWD"
CMD_MKD = "MKD"
CMD_RMD = "RMD"
CMD_LIST = "LIST"
CMD_CWD = "CWD"
CMD_DL = "DL"
CMD_HELP = "HELP"
CMD_LS = "LS"
CMD_UP = "UP"

CMD_IN_INITIATION_STATUS = [CMD_USER]
CMD_IN_NEEDPASSWORD_STATUS = [CMD_PASS]
CMD_IN_LOGGEDIN_STATUS = [CMD_PWD, CMD_MKD, CMD_RMD, CMD_LIST, CMD_CWD, CMD_DL, CMD_LS, CMD_HELP, CMD_UP]



RESPONSE_USER_OK = "331 User name okay, need password."
RESPONSE_BAD_SEQUENCE = "503 Bad sequence of commands."
RESPONSE_LOGGED_IN = "230 User logged in, proceed."
RESPONSE_INVALID_USER_PASS = "430 Invalid username or password."
RESPONSE_DIRECTORY = "257 {}"
RESPONSE_DIRECTORY_CREATED = "257 {} created."
RESPONSE_DIRECTORY_DELETED = "250 {} deleted."
RESPONSE_LIST_TRANSFER = "226 List transfer done."
RESPONSE_LS_TRANSFER = "227 Ls transfer done"
RESPONSE_DIRECTORY_CHANGE = "250 Successful change."
RESPONSE_DOWNLOAD = "226 Successful download."
RESPONSE_UPLOAD = "226 Successful upload."

RESPONSE_NEED_LOGIN = "332 Need account for login."
RESPONSE_SYNTAX_ERROR = "501 Syntax error in parameters or arguments."
RESPONSE_QUIT = "221 Successful Quit."
RESPONSE_ERROR = "500 Error."
RESPONSE_FILE_UNAVAILABLE = "550 File unavailable."
RESPONSE_CANT_OPEN = "425 Can't open data connection."

DIRECTORIES = "DIRECTORIES:"
FILES = "FILES:"

MAKE_FILE_FLAG = "-i"
REMOVE_DIR_FLAG = "-f"

MAIL_ADDR = "mail.ut.ac.ir"
MAIL_ADDR_SERVER = 465
SENDER_EMAIL = "ghazal.minaei"
SENDER_PASSWORD = "row657-GH77"
MAIL_DOMAIN = "@ut.ac.ir"

HELO_COMMAND = "EHLO mail\r\n"

EMAIL_BODY = "Hello {}!\nYour remainder download size is {} bytes. Please consider recharging it.\n\nBest regards\n-FTPServer Team\n"
EMAIL_SUBJECT = "Download Threshold"

HELP_MESSAGE = """214\nUSER [name], Its argument is used to specify the user's string. It is used for user authentication.
PASS [password], Its argument is used to specify the user's password. It is used for user authentication.
PWD, It is used for printing current working directory
MKD [flag] [name], Its argument is used to specify the file/directory path. Flag: -i, If present, a new file will be created and otherwise a new directory. It is used for creating a new file or directory.
RMD [flag] [name], Its argument is used to specify the file/directory path. Flag: -f, If present, a directory will be removed and otherwise a file. It is used for removing a file or directory.
LIST, It is used for printing list of files exists in current working directory.
LS, It is used for printing list of directories and files exists in current working directory.
CWD [path], Its argument is used to specify the directory's path. It is used for changing the current working directory.
DL [name], Its argument is used to specify the file's name. It is used for downloading a file.
HELP, It is used for printing list of availabale commands.
QUIT, It is used for signing out from the server.
UP [name], Its argument is used to specify the file's name. It is used for uploading a file to current directory."""