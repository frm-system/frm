import socket
from logging.handlers import SysLogHandler

class SysLogHandlerWithoutBOM(SysLogHandler):

    # copy past from logging/handlers.py SysLogHandler for python 2.7
    def emit(self, record):
        """
        Emit a record.

        The record is formatted, and then sent to the syslog server. If
        exception information is present, it is NOT sent to the server.
        """
        msg = self.format(record) + '\000'
        """
        We need to convert record level to lowercase, maybe this will
        change in the future.
        """
        prio = '<%d>' % self.encodePriority(self.facility,
                                            self.mapPriority(record.levelname))
        # Message is a string. Convert to bytes as required by RFC 5424
        if type(msg) is unicode:
            msg = msg.encode('utf-8')
            # rsyslog old version doesn't support BOM_UTF8, therefore removing it
            # if codecs:
            #    msg = codecs.BOM_UTF8 + msg
        msg = prio + msg
        try:
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except socket.error:
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            elif self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            else:
                self.socket.sendall(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
