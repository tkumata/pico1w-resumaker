import os

LOG_FILE = "/log.txt"
MAX_SIZE = 5120


def _clear_if_needed():
    try:
        stat = os.stat(LOG_FILE)
        if stat[6] > MAX_SIZE:
            with open(LOG_FILE, "w"):
                pass
    except OSError:
        pass


def error(message):
    try:
        _clear_if_needed()
        with open(LOG_FILE, "a") as file_obj:
            file_obj.write("[ERR] {}\n".format(str(message)))
    except Exception:
        pass
