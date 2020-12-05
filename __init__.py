# Image/Icon-Preview https://docs.blender.org/api/blender2.8/bpy.utils.previews.html?highlight=preview#module-bpy.utils.previews
# UI-Layout 2.8: https://docs.blender.org/api/blender2.8/bpy.types.UILayout.html?highlight=uilayout
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


import os,sys,traceback
import json
path = os.path.dirname(os.path.realpath(__file__))
print("__##current_path:"+path)
sys.path.insert(0, path)

import base64
import bpy
import JSONNodetree 
import JSONNodetreeUtils
from bpy.types import Operator
from bpy.app.handlers import persistent

#import JSONNodeServer

#JSONNodeServer.startServer()

preview_collections = {}


def processNodetreeFromFile():
    if "main" in preview_collections:
        preview_collections["main"].clear()

    jsonData = None
    jsonPath = bpy.data.worlds[0].jsonNodes.path
    if jsonPath:
        print("LOAD NODETREEs from %s" % (jsonPath))
        jsonData = JSONNodetree.loadJSON(jsonPath)

    jsonPath2 = bpy.data.worlds[0].jsonNodes.path2
    if jsonPath2:
        jsonData2 = JSONNodetree.loadJSON(jsonPath2)

        if jsonData:
            print("merge json-data")
            for nodetree in jsonData2["trees"]:
                # TODO merge trees of same type?
                jsonData["trees"].append(nodetree)
            
            
            
            # for nodetree in jsonData2["trees"]:
            #     idx = 0
            #     for current in jsonData["trees"]:
            #         if current["id"]==nodetree["id"]:
            #             print("REPLACE NODETREE with id: %s" % nodetree["id"])
            #             jsonData["trees"][idx] = nodetree
            #             break
                    
        else:
            jsonData = jsonData2
        
    customUIFile = bpy.data.worlds[0].jsonNodes.customUIFile
    print(";;;;;;;;;;;;;;; customUIFile")
    if customUIFile:
        file = open(customUIFile,"r")
        result = file.read()
        b64encoded = base64.b64encode(result.encode('ascii')) # the nodetree expects customUIs to be store in base64-format
        
        jsonData["customUI"]=[b64encoded]


    JSONNodetree.createNodeTrees(jsonData)

    


    JSONNodetree.ntRegister()


def exportScene(scene):
    return JSONNodetree.exportScene(scene)

def exportNodetree(nodetree,onlyValueDifferentFromDefault=False):
    return JSONNodetree.exportNodes(nodetree,onlyValueDifferentFromDefault)

# class ModalOperator(bpy.types.Operator):
#     bl_idname = "object.modal_operator"
#     bl_label = "Simple Modal Operator"

#     def execute(self, context):
#         print("This is the modal operator")
#         return {'FINISHED'}

#     def modal(self, context, event):
#         print ("FLUSH ACTIONS")
#         JSONNodetreeUtils.flushIDAssignmentBuffer()
#         return {'FINISHED'}

#     def invoke(self, context, event):
#         print("This is the invoker")

#         context.window_manager.modal_handler_add(self)
#         return {'RUNNING_MODAL'}

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

class ShowJsonNodetreeOptions(bpy.types.Operator):
    ''''''
    bl_idname = "nodetree.full_jsonnodetree"
    bl_label = "Show all JSON-Nodetree-Options"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = 'NODE_EDITOR'
 
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        jsonNodes = bpy.data.worlds[0].jsonNodes
        jsonNodes.show_export_panel=True
        jsonNodes.show_auto_select=True
        jsonNodes.show_custom_ui_field=True
        jsonNodes.show_developer=True
        jsonNodes.show_object_export=True
        jsonNodes.show_object_mapping=True
        return {'FINISHED'} 


