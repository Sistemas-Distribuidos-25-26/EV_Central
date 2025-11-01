from io import TextIOWrapper

PORT = 10001
BROKER_IP = "127.0.0.1"
BROKER_PORT = 9092

LOG_FILE : TextIOWrapper | None = None
try:
    LOG_FILE = open("app.log", "a+")
    LOG_FILE.truncate(0)
except OSError:
    LOG_FILE = None

def log(message: str):
    if LOG_FILE:
        LOG_FILE.write(message + '\n')
        LOG_FILE.flush()
    else:
        print(message)
