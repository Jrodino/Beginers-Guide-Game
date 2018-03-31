from panda3d.core import *

class NetworkHandler():

    def __init__(self):
        taskMgr.add(self.updateInput, "update network input")

    def updateInput(self, task):
        #self.dispatchMessages()

        return task.cont