# Export nodetrees
class ExportNodetreeOperator(bpy.types.Operator):
    ''''''
    bl_idname = "nodetree.export"
    bl_label = "export nodetrees as JSON"
    bl_options = {'REGISTER', 'UNDO'}
    bl_space_type = 'NODE_EDITOR'
 
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for nodetree in bpy.data.node_groups:
            tree = exportNodetree(nodetree,False)
            print("TREE:%s" % tree)
            result = json.dumps(tree, ensure_ascii=False, sort_keys=True, indent=4)
            print(result)
            WriteFile(result,bpy.data.worlds[0].jsonNodes.exportPath+"/nt_"+tree["name"]+".json")            

        for scene in bpy.data.scenes:
            sceneExport = exportScene(scene)
            result = json.dumps(sceneExport, ensure_ascii=False, sort_keys=True, indent=4)
            WriteFile(result,bpy.data.worlds[0].jsonNodes.exportPath+"/scene_"+scene.name+".json")     

        print("FINISHED")

        return {'FINISHED'}        


def DeActivatePath2Timer():
    try:
        jsonNodes = bpy.data.worlds[0].jsonNodes

        if jsonNodes.path_autoreload or jsonNodes.path2_autoreload:
            if not bpy.app.timers.is_registered(checkFileChange):
                bpy.app.timers.register(checkFileChange,first_interval=0, persistent=True)
        else:
            if bpy.app.timers.is_registered(checkFileChange):
                bpy.app.timers.unregister(checkFileChange)

        #print("Timers activated!")
    except Exception as e:
        print("Could not activate timers,yet (%s)" % e)
        return        


def drawJSONFileSettings(self, context):
    jsonNodes = bpy.data.worlds[0].jsonNodes

    #nodetree = context.space_data.node_tree
    #print("TREE:"+str(nodetree))     
    layout = self.layout

    row = layout.row()
    #row.prop(jsonNodes,"usageType")
    if (jsonNodes.usageType == "from_file"):
        layout.row().separator()
        row = layout.row()
        row.label(text="Load JSON-Trees from file")
        box = layout.box()
        row = box.row()
        row.prop(jsonNodes,"path",text=jsonNodes.path_ui_name)
        row.prop(jsonNodes,"path_autoreload",text="")
        row = box.row()
        row.prop(jsonNodes,"path2",text=jsonNodes.path2_ui_name) 
        row.prop(jsonNodes,"path2_autoreload",text="")

        DeActivatePath2Timer()

        if jsonNodes.show_custom_ui_field:
            row = box.row()
            row.prop(jsonNodes,"customUIFile")

        row = box.row()
        row.operator("nodetree.jsonload",text=jsonNodes.load_trees_button_name)

        jsonNodes = bpy.data.worlds[0].jsonNodes

        #nodetree = context.space_data.node_tree
        #print("TREE:"+str(nodetree))     
        layout = self.layout

        if jsonNodes.show_object_mapping:
            if bpy.context.active_object:
                box = layout.box()
                row = box.label(text="Object-Nodetree")

                row = box.row()
                row.prop(bpy.context.active_object,"nodetree",text="Nodetree")
            
        if jsonNodes.show_auto_select:
            row = layout.row()
            row.prop(jsonNodes,"autoSelectObjectNodetree",text="autoselect object nodetree")

        if jsonNodes.show_developer:
            row = layout.row()
            
            #row.prop(jsonNodes,"automaticFakeuser",text="automatic set fake user to assigned nodetrees")        
            
            box = layout.row().box()
            row = box.row()
            row.label(text="For developers:")
            row = box.row()
            row.prop(jsonNodes,"outputHooks",text="output called hooks on stdout")


        
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
    if jsonNodes.show_export_panel:
        box = layout.box()
        row = box.row()
        row.prop(jsonNodes,"exportPath")
        row = box.row()
        row.operator("nodetree.export")

    if not jsonNodes.show_export_panel and "addon_jsonnodetree" in bpy.context.preferences.addons.keys():
        box = layout.box()
        row = box.row()
        row.operator("nodetree.full_jsonnodetree")



