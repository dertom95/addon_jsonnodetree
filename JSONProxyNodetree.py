import json
import bpy
import sys, traceback
from bpy.types import NodeTree, Node, NodeSocket
import base64, random


from JSONNodetreeCustom import Custom
import JSONNodetreeUtils
from JSONNodetreeUtils import NodeHasExposedValues,TreeHasNodeOfType

#import rxUtils
#from rx.subjects import Subject

proxy_nodetree_name = "__proxy_linked_exposeddata__"

collection_node_clazzes = {}

def GetCollectionInstanceDetail(nodeGroupInstance,linked_obj,tree,node):
    key = "%s__%s__%s" % ( linked_obj,tree,node)
    try:
        result = eval("nodeGroupInstance.%s" % key)
        return result
    except:
        # print("Something went wrong getting proxy node. nodeGroupInstance:%s obj:%s tree:%s node:%s" % (nodeGroupInstance.collection_root_object.name,linked_obj.name,tree.name,node.name))
        return None

def is_in_any_scene(obj):
    for scene in bpy.data.scenes:
        if obj.name in scene.objects:
            return True
    return False

def refresh_linked_instance(new_inst,get_default_from_nodetree=False):
    for linked_nodetree in new_inst.linked_nodetree_mapping:
        try:
            nt = eval("new_inst.%s"%linked_nodetree)

            # get the default-values from the nodetree and not the overriden data from the collection-objects
            for prop in nt.bl_rna.properties:
                prop_name = prop.name


                if not prop_name.endswith("_expose"):
                    continue

                modified = eval("nt.%s"%prop_name)
                if not modified:
                    try:
                        exec("nt.%s=False" % prop_name)                
                    except:
                        pass

        except:
            print("Could not read new_inst.%s"%linked_nodetree)



def sync_check_proxy(proxy_node,remove_if_root_in_no_scene=True):
    for idx in range(len(proxy_node.nodeGroupInstances)-1, -1, -1):
        inst = proxy_node.nodeGroupInstances[idx]

        # remove if the collection_root doesn't exist in any scene
        if remove_if_root_in_no_scene:
            try:
                if not is_in_any_scene(inst.collection_root_object):
                    proxy_node.nodeGroupInstances.remove(idx)
                    continue
            except:
                try:
                    if not is_in_any_scene(inst.root_object):
                        proxy_node.nodeGroupInstances.remove(idx)
                        continue
                except:
                    print("sync_check_proxy error:", sys.exc_info()[0])


        refresh_linked_instance(inst)

        # #iterate over all node-'overrides' and trigger update for those not modified
        # for key in inst.linked_nodetree_mapping:
        #     link_nt = inst.linked_nodetree_mapping[key]
        #     node_name = key.split("__")[2]
        #     link_node = None
        #     # get the corresponding node in the linked tree with the 'original' values
        #     for lnode in link_nt.nodes:
        #         if lnode.name == node_name:
        #             link_node = lnode
        #             break

        #     # todo: apply instace-data of the
        #     instData = eval("inst.%s"%key)
        #     for             


def refresh_libraries():
    for lib in bpy.data.libraries:
        lib.reload()
    sync_and_check_all_proxys()

def sync_and_check_all_proxys(remove_dangling=True):
    proxy_nt = bpy.data.node_groups[proxy_nodetree_name]
    for proxy_node in proxy_nt.nodes:
        sync_check_proxy(proxy_node,remove_dangling)


def EnsureProxyDataForLinkedNodetree(obj,nodetree, create=True):
    if not nodetree.library:
        print("only create proxy for linked-nodetrees: %s" % nodetree.name)
        return None

    proxy_nt = bpy.data.node_groups[proxy_nodetree_name]
    col_node_name = "proxynode_%s"%nodetree.name
    
    proxy_node=None
    try:
        proxy_node = proxy_nt.nodes[col_node_name]
    except:
        pass
    
    if not proxy_node:
        print("COULD NOT FIND LTree-Proxy-Node for tree:%s (obj:%s)" %(nodetree.name,obj.name))
        return None

    try:
        for instance in proxy_node.nodeGroupInstances:
            if instance.root_object == obj:
                return instance
            
        if not create:
            return None
        
        # create an instance
        new_inst = proxy_node.nodeGroupInstances.add()
        new_inst.linked_nodetree = nodetree
        new_inst.root_object = obj

        for linked_nodetree in new_inst.linked_nodetree_mapping:
            nt = eval("new_inst.%s"%linked_nodetree)
            nt.instance_object=obj
            nt.instance_tree=nodetree
            nt.collection_signature=linked_nodetree

            linked_obj_name,nodetree_name,node_name=linked_nodetree.split("__")
            linked_obj = bpy.data.objects[linked_obj_name]
            for l_ntp in linked_obj.nodetrees:
                if not l_ntp.nodetreePointer:
                    continue
                l_nt=l_ntp.nodetreePointer
                if l_nt.name!=nodetree_name:
                    continue
                node=l_nt.nodes[node_name]
                for prop_name in node.propNames:
                    exec("nt.%_exposename=%node.nodeData.%s_exposename" % (prop_name,prop_name))

        refresh_linked_instance(new_inst)

        return new_inst
    except:
        return None


def EnsureProxyDataForCollectionRoot(collection_root, create=True):
    collection = collection_root.instance_collection

    if not collection:
        print("No collection instance for object: %s" % collection_root.name)
        return None

    proxy_nt = bpy.data.node_groups[proxy_nodetree_name]
    col_node_name = "collectionnode_%s"%collection.name
    
    proxy_node=None
    try:
        proxy_node = proxy_nt.nodes[col_node_name]
    except:
        pass
    
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

        for linked_nodetree in new_inst.linked_nodetree_mapping:
            nt = eval("new_inst.%s"%linked_nodetree)
            nt.instance_object=collection_root
            node_tree_name = new_inst.linked_nodetree_mapping[linked_nodetree][1]
            nt.instance_tree=bpy.data.node_groups[node_tree_name]
            nt.collection_signature=linked_nodetree

            linked_obj_name,nodetree_name,node_name=linked_nodetree.split("__")
            linked_obj = bpy.data.objects[linked_obj_name]
            for l_ntp in linked_obj.nodetrees:
                if not l_ntp.nodetreePointer:
                    continue
                l_nt=l_ntp.nodetreePointer
                if l_nt.name!=nodetree_name:
                    continue
                node=l_nt.nodes[node_name]
                for prop_name in node.propNames:
                    exec("nt.%s_exposename=node.nodeData.%s_exposename" % (prop_name,prop_name))            

        refresh_linked_instance(new_inst)

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
        linked_nodetree_mapping = {}
        
        

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
            return "PROXY"



    print ("Process Collection-Proxy:%s"%col.name)
    found_exposed_values = False

    for obj in col.objects:
        for _treeInfo in obj.nodetrees:
            _tree = _treeInfo.nodetreePointer

            if not _tree or not _tree.has_exposed_values:
                continue

            for _node in _tree.nodes:
                if NodeHasExposedValues(_node):
                    key = "%s__%s__%s" % (obj.name,_tree.name,_node.name)
                    CollectionNodeGroupData.__annotations__[key]=bpy.props.PointerProperty(type=type(_node.nodeData))
                    found_exposed_values = True
                    CollectionNodeGroupData.linked_nodetree_mapping[key]=(obj.name,_tree.name,_node.name)
    
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

def CreateNodeForLinkedNodetree(lnodetree,register=True):
    global collection_node_clazzes

    if not lnodetree or not lnodetree.has_exposed_values:
        return


    class LinkedNodetreeGroupData(bpy.types.PropertyGroup):
        __annotations__ = {
            "linked_nodetree"  : bpy.props.PointerProperty(type=bpy.types.NodeTree),
            "root_object" : bpy.props.PointerProperty(type=bpy.types.Object)
        }
        linked_nodetree_mapping = {}
        
        

    # Derived from the Node base type.
    class LinkedNodetreeNode(bpy.types.Node):
        nonlocal lnodetree,LinkedNodetreeGroupData
        # === Basics ===
        # Description string
        '''Proxy Node %s''' % lnodetree.name
        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = 'proxynode_%s' % lnodetree.name
        # Label for nice name display
        bl_label = "proxynode_%s" % lnodetree.name
        # Icon identifier
        bl_icon = 'SOUND'

        linked_nodetree : bpy.props.PointerProperty(type=bpy.types.NodeTree)
        nodeGroupInstances : bpy.props.CollectionProperty(type=LinkedNodetreeGroupData)

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
            return "PROXY"



    print ("Process LNodetree-Proxy:%s"%lnodetree.name)
    found_exposed_values = False

    _tree = lnodetree


    for _node in _tree.nodes:
        if NodeHasExposedValues(_node):
            key = "linkedNT__%s__%s" % (_tree.name,_node.name)
            LinkedNodetreeGroupData.__annotations__[key]=bpy.props.PointerProperty(type=type(_node.nodeData))
            found_exposed_values = True
            LinkedNodetreeGroupData.linked_nodetree_mapping[key]=(None,_tree.name,_node.name)
    
    if register:
        if lnodetree in collection_node_clazzes:
            for elem in reversed(collection_node_clazzes[lnodetree]):
                try:
                    bpy.utils.unregister_class(elem)
                except:
                    pass

            #collection_node_clazzes.pop(col,None)
        
        if found_exposed_values:
            collection_node_clazzes[lnodetree]=[LinkedNodetreeGroupData,LinkedNodetreeNode]
            for elem in collection_node_clazzes[lnodetree]:
                try:
                    bpy.utils.register_class(elem)
                except:
                    pass
    
    if found_exposed_values:
        return LinkedNodetreeGroupData
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

    for nt in bpy.data.node_groups:
        if nt.library:
            lntNode = CreateNodeForLinkedNodetree(nt)
            node_id = "proxynode_%s" % nt.name
            if lntNode and not TreeHasNodeOfType(proxy_tree,node_id):
                proxy_tree.nodes.new(node_id)

    sync_and_check_all_proxys()

        
