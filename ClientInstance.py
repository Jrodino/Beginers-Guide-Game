from NetClasses import *
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject

class ClientI(DirectObject):
    def __init__(self):
        self.setupClient()

    def setupClient(self):

        client = Client(ClientProtocol())
        client.connect("localhost" , 9999, 3000)
        client.start()
w = ClientI()
base.run()