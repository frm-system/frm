import os
import socket
import struct

def ip2bytes(ip):
    return socket.inet_aton(ip)

def ip2int(ip):
    return struct.unpack("!I", ip2bytes(ip))[0]

def get_hostname():
    if os.name == 'nt':
        return os.getenv('COMPUTERNAME')
    else:
        return os.uname()[1]

def get_current_user():
    import getpass
    return getpass.getuser()

