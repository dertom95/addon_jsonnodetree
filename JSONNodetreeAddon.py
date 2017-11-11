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



import sys
import bpy
import JSONNodetree 
from bpy.types import Operator
from bpy.app.handlers import persistent

import os
path = os.path.dirname(os.path.realpath(__file__))
print("__##current_path:"+path)
sys.path.insert(0, path)
import rx
import rxUtils

rxUtils.addDisposable(rx.Observable.interval(1000).subscribe(lambda value: print("timer:"+str(value)+"/"+str(len(rxUtils.rxData.disposeables)))))

class NodeTreeCustomData(bpy.types.PropertyGroup):
    usageType = bpy.props.EnumProperty(items=[
        ('from_file','from file','Get nodetrees from static file','FILE_BLANK',0),
        ('from_runtime','from runtime','Get nodetrees dynamically from runtime','ALIGN',1)
    ])
    runtimeHost   = bpy.props.StringProperty(default="localhost");
    runtimePort = bpy.props.IntProperty(default=9595);
    path = bpy.props.StringProperty(subtype="FILE_PATH");

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

@persistent
def load_handler(dummy):
    print("Load Handler:", bpy.data.filepath)
    if (bpy.data.worlds[0].jsonNodes.path!=""):
        processNodetreeFromFile()    


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

    bpy.types.World.jsonNodes=bpy.props.PointerProperty(type=NodeTreeCustomData)
    bpy.app.handlers.load_post.append(load_handler)



def unregister():
    for clazz in classes:
        bpy.utils.unregister_class(clazz)

    rxUtils.disposeAll()

if __name__ == "__main__":
    register()
