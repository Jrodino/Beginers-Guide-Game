import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from panda3d.core import *
import random
from random import choice

class NetCommon:
    def __init__(self, protocol):
        self.manager = ConnectionManager()
        self.reader = QueuedConnectionReader(self.manager, 0)
        self.writer = ConnectionWriter(self.manager, 0)
        self.protocol = protocol
        taskMgr.add(self.updateReader, "updateReader")

    def updateReader(self, task):
        if self.reader.dataAvailable():
            data = NetDatagram()
            self.reader.getData(data)
            reply = self.protocol.process(data)

            if reply != None:
                self.writer.send(reply, data.getConnection())

        return task.cont


class Server(NetCommon):
    def __init__(self, protocol, port):
        NetCommon.__init__(self, protocol)
        self.listener = QueuedConnectionListener(self.manager, 0)
        socket = self.manager.openTCPServerRendezvous(port, 100)
        self.listener.addConnection(socket)
        self.connections = []

        self.smiley = ServerSmiley()
        self.frowney = loader.loadModel("Models/MartinBall.egg")
        self.frowney.reparentTo(render)

        taskMgr.add(self.updateListener, 'updateListener')
        taskMgr.add(self.updateSmiley, "updateSmiley")
        taskMgr.doMethodLater(0.1, self.syncSmiley, "syncSmiley")

    def updateSmiley(self, task):
        self.smiley.update()
        self.frowney.setPos(self.smiley.pos)
        return task.cont

    def syncSmiley(self, task):
        sync = PyDatagram()
        sync.addFloat32(self.smiley.vel)
        sync.addFloat32(self.smiley.pos.getZ())
        self.broadcast(sync)
        return task.again

    def broadcast(self, datagram):
        for conn in self.connections:
            self.writer.send(datagram, conn)

    def updateListener(self, task):
        if self.listener.newConnectionAvailable():
            connection = PointerToConnection()
            if self.listener.getNewConnection(connection):
                connection = connection.p()
                self.connections.append(connection)
                self.reader.addConnection(connection)
                print "Server: New connection established."

        return task.cont


class Client(NetCommon):
    def __init__(self, protocol):
        NetCommon.__init__(self, protocol)

    def connect(self, host, port, timeout):
        self.connection = self.manager.openTCPClientConnection(host, port, timeout)
        if self.connection:
            self.reader.addConnection(self.connection)
            print "Client: Connected to server."

    def send(self, datagram):
        if self.connection:
            self.writer.send(datagram, self.connection)


class Protocol:
    def printMessage(self, title, msg):
        print "%s %s" % (title, msg)

    def buildReply(self, msgid, data):
        reply = PyDatagram()
        reply.addUint8(msgid)
        reply.addString(data)
        return reply

    def process(self, data):
        return None


class ServerProtocol(Protocol):
    def process(self, data):
        it = PyDatagramIterator(data)
        msgid = it.getUint8()

        if msgid == 0:
            return self.handleHello(it)
        elif msgid == 1:
            return self.handleQuestion(it)
        elif msgid == 2:
            return self.handleBye(it)

    def handleHello(self, it):
        self.printMessage("Server received:", it.getString())
        return self.buildReply(0, "Hello, too!")

    def handleQuestion(self, it):
        self.printMessage("Server received:", it.getString())
        return self.buildReply(1, "I'm fine. How are you?")

    def handleBye(self, it):
        self.printMessage("Server received:", it.getString())
        return self.buildReply(2, "Bye!")


class ClientProtocol(Protocol):
    def process(self, data):
        it = PyDatagramIterator(data)
        msgid = it.getUint8()

        if msgid == 0:
            return self.handleHello(it)
        elif msgid == 1:
            return self.handleQuestion(it)
        elif msgid == 2:
            return self.handleBye(it)


class ClientProtocol2(Protocol):
    def __init__(self, smiley):
        self.smiley = smiley

    def process(self, data):
        it = PyDatagramIterator(data)
        vel = it.getFloat32()
        z = it.getFloat32()
        diff = z - self.smiley.getZ()
        self.smiley.setPythonTag("velocity", vel + diff * 0.03)
        return None


class ServerSmiley:
    def __init__(self):
        self.pos = Vec3(0, 0, 30)
        self.vel = 0

    def update(self):
        z = self.pos.getZ()
        if z <= 0:
            self.vel = random.uniform(0.1, 0.8)
        self.pos.setZ(z + self.vel)
        self.vel -= 0.01