import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from panda3d.core import *
import random
from direct.actor.Actor import Actor
from panda3d.core import *
from NetworkHandler import NetworkHandler
from NetClasses import Server, Client, ServerProtocol, ClientProtocol

class World(DirectObject):

    def __init__(self):
        base.disableMouse()

        self.smiley = loader.loadModel("Models/MartinBall.egg")
        self.smiley.setPythonTag("velocity", 0)
        self.smiley.reparentTo(render)
        self.smiley.setPos(0, 0, 30)

        self.speed = 0
        self.throttle = 0
        self.maxSpeed = 400
        self.accel = 80
        self.handling = 40
        self.height = 0
        base.setBackgroundColor(0, 0, 0)
        self.track = loader.loadModel('Models/Grass/world.bam')
        self.track.reparentTo(render)
        self.track.setPos(0, 0, -50)
        self.KeyMap = {"w": False,
                       "s": False,
                       "a": False,
                       "d": False,
                       "mouse1": False,
                       "mouse3": False,
                       "r": False,
                       "f": False,
                       "g": False}
        self.drone = loader.loadModel('Models/Drone/sad_drone.egg')
        self.drone.reparentTo(render)
        self.drone.setPos(40, 40, 10)
        self.drone.setScale(0.2)
        base.camera.reparentTo(self.drone)
        base.camera.setY(base.camera, -20)
        base.camera.setZ(base.camera, 5)
        base.camera.setP(base.camera, -10)
        self.distTrav = 0
        taskMgr.add(self.droneControl, 'Drone Control')
        #taskMgr.doMethodLater(5, self.debugTask, 'Debug Task')
        taskMgr.add(self.DroneReset, 'Reset Drone')
        taskMgr.add(self.updateSmiley, "updateSmiley")

        self.setupNetInput()
        self.setupNetwork()

        self.accept("h", self.Hello)
        self.accept("w", self.setKey, ["w", True])
        self.accept("s", self.setKey, ["s", True])
        self.accept("a", self.setKey, ["a", True])
        self.accept("d", self.setKey, ["d", True])
        self.accept("r", self.setKey, ["r", True])
        self.accept("f", self.setKey, ["f", True])
        self.accept("mouse1", self.setKey, ["mouse1", True])
        self.accept("mouse3", self.setKey, ["mouse3", True])
        self.accept("w-up", self.setKey, ["w", False])
        self.accept("s-up", self.setKey, ["s", False])
        self.accept("a-up", self.setKey, ["a", False])
        self.accept("d-up", self.setKey, ["d", False])
        self.accept("r-up", self.setKey, ["r", False])
        self.accept("f-up", self.setKey, ["f", False])
        self.accept("mouse1-up", self.setKey, ["mouse1", False])
        self.accept("mouse3-up", self.setKey, ["mouse3", False])
        self.accept("g", self.setKey, ["g", True])
        self.accept("g-up", self.setKey, ["g", False])



    def updateSmiley(self, task):
        vel = self.smiley.getPythonTag("velocity")
        z = self.smiley.getZ()

        if z <= 0:
            vel = random.uniform(0.1, 0.8)
        self.smiley.setZ(z + vel)
        vel -= 0.01
        self.smiley.setPythonTag("velocity", vel)
        return task.cont

    def setKey(self, key, value):
        self.KeyMap[key] = value

    def Hello(self):
        print "hello World"

    def droneControl(self, task):
        dt = globalClock.getDt()
        if dt > .2:
            return task.cont
        if self.KeyMap["w"] is True:
            self.adjustTrhottle("up", dt)
        elif self.KeyMap["s"] is True:
            self.adjustTrhottle("down", dt)
        if self.KeyMap["d"] is True:
            self.turn("r", dt)
        elif self.KeyMap["a"] is True:
            self.turn("l", dt)
        if self.KeyMap["mouse1"] is True:
            self.cameraZoom("in", dt)
        elif self.KeyMap["mouse3"] is True:
            self.cameraZoom("out", dt)
        if self.KeyMap["r"] is True:
            self.adjustHeight("up", dt)
        elif self.KeyMap["f"] is True:
            self.adjustHeight("down", dt)

        self.speedCheck(dt)
        self.move(dt)
        return task.cont
    def setupNetInput(self):
        dt = globalClock.getDt()
        self.accept("net-fly-start", self.setKey, ["w", True])
        self.accept("net-fly-stop", self.setKey, ["s", True])
        self.accept("net-turn-left", self.setKey, ["a", True])
        self.accept("net-turn-right", self.setKey, ["d", True])

    def setupNetwork(self):
        server = Server(ServerProtocol(), 9999)
        client = Client(ClientProtocol())
        client.connect("localhost", 9999, 3000)
        client.start()

    def cameraZoom(self, dir, dt):
        if dir == "in":
            base.camera.setY(base.camera, 10 * dt)
        else:
            base.camera.setY(base.camera, -10 * dt)

    def turn(self, dir, dt):
        turnRate = self.handling * (2 - (self.speed / self.maxSpeed))
        if dir == "r":
            turnRate = -turnRate
            self.drone.setH(self.drone, turnRate * dt)
        elif dir == "l":
            self.drone.setH(self.drone, turnRate * dt)

    def adjustHeight(self, dir, dt):
        if dir == "up":
            self.drone.setZ(self.drone, .5)
        elif dir == "down":
            self.drone.setZ(self.drone, -.5)

    def adjustTrhottle(self, dir, dt):
        if dir == "up":
            self.throttle += .25 * dt
            if self.throttle > 1:
                self.throttle = 1
        else:
            self.throttle -= .25 * dt
            if self.throttle < -1:
                self.throttle = -1

    def DroneReset(self, task):
        if self.distTrav >= 40:
            self.drone.setPos(-2, 2, 0)
            self.distTrav = 0
            return task.cont
        else:
            return task.cont

    def debugTask(self, task):
        print taskMgr
        print self.distTrav
        return task.again

    def speedCheck(self, dt):
        tSetting = (self.maxSpeed * self.throttle)
        if self.speed < tSetting:
            if (self.speed + (self.accel * dt)) > tSetting:
                self.speed = tSetting
            else:
                self.speed += (self.accel * dt)
        elif self.speed > tSetting:
            if (self.speed - (self.accel * dt)) < tSetting:
                self.speed = tSetting
            else:
                self.speed -= (self.accel * dt)

    def move(self, dt):
        mps = self.speed * 1000 / 3600
        self.drone.setY(self.drone, mps * dt)


w = World()
base.run()
