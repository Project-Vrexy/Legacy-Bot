import os

def path():
    if os.name == "nt":
        return "./"
    return "/root/runner/pub/aeon"
