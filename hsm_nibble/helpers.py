import os


DEBUG_LEVEL = bool("DEBUG" in os.environ)

def log(text: str, level: int = 1):
    if DEBUG_LEVEL >= level:
        print(text)