class NODE_PT_json_nodetree_file(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "JSON-Nodetree Loader"
    bl_category = "JSON-Nodes"

#    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        drawJSONFileSettings(self,context)

class IV_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        drawJSONFileSettings(self,context)

@persistent
def load_handler(dummy):
    print("Load Handler:", bpy.data.filepath)
    if (bpy.data.worlds[0].jsonNodes.path!="" or bpy.data.worlds[0].jsonNodes.path2!=""):
        processNodetreeFromFile()    


# all global json-ui configuration come here 
class NodeTreeCustomData(bpy.types.PropertyGroup):
    usageType : bpy.props.EnumProperty(items=[
        ('from_file','from file','Get nodetrees from static file','FILE_BLANK',0),
        ('from_runtime','from runtime','Get nodetrees dynamically from runtime','ALIGN',1)
    ])
    runtimeHost   : bpy.props.StringProperty(default="localhost")
    runtimePort : bpy.props.IntProperty(default=9595)
    path : bpy.props.StringProperty(subtype="FILE_PATH")
    path_autoreload : bpy.props.BoolProperty(default=True,description="autoreload on change")
    path_lastmodified : bpy.props.IntProperty()
    path_ui_name : bpy.props.StringProperty(default="Path")


    path2 : bpy.props.StringProperty(subtype="FILE_PATH")
    path2_autoreload : bpy.props.BoolProperty(default=True,description="autoreload on change")
    path2_lastmodified : bpy.props.IntProperty()
    path2_ui_name : bpy.props.StringProperty(default="Path2")

    load_trees_button_name : bpy.props.StringProperty(default="load json-trees")

    show_custom_ui_field : bpy.props.BoolProperty(default=True)
    show_export_panel : bpy.props.BoolProperty(default=True)
    show_object_export : bpy.props.BoolProperty(default=True)
    show_developer : bpy.props.BoolProperty(default=True)
    show_object_mapping: bpy.props.BoolProperty(default=True)
    show_auto_select: bpy.props.BoolProperty(default=True)

    exportPath: bpy.props.StringProperty(subtype="FILE_PATH")
    autoSelectObjectNodetree : bpy.props.BoolProperty()
    # counter for unique ids
    uuid : bpy.props.IntProperty(default=0)
    #automaticFakeuser : bpy.props.BoolProperty(default=True,description="add a fakeuser to the nodetrees that get assigned")
    outputHooks : bpy.props.BoolProperty(default=False,description="FOR DEVELOPERS: output the hooks/callbacks tried to be called for overriding ui and behaviour")
    customUIFile : bpy.props.StringProperty(subtype="FILE_PATH")





def WriteFile(data, filepath):
    try:
        file = open(filepath, "w")
    except Exception as e:
        print("Cannot open file %s %s" % (filepath, e))
        return
    try:
        file.write(data)
    except Exception as e:
        print("Cannot write to file %s %s" % (filepath, e))
    file.close()

# property hooks:
# def updateNodetreeName(self,ctx):
#     print("UPDATED-Nodetreename(%s) self:%s  to %s" % (self.name,type(self), type(ctx)) )
#     if (self.nodetreeId!=-1):
#         ctx.space_data.node_tree = JSONNodetreeUtils.getNodetreeById(self.nodetreeId)
#     else:
#         ctx.space_data.node_tree = None
    
# def getNodetreeName(self):
#     #print("getNodetreeName:self:%s" % type(self))
#     if self.nodetreeId == -1:
#         #print("No nodetree(%s)" % self.name)
#         return ""
    
#     nodetree = JSONNodetreeUtils.getNodetreeById(self.nodetreeId)
#     if nodetree:
#         return nodetree.name
#     else:
#         return ""

# def setNodetreeName(self,value):
#     print("setNodetreeName:self:%s value:%s" % (type(self),value) )
#     if value == "":
#         #print("RESETID")
#         self.nodetreeId = -1
#     else:
#         #print("set %s=%s" % (self.name, str(value) ))
#         nodetree = bpy.data.node_groups[value]
#         self.nodetreeId = JSONNodetreeUtils.getID(nodetree)
#         if bpy.data.worlds[0].jsonNodes.automaticFakeuser:
#             nodetree.use_fake_user=True
#         #print("assigned ID %s" % getID(nodetree))



# We can store multiple preview collections here,
# however in this example we only store "main"
# check if path2 should be checked for mods
if 'checkFileChange' not in globals():
    print("ACTIVATE CHECKFILECHANGE")
    def checkFileChange():
        #print("--check filechange--")
        jsonNodes = bpy.data.worlds[0].jsonNodes

        reload = False
        if jsonNodes.path_autoreload and jsonNodes.path and os.path.exists(jsonNodes.path):
            fileModifiedTime = os.stat(jsonNodes.path)[8]

            if fileModifiedTime != jsonNodes.path_lastmodified:
                jsonNodes.path_lastmodified = fileModifiedTime
                reload = True

        if jsonNodes.path2_autoreload and jsonNodes.path2 and os.path.exists(jsonNodes.path2):
            fileModifiedTime = os.stat(jsonNodes.path2)[8]

            if fileModifiedTime != jsonNodes.path2_lastmodified:
                jsonNodes.path2_lastmodified = fileModifiedTime
                reload = True

        if reload:
            bpy.ops.nodetree.jsonload()

        
        return 2.0
        
classes = [
    ExportNodetreeOperator,
    LoadNodetreeOperator,
    NodeTreeCustomData,
    #ModalOperator,
    IV_Preferences,
    ShowJsonNodetreeOptions
]

classes_ui = [
    NODE_PT_json_nodetree_file,
]

def register():
    json_nodetree_register()



    for clazz in classes_ui:
        try:
            bpy.utils.register_class(clazz)
        except:
            print("Unexpected error in jsonnodetree_register_ui:%s" % traceback.format_exc())

def json_nodetree_register():
    global classes,classes_ui

    # install logic (without UI)

    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    import bpy.utils.previews
    JSONNodetreeUtils.pcoll = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    #my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")


    if not "main" in preview_collections:
        preview_collections["main"] = JSONNodetreeUtils.pcoll
    else:
        preview_collections["main"].clear()

    for clazz in classes:
        try:
            bpy.utils.register_class(clazz)
        except:
            print("Unexpected error in jsonnodetree_register:%s" % traceback.format_exc())


    # link the json-ui config data into world object and access it via byp.data.world[0].jsonNodes
    bpy.types.World.jsonNodes=bpy.props.PointerProperty(type=NodeTreeCustomData)

    
    bpy.types.Object.nodetree=bpy.props.PointerProperty(type=bpy.types.NodeTree)
    #bpy.types.Object.nodetreeId = bpy.props.IntProperty(default=-1)
    bpy.types.NodeTree.id = bpy.props.IntProperty(default=-1)
    bpy.types.Object.id = bpy.props.IntProperty(default=-1)
#    bpy.types.Texture.id = bpy.props.IntProperty(default=-1)
    bpy.types.Image.id = bpy.props.IntProperty(default=-1)
    
    bpy.app.handlers.load_post.append(load_handler)
    DeActivatePath2Timer()


def unregister():
    json_nodetree_unregister()
    for clazz in classes_ui:
        bpy.utils.unregister_class(clazz)

def json_nodetree_unregister():
    if bpy.app.timers.is_registered(checkFileChange):
        bpy.app.timers.unregister(checkFileChange)

    for pcoll in preview_collections.values():
        print("Remove:pcoll")
        pcoll.clear()
        bpy.utils.previews.remove(pcoll)
        print("...done")
    preview_collections.clear()
    


    for clazz in classes:
        bpy.utils.unregister_class(clazz)

    del bpy.types.Object.nodetree
    #del bpy.types.Object.nodetreeId
    del bpy.types.NodeTree.id
    del bpy.types.Object.id
    del bpy.types.Image.id
    bpy.app.handlers.load_post.remove(load_handler)
#    rxUtils.disposeAll()

if __name__ == "__main__":
    register()
