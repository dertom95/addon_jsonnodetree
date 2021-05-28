import bpy,hashlib

idCache = {}

pcoll = None

class Data:
    pass

class NodeTreeInstance(bpy.types.PropertyGroup):
    instance_object : bpy.props.PointerProperty(type=bpy.types.Object)

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

def TreeCheckForExposedValues(tree):
    for node in tree.nodes:
        for prop_name in node.propNames:
            if eval("node.nodeData.%s_expose" % prop_name):
                tree.has_exposed_values=True
                return

    tree.has_exposed_values=False

def TreeEnsureInstanceForNode(node,obj,create=True):
    # iterate over instance data and check if there is an instance for this obj already
    data = None

    for inst_data in node.instance_data:
        if inst_data and inst_data.instance_object==obj:
            data = inst_data
            break
    if not data and create:
        data = node.instance_data.add()
        data.instance_object = obj
        data.instance_tree = node.id_data
        for prop_name in node.propNames:
            exec("data.%s_expose=False" % prop_name)

    return data


def TreeRemoveInstanceFromNode(node,obj):
    for i,inst_data in enumerate(node.instance_data):
        if inst_data and inst_data.instance_object==obj:
            node.instance_data.remove(i)
            return True

    return False


def TreeAddInstanceToTree(tree,obj):
    # iterate over instances and ensure the object is added if not already present
    found = TreeHasInstanceForObject(tree,obj)

    if not found:
        # tell the tree what objects have instances on this nodetree
        new_instance = tree.instances.add()
        new_instance.instance_object=obj
    
    # now make sure all nodes have instance-data for this obj
    for node in tree.nodes:
#        if node.exposeData:
        TreeEnsureInstanceForNode(node,obj)


def TreeRemoveInstanceFromTree(tree,obj,force=False):
    # iterate over instances and ensure the object is added if not already present
    found=False

    for i,inst in enumerate(tree.instances):
        if inst.instance_object and inst.instance_object==obj:
            tree.instances.remove(i)
            found=True
            break

    if not found and not force:
        return

    # now make sure all nodes have instance-data for this obj
    for node in tree.nodes:
        TreeRemoveInstanceFromNode(node,obj)

def TreeHasInstanceForObject(tree,obj):
    for inst in tree.instances:
        if inst.instance_object and inst.instance_object==obj:
            return True

    return False

def TreeResetValueForInstanceProperty(tree,obj,param_name,search_expose_name):
    for node in tree.nodes:
        try:
            expose_name = eval("node.nodeData.%s_exposename"%param_name)
            if expose_name == search_expose_name:
                inst_data = TreeEnsureInstanceForNode(node,obj)
                if not inst_data:
                    # error. no instance data?
                    return
                value = eval("node.nodeData.%s" % param_name)
                exec("inst_data.%s=value" % param_name)
                exec("inst_data.%s_expose=False" % param_name)
                exec("inst_data.%s_exposename=expose_name" % param_name)
                exec("inst_data.%s_exposename_last=expose_name" % param_name)
        except:
            pass

def TreeUpdateExposedNames(tree,update_prop_name=""):
    update_all = update_prop_name==""
    for node in tree.nodes:
        if not node.exposeData:
            continue

        for prop_name in node.propNames:
            if not (update_all or prop_name == update_prop_name):
                continue
            
            is_exposed = eval("node.nodeData.%s_expose" % prop_name)
            if not is_exposed:
                continue
                
            expose_name = eval("node.nodeData.%s_exposename" % prop_name)
            for inst in node.instance_data:
                exec("inst.%s_exposename=expose_name" % prop_name)
                exec("inst.%s_exposename_last=expose_name" % prop_name)




# def TreeEnsureInstanceForAllObjects():
#     for obj in bpy.data.objects:
#         if obj:
#             for nt in obj.nodetrees:


