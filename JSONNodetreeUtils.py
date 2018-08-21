import bpy

idCache = {}

class Data:
    pass


initialized = False

def init():
    global initialized

    if (hasattr(Data,"actionCTX")):
        return

    print("##init##")

    class ActionContext:
        def getID(self):
            return self.uuid

        initialized = False
        actions = []
        waitingObjects = {}
        uuid = bpy.data.worlds[0].jsonNodes.uuid

    Data.actionCTX = ActionContext()
    print("ADDED ACTIONCTX TO DATA")

def addIDAction(obj,_id):
    print("ADD ACTION")
    if not initialized:
        init()

    def doit():
        print("Assign %s.id=%s" % (obj,_id))
        obj.id=_id

    Data.actionCTX.actions.append(doit)
    Data.actionCTX.waitingObjects[obj]=_id


def modalStarter(self,ctx):
    bpy.ops.object.modal_operator('INVOKE_DEFAULT')

# set a id for the corresponding obj
def giveID(obj,buffered):
    if not initialized:
        init()

    if buffered:
        lastId = Data.actionCTX.getID()
        lastId = lastId + 1
        print ("LASTID:%s" % lastId)
        Data.actionCTX.uuid = lastId
        addIDAction(obj,lastId)
    else:
        lastId = bpy.data.worlds[0].jsonNodes.uuid
        lastId = lastId + 1
        bpy.data.worlds[0].jsonNodes.uuid = lastId
        obj.id = lastId
    idCache[lastId]=obj
    print("GAVE ID TO %s" % lastId)
    return lastId

def flushIDAssignmentBuffer():
    init()

    bpy.data.worlds[0].jsonNodes.uuid=Data.actionCTX.uuid

    for act in Data.actionCTX.actions:
        print("CALL START")
        act()
        print("CALL ENDäääääääääääääääääääääääää")
    Data.actionCTX.actions = []
    Data.actionCTX.waitingObjects={}


def getID(obj,buffered=True):
    if obj.id == -1:
        if buffered and hasattr(Data,"actionCTX") and obj in Data.actionCTX.waitingObjects:
            return Data.actionCTX.waitingObjects[obj]
        else:
            return giveID(obj,buffered)
    else:
        return obj.id


def getNodetreeById(id):
    return getById(bpy.data.node_groups,id)

def getTextureById(id):
    return getById(bpy.data.textures,id)

def getObjectById(id):
    return getById(bpy.data.objects,id)

def getById(array,id):
    if id == -1 or array==None:
        return None

    try:
        nt = idCache[id]
        #print("found cached nt with id %s" % id)
        return nt
    except:
        # not in map atm? retrieve and cache it
        for nodetree in array:
            if getID(nodetree) == id:
                idCache[id]=nodetree
                return nodetree
        print("Couldn't find nodetree with id: %s" % id)
    return None
