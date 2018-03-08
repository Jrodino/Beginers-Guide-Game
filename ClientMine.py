from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionReader
from direct.showbase.DirectObject import DirectObject

class ClientMine(DirectObject):
    def __init__(self):

        self.port_address = 9099  # same for client and server

        # a valid server URL. You can also use a DNS name
        # if the server has one, such as "localhost" or "panda3d.org"
        self.ip_address = "localhost"

        # how long until we give up trying to reach the server?
        self.timeout_in_miliseconds = 3000  # 3 seconds
        taskMgr.add(self.connect, 'connection')
        print 'done'

    def connect(self, Task):
        self.myConnection = self.cManager.openTCPClientConnection(self.ip_address, self.port_address, self.timeout_in_miliseconds)
        if myConnection:
            self.cReader.addConnection(self.myConnection)  # receive messages from server
        Task.cont