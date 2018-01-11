bl_info = {
    "name": "JSON-Nodetree",
    "author": "Thomas Trocha",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "Nodeeditor > Sidebar > Load JSON-NodeTree",
    "description": "Create nodetrees from json-files",
    "warning": "",
    "wiki_url": "",
    "category": "NodeTree",
    }

import os,sys
path = os.path.dirname(os.path.realpath(__file__))
print("__##current_path:"+path)
sys.path.insert(0, path)

import bpy
import JSONNodetree 
from bpy.types import Operator
from bpy.app.handlers import persistent


#import JSONNodeServer

#JSONNodeServer.startServer()



def processNodetreeFromFile():
    jsonPath = bpy.data.worlds[0].jsonNodes.path
    print("LOAD NODETREEs from %s" % (jsonPath))
    jsonData = JSONNodetree.loadJSON(jsonPath)
    JSONNodetree.createNodeTrees(jsonData)		
    JSONNodetree.register()


# Export startup config fo gamekit
class LoadNodetreeOperator(bpy.types.Operator):
    ''''''
    bl_idname = "nodetree.jsonload"
    bl_label = "load json-trees"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = 'NODE_EDITOR'
 
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        processNodetreeFromFile()
        print("FINISHED")

        return {'FINISHED'}    

class NODE_PT_json_nodetree(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "JSON-Nodetree"
#    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        jsonNodes = bpy.data.worlds[0].jsonNodes

        #nodetree = context.space_data.node_tree
        #print("TREE:"+str(nodetree))     
        layout = self.layout

        if bpy.context.active_object:
            box = layout.box()
            row = box.label("Object-Nodetree")

            row = box.row()
            row.prop_search(bpy.context.active_object,"nodetreeName",bpy.data,"node_groups","Nodetree")
            

        row = layout.row()
        row.prop(jsonNodes,"usageType")
        if (jsonNodes.usageType == "from_file"):
            layout.row().separator()
            row = layout.row()
            row.label("Load JSON-Trees from file")
            box = layout.box()
            row = box.row()
            row.prop(jsonNodes,"path")
            row = box.row()
            row.operator("nodetree.jsonload")
        elif (jsonNodes.usageType == "from_runtime"):
            layout.row().separator()
            row = layout.row()
            row.label("Load JSON-Trees from runtime")
            box = layout.box()
            row = box.row()
            row.label("runtime-host:")
            row = box.row()
            row.prop(jsonNodes,"runtimeHost")
            row = box.row()
            row.label("runtime-port:")
            row = box.row()
            row.prop(jsonNodes,"runtimePort")
            
        row = layout.row()
        row.prop(jsonNodes,"autoSelectObjectNodetree",text="autoselect object nodetree")

@persistent
def load_handler(dummy):
    print("Load Handler:", bpy.data.filepath)
    if (bpy.data.worlds[0].jsonNodes.path!=""):
        processNodetreeFromFile()    


# all global json-ui configuration come here 
class NodeTreeCustomData(bpy.types.PropertyGroup):
    usageType = bpy.props.EnumProperty(items=[
        ('from_file','from file','Get nodetrees from static file','FILE_BLANK',0),
        ('from_runtime','from runtime','Get nodetrees dynamically from runtime','ALIGN',1)
    ])
    runtimeHost   = bpy.props.StringProperty(default="localhost");
    runtimePort = bpy.props.IntProperty(default=9595);
    path = bpy.props.StringProperty(subtype="FILE_PATH");
    autoSelectObjectNodetree = bpy.props.BoolProperty()
    # counter for unique ids
    uuid = bpy.props.IntProperty(default=0)

idMap = {}

# set a id for the corresponding obj
def giveID(obj):
    lastId = bpy.data.worlds[0].jsonNodes.uuid
    lastId = lastId + 1
    bpy.data.worlds[0].jsonNodes.uuid = lastId
    obj.id = lastId
    idMap[lastId]=obj
    print("GAVE ID TO %s" % obj.name)
    return lastId


def getID(obj):
    if obj.id == -1:
        return giveID(obj)
    else:
        return obj.id


def getNodetreeById(id):
 #   print("getnodetree:%s" % id)
    try:
        nt = idMap[id]
        print("found cached nt with id %s" % id)
        return nt
    except:
        # not in map atm? retrieve and cache it
        for nodetree in bpy.data.node_groups:
            if getID(nodetree) == id:
                idMap[id]=nodetree
                return nodetree
        print("Couldn't find nodetree with id: %s" % id)
        
    
classes = [
    LoadNodetreeOperator,
    NODE_PT_json_nodetree,
    NodeTreeCustomData
]

def register():
    #rxUtils.disposeAll()
    try:
        unregister()
    except:
        pass
    
    for clazz in classes:
        bpy.utils.register_class(clazz)

    # property hooks:
    def updateNodetreeName(self,ctx):
        print("UPDATED-Nodetreename(%s) to %s" % (self.name, type(ctx)) )
        if (self.nodetreeId!=-1):
            ctx.space_data.node_tree = getNodetreeById(self.nodetreeId)
        else:
            ctx.space_data.node_tree = None
        
    def getNodetreeName(self):
       # print("get")
        if self.nodetreeId == -1:
            #print("No nodetree(%s)" % self.name)
            return ""
        
        nodetree = getNodetreeById(self.nodetreeId)
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
            self.nodetreeId = getID(nodetree)
            #print("assigned ID %s" % getID(nodetree))

    # link the json-ui config data into world object and access it via byp.data.world[0].jsonNodes
    bpy.types.World.jsonNodes=bpy.props.PointerProperty(type=NodeTreeCustomData)

    
    bpy.types.Object.nodetreeName=bpy.props.StringProperty(get=getNodetreeName,set=setNodetreeName,update=updateNodetreeName)
    bpy.types.Object.nodetreeId = bpy.props.IntProperty(default=-1)
    bpy.types.NodeTree.id = bpy.props.IntProperty(default=-1)
    bpy.types.Object.id = bpy.props.IntProperty(default=-1)
    
    bpy.app.handlers.load_post.append(load_handler)



def unregister():
    for clazz in classes:
        bpy.utils.unregister_class(clazz)

#    rxUtils.disposeAll()

if __name__ == "__main__":
    register()
