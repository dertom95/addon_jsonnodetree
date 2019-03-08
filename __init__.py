bl_info = {
    "name": "JSON-Nodetree",
    "author": "Thomas Trocha",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
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
import JSONNodetreeUtils
from bpy.types import Operator
from bpy.app.handlers import persistent

#import JSONNodeServer

#JSONNodeServer.startServer()


def processNodetreeFromFile():
    jsonPath = bpy.data.worlds[0].jsonNodes.path
    print("LOAD NODETREEs from %s" % (jsonPath))
    jsonData = JSONNodetree.loadJSON(jsonPath)
    JSONNodetree.createNodeTrees(jsonData)		
    JSONNodetree.ntRegister()


def exportNodetree(nodetree):
    JSONNodetree.exportNodes(nodetree)

class ModalOperator(bpy.types.Operator):
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"

    def execute(self, context):
        print("This is the modal operator")
        return {'FINISHED'}

    def modal(self, context, event):
        print ("FLUSH ACTIONS")
        JSONNodetreeUtils.flushIDAssignmentBuffer()
        return {'FINISHED'}

    def invoke(self, context, event):
        print("This is the invoker")

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


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

# Export nodetrees
class ExportNodetreeOperator(bpy.types.Operator):
    ''''''
    bl_idname = "nodetree.export"
    bl_label = "export nodetrees"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = 'NODE_EDITOR'
 
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for nodetree in bpy.data.node_groups:
            exportNodetree(nodetree)

        print("FINISHED")

        return {'FINISHED'}        

## select nodetree for object
class NODE_PT_json_nodetree_select(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "JSON-Nodetree Selector"
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
            row = box.label(text="Object-Nodetree")

            row = box.row()
            row.prop_search(bpy.context.active_object,"nodetreeName",bpy.data,"node_groups",text="Nodetree")
            
        row = layout.row()
        row.prop(jsonNodes,"autoSelectObjectNodetree",text="autoselect object nodetree")


class NODE_PT_json_nodetree_file(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "JSON-Nodetree Loader"
#    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        jsonNodes = bpy.data.worlds[0].jsonNodes

        #nodetree = context.space_data.node_tree
        #print("TREE:"+str(nodetree))     
        layout = self.layout

        row = layout.row()
        row.prop(jsonNodes,"usageType")
        if (jsonNodes.usageType == "from_file"):
            layout.row().separator()
            row = layout.row()
            row.label(text="Load JSON-Trees from file")
            box = layout.box()
            row = box.row()
            row.prop(jsonNodes,"path")
            row = box.row()
            row.operator("nodetree.jsonload")
        elif (jsonNodes.usageType == "from_runtime"):
            layout.row().separator()
            row = layout.row()
            row.label(text="Load JSON-Trees from runtime")
            box = layout.box()
            row = box.row()
            row.label(text="runtime-host:")
            row = box.row()
            row.prop(jsonNodes,"runtimeHost")
            row = box.row()
            row.label(text="runtime-port:")
            row = box.row()
            row.prop(jsonNodes,"runtimePort")
            
        ## TODO: export is not finished needs have a deeeep look. not sure about the state anymore    
        ##row = layout.row()
        ##row.operator("nodetree.export")


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

classes = [
    ExportNodetreeOperator,
    LoadNodetreeOperator,
    NODE_PT_json_nodetree_file,
    NODE_PT_json_nodetree_select,
    NodeTreeCustomData,
    ModalOperator    
]

# property hooks:
def updateNodetreeName(self,ctx):
    print("UPDATED-Nodetreename(%s) self:%s  to %s" % (self.name,type(self), type(ctx)) )
    if (self.nodetreeId!=-1):
        ctx.space_data.node_tree = JSONNodetreeUtils.getNodetreeById(self.nodetreeId)
    else:
        ctx.space_data.node_tree = None
    
def getNodetreeName(self):
    print("getNodetreeName:self:%s" % type(self))
    if self.nodetreeId == -1:
        #print("No nodetree(%s)" % self.name)
        return ""
    
    nodetree = JSONNodetreeUtils.getNodetreeById(self.nodetreeId)
    if nodetree:
        return nodetree.name
    else:
        return ""

def setNodetreeName(self,value):
    print("setNodetreeName:self:%s value:%s" % (type(self),value) )
    if value == "":
        #print("RESETID")
        self.nodetreeId = -1
    else:
        #print("set %s=%s" % (self.name, str(value) ))
        nodetree = bpy.data.node_groups[value]
        self.nodetreeId = JSONNodetreeUtils.getID(nodetree)
        #print("assigned ID %s" % getID(nodetree))

def register():
    #rxUtils.disposeAll()
    try:
        unregister()
    except:
        pass

    for clazz in classes:
        bpy.utils.register_class(clazz)



    # link the json-ui config data into world object and access it via byp.data.world[0].jsonNodes
    bpy.types.World.jsonNodes=bpy.props.PointerProperty(type=NodeTreeCustomData)

    
    bpy.types.Object.nodetreeName=bpy.props.StringProperty(get=getNodetreeName,set=setNodetreeName,update=updateNodetreeName)
    bpy.types.Object.nodetreeId = bpy.props.IntProperty(default=-1)
    bpy.types.NodeTree.id = bpy.props.IntProperty(default=-1)
    bpy.types.Object.id = bpy.props.IntProperty(default=-1)
#    bpy.types.Texture.id = bpy.props.IntProperty(default=-1)
    bpy.types.Image.id = bpy.props.IntProperty(default=-1)
    
    bpy.app.handlers.load_post.append(load_handler)

    
def unregisterSelectorPanel():
    print("Try to remove the default-nodetree-selector!")
    bpy.utils.unregister_class(NODE_PT_json_nodetree_select)


def unregister():
    for clazz in classes:
        bpy.utils.unregister_class(clazz)

    del bpy.types.Object.nodetreeName
    del bpy.types.Object.nodetreeId
    del bpy.types.NodeTree.id
    del bpy.types.Object.id
    del bpy.types.Image.id
    bpy.app.handlers.load_post.remove(load_handler)
#    rxUtils.disposeAll()

if __name__ == "__main__":
    register()
