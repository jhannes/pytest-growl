import time
import socket
import struct
from cStringIO import StringIO
from hashlib import md5

_GROWL_UDP_PORT = 9887
_GROWL_VERSION = 1
_PACKET_TYPE_REGISTRATION = 0
_PACKET_TYPE_NOTIFICATION = 1

QUIET_MODE_INI='quiet_growl'


class SignedStructStream(object):
    def __init__(self):
        super(SignedStructStream, self).__init__()
        self._stream = StringIO()
        self._hash = md5()

    def writeBuffer(self, buff, sign=True):
        if sign:
            self._hash.update(buff)
        self._stream.write(buff)

    def sign(self):
        self.writeBuffer(self._hash.digest(), sign=False)

    def write(self, format, *data):
        packed = struct.pack(format, *data)
        self.writeBuffer(packed)

    def getvalue(self):
        return self._stream.getvalue()

    def gethash(self):
        return self._hash.digest()


def brp(application_name, notifications):
    returned = SignedStructStream()
    returned.write("b", _GROWL_VERSION)
    returned.write("b", _PACKET_TYPE_REGISTRATION)
    returned.write("!H", len(application_name))
    returned.write("bb", len(notifications), len(notifications))
    returned.writeBuffer(application_name.encode('utf-8'))
    for notification in notifications:
        returned.write("!H", len(notification))
        returned.writeBuffer(notification.encode('utf-8'))
    for i in xrange(len(notifications)):
        returned.write("b", i)
    returned.sign()
    return returned.getvalue()


def bnp(application_name, notification_name, title, message, priority, sticky):
    flags = (priority & 0x07) * 1
    returned = SignedStructStream()
    returned.write("!BBHHHHH", 1, 1, flags, len(notification_name), len(title), len(message), len(application_name),)
    for x in (notification_name, title, message, application_name):
        returned.writeBuffer(x.encode('utf-8'))
    returned.sign()
    return returned.getvalue()


def growl_fallback(message='', title='', _socket=socket.socket, _bnp=bnp, _brp=brp):
    s = _socket(socket.AF_INET, socket.SOCK_DGRAM)
    reg_packet = _brp(application_name="pytest", notifications=["Notification"])
    s.sendto(reg_packet, ("127.0.0.1", 9887))
    notification = _bnp(
        priority=4,
        message=message,
        title=title,
        notification_name="Notification",
        application_name="pytest",
        sticky=False)
    s.sendto(notification, ("127.0.0.1", 9887))
    s.close()

