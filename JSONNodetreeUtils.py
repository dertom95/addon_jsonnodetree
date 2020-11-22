import bpy,hashlib

idCache = {}

pcoll = None

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


## TODO: Check about the textureIDs that seemed to need buffered=True as default
def getID(obj,buffered=False):
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
        # try to get the name, as this will throw an exception when the rna-struct is kicked (for what reason...)
        name = nt.name
        #print("found cached nt with id %s" % id)
        return nt
    except:
        # not in map atm? retrieve and cache it
        for nodetree in array:
            if getID(nodetree,False) == id:
                idCache[id]=nodetree
                return nodetree
        print("Couldn't find nodetree with id: %s" % id)
    return None

def updateNodeTreeIDCache():
    print("UPDATING NodeTree IDCACHE (elements before:%s" % len(idCache) )
    idCache={}

    for nodetree in bpy.data.node_groups:
        print("%s : %s" % ( nodetree.id, nodetree.name ) )
        idCache[nodetree.id]=nodetree

    print("Elements afterwards:%s" % len(idCache) )

def overrideAutoNodetree(current_object,current_treetype,current_tree):
#    if (current_object and current_tree):
#        print("CUSTOM CHECK:%s %s %s" % (current_object.name,current_treetype,current_tree.name))
    return None

def GetAutoNodetree(space_tree_type,current_object,current_tree):
    if current_object.nodetreeName in bpy.data.node_groups:
        # node tree is known
        show_nodetree = bpy.data.node_groups[current_object.nodetreeName]
        feedback("found nodetree: %s" % current_object.nodetreeName) 
    else:
        # inconsistend data. a nodetree is referenced that is not known
        feedback("Unknown nodetree(%s) assigned to object %s" % (current_object.nodetreeName,current_object.name))    

def CreateStringHash(st,amountDigits=7):
    return int(hashlib.sha256(st.encode('utf-8')).hexdigest(), 16) % 10**amountDigits