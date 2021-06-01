import json
import bpy
import sys, traceback
from bpy.types import NodeTree, Node, NodeSocket
import base64, random


from JSONNodetreeCustom import Custom
import JSONNodetreeUtils
from JSONNodetreeUtils import CreateStringHash,NodeHasExposedValues,TreeHasNodeOfType

#import rxUtils
#from rx.subjects import Subject

proxy_nodetree_name = "__proxy_linked_exposeddata__"

collection_node_clazzes = {}

def GetCollectionInstanceDetail(nodeGroupInstance,linked_obj,tree,node):
    key = "%s__%s__%s" % ( linked_obj.name,tree.name,node.name)
    try:
        result = eval("nodeGroupInstance.%s" % key)
        return result
    except:
        # print("Something went wrong getting proxy node. nodeGroupInstance:%s obj:%s tree:%s node:%s" % (nodeGroupInstance.collection_root_object.name,linked_obj.name,tree.name,node.name))
        return None


def EnsureProxyDataForCollectionRoot(collection_root, create=True):
    collection = collection_root.instance_collection

    if not collection:
        print("No collection instance for object: %s" % collection_root.name)
        return None

    proxy_nt = bpy.data.node_groups[proxy_nodetree_name]
    proxy_node = proxy_nt.nodes["collectionnode_%s"%collection.name]
    if not proxy_node:
        print("COULD NOT FIND Proxy-Node for collection:%s (col_root:%s)" %(collection.name,collection_root.name))
        return None

    try:
        for instance in proxy_node.nodeGroupInstances:
            if instance.collection_root_object == collection_root:
                return instance
            
        if not create:
            return None
        
        # create an instance
        new_inst = proxy_node.nodeGroupInstances.add()
        new_inst.collection_root_object = collection_root
        new_inst.nodegroup_collection = collection
        return new_inst
    except:
        return None

def CreateNodeForCollection(col,register=True):
    global collection_node_clazzes

    class CollectionNodeGroupData(bpy.types.PropertyGroup):
        __annotations__ = {
            "collection_root_object"  : bpy.props.PointerProperty(type=bpy.types.Object),
            "nodegroup_collection" : bpy.props.PointerProperty(type=bpy.types.Collection)
        }

    # Derived from the Node base type.
    class CollectionNode(bpy.types.Node):
        nonlocal col,CollectionNodeGroupData
        # === Basics ===
        # Description string
        '''Collection Node %s''' % col.name
        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = 'collectionnode_%s' % col.name
        # Label for nice name display
        bl_label = "collectionnode_%s" % col.name
        # Icon identifier
        bl_icon = 'SOUND'

        master_collection : bpy.props.PointerProperty(type=bpy.types.Collection)
        nodeGroupInstances : bpy.props.CollectionProperty(type=CollectionNodeGroupData)

        @classmethod
        def poll(cls, ntree):
            return True

        def init(self, context):
            #print("Created CollectionNode:%s"%col.name)
            pass

        # Copy function to initialize a copied node from an existing one.
        def copy(self, node):
            print("Copying from node ", node)

        # Free function to clean up on removal.
        def free(self):
            print("Removing node ", self, ", Goodbye!")

        # Additional buttons displayed on the node.
        def draw_buttons(self, context, layout):
            layout.label(text=self.bl_idname)

        # Detail buttons in the sidebar.
        # If this function is not defined, the draw_buttons function is used instead
        def draw_buttons_ext(self, context, layout):
            layout.label(text=self.bl_idname)
        
        # Optional: custom label
        # Explicit user label overrides this, but here we can define a label dynamically
        def draw_label(self):
            #return "proxy col %s"%col.name
            pass



    print ("Process Collection-Proxy:%s"%col.name)
    found_exposed_values = False

    for obj in col.objects:
        for _treeInfo in obj.nodetrees:
            _tree = _treeInfo.nodetreePointer

            if not _tree.has_exposed_values:
                continue

            for _node in _tree.nodes:
                if NodeHasExposedValues(_node):
                    key = "%s__%s__%s" % (obj.name,_tree.name,_node.name)
                    CollectionNodeGroupData.__annotations__[key]=bpy.props.PointerProperty(type=type(_node.nodeData))
                    found_exposed_values = True
    
    if register:
        if col in collection_node_clazzes:
            for elem in reversed(collection_node_clazzes[col]):
                try:
                    bpy.utils.unregister_class(elem)
                except:
                    pass

            #collection_node_clazzes.pop(col,None)
        
        if found_exposed_values:
            collection_node_clazzes[col]=[CollectionNodeGroupData,CollectionNode]
            for elem in collection_node_clazzes[col]:
                try:
                    bpy.utils.register_class(elem)
                except:
                    pass
    
    if found_exposed_values:
        return CollectionNode
    else:
        return None

def CreateProxyNodetree():
   
    if proxy_nodetree_name not in bpy.data.node_groups:
        bpy.data.node_groups.new(proxy_nodetree_name,"urho3dcomponents")
        bpy.data.node_groups[proxy_nodetree_name].use_fake_user = True


    proxy_tree = bpy.data.node_groups[proxy_nodetree_name]

    for col in bpy.data.collections:
        if not col.library or not col.urhoExport:
            continue
        collectionNodeClz = CreateNodeForCollection(col)
        node_id = "collectionnode_%s"%col.name
        if collectionNodeClz and not TreeHasNodeOfType(proxy_tree,node_id):
            proxy_tree.nodes.new(node_id)

        
