from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from direct.showbase.DirectObject import DirectObject
from panda3d.core import PointerToConnection
from panda3d.core import NetAddress
from panda3d.core import NetDatagram
from direct.distributed.PyDatagram import PyDatagram
import direct.directbase.DirectStart


class ServerMine(DirectObject):

    def __init__(self):
        self.startConectionManager()
        self.port_address = 9099  # No-other TCP/IP services are using this port
        self.backlog = 1000  # If we ignore 1,000 connection attempts, something is wrong!
        self.tcpSocket = self.cManager.openTCPServerRendezvous(self.port_address, self.backlog)
        self.PRINT_MESSAGE = 1

        #The tasks poll data listened and conection reader

        taskMgr.add(self.tskListenerPolling, "Poll the connection listener", -39)
        taskMgr.add(self.tskReaderPolling, "Poll the connection reader", -40)
        #taskMgr.add(self.debugTask, 'Debug Task')

        self.cListener.addConnection(self.tcpSocket)
        self.sendAnswer()

    def debugTask(self, task):
        print taskMgr
        return task.cont

    def myNewPyDatagram(self):
        # Send a test message
        self.myPyDatagram = PyDatagram()
        self.myPyDatagram.addUint8(self.PRINT_MESSAGE)
        self.myPyDatagram.addString("Hello, world!")
        return self.myPyDatagram
    def terminateConnection(self):
        # terminate connection to all clients

        for aClient in activeConnections:
            cReader.removeConnection(aClient)
        self.activeConnections = []

        # close down our listener
        cManager.closeConnection(tcpSocket)


    # broadcast a message to all clients
    def sendAnswer(self):
        self.myPyDatagram = self.myNewPyDatagram()  # build a datagram to send
        for self.aClient in self.activeConnections:
            cWriter.send(myPyDatagram, aClient)

    def startConectionManager(self):
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)

        self.activeConnections = []  # We'll want to keep track of these later


    def tskListenerPolling(self, Task):
        if self.cListener.newConnectionAvailable():

            self.rendezvous = PointerToConnection()
            self.netAddress = NetAddress()
            self.newConnection = PointerToConnection()

            if self.cListener.getNewConnection(self.rendezvous, self.netAddress, self.newConnection):
                self.newConnection = self.newConnection.p()
                self.activeConnections.append(self.newConnection)  # Remember connection
                self.cReader.addConnection(self.newConnection)  # Begin reading connection
        return Task.cont

    def myProcessDataFunction(netDatagram):
        myIterator = PyDatagramIterator(netDatagram)
        msgID = myIterator.getUint8()
        if msgID == PRINT_MESSAGE:
            messageToPrint = myIterator.getString()
            print messageToPrint

    def tskReaderPolling(self, Task):
      if self.cReader.dataAvailable():
        datagram = NetDatagram()  # catch the incoming data in this instance
        # Check the return value; if we were threaded, someone else could have
        # snagged this data before we did
        if self.cReader.getData(datagram):
          self.myProcessDataFunction(datagram)
      return Task.cont


w = ServerMine()
run()