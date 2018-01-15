import bpy

idCache = {}

# set a id for the corresponding obj
def giveID(obj):
    lastId = bpy.data.worlds[0].jsonNodes.uuid
    lastId = lastId + 1
    bpy.data.worlds[0].jsonNodes.uuid = lastId
    obj.id = lastId
    idCache[lastId]=obj
    print("GAVE ID TO %s" % obj.name)
    return lastId


def getID(obj):
    if obj.id == -1:
        return giveID(obj)
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
        print("found cached nt with id %s" % id)
        return nt
    except:
        # not in map atm? retrieve and cache it
        for nodetree in array:
            if getID(nodetree) == id:
                idCache[id]=nodetree
                return nodetree
        print("Couldn't find nodetree with id: %s" % id)
    return None

def createIDHooks():
    # property hooks:
    def updateNodetreeName(self,ctx):
        print("UPDATED-Nodetreename(%s) to %s" % (self.name, type(ctx)) )
        if (self.nodetreeId!=-1):
            ctx.space_data.node_tree = utils.getNodetreeById(self.nodetreeId)
        else:
            ctx.space_data.node_tree = None
        
    def getNodetreeName(self):
       # print("get")
        if self.nodetreeId == -1:
            #print("No nodetree(%s)" % self.name)
            return ""
        
        nodetree = utils.getNodetreeById(self.nodetreeId)
        if nodetree:
            return nodetree.name
        else:
            return ""
    
    def setNodetreeName(self,value):
        if value == "":
            #print("RESETID")
            self.nodetreeId = -1
        else:
            #print("set %s=%s" % (self.name, str(value) ))
            nodetree = bpy.data.node_groups[value]
            self.nodetreeId = utils.getID(nodetree)
            #print("assigned ID %s" % getID(nodetree))    