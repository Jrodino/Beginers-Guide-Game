import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject


class World(DirectObject):
    def __init__(self):
        base.disableMouse()
        self.speed = 0
        self.throttle = 0
        self.maxSpeed = 200
        self.accel = 40
        self.handling = 20
        base.setBackgroundColor(0,0,0)
        self.track = loader.loadModel('Models/Grass/mount.blend1.egg')
        self.track.reparentTo(render)
        self.track.setScale(10)
        self.track.setPos(0, 0, -15)
        self.KeyMap = {"w": False,
                       "s": False,
                       "a": False,
                       "d": False,
                       "mouse1": False,
                       "mouse3": False}
        self.drone = loader.loadModel('Models/Drone/sad_drone.egg')
        self.drone.reparentTo(render)
        self.drone.setPos(0, 5, -.5)
        self.drone.setScale(0.2)
        base.camera.reparentTo(self.drone)
        base.camera.setY(base.camera, -20)
        base.camera.setZ(base.camera, 5)
        base.camera.setP(base.camera, -10)
        self.distTrav = 0
        taskMgr.add(self.droneControl, 'Drone Control')
        taskMgr.doMethodLater(1, self.debugTask, 'Debug Task')
        taskMgr.add(self.DroneReset, 'Reset Drone')
        self.accept("h", self.Hello)
        self.accept("w", self.setKey, ["w", True])
        self.accept("s", self.setKey, ["s", True])
        self.accept("a", self.setKey, ["a", True])
        self.accept("d", self.setKey, ["d", True])
        self.accept("q", self.setKey, ["q", True])
        self.accept("e", self.setKey, ["e", True])
        self.accept("mouse1", self.setKey, ["mouse1", True])
        self.accept("mouse3", self.setKey, ["mouse3", True])
        self.accept("w-up", self.setKey, ["w", False])
        self.accept("s-up", self.setKey, ["s", False])
        self.accept("a-up", self.setKey, ["a", False])
        self.accept("d-up", self.setKey, ["d", False])
        self.accept("q-up", self.setKey, ["q", False])
        self.accept("e-up", self.setKey, ["e", False])
        self.accept("mouse1-up", self.setKey, ["mouse1", False])
        self.accept("mouse3-up", self.setKey, ["mouse3", False])

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
        self.speedCheck(dt)
        self.move(dt)
        return task.cont

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
