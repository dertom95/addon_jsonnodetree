import json
import bpy
import sys 
from bpy.types import NodeTree, Node, NodeSocket
from JSONNodetreeCustom import CustomMethod 

class DefaultCollection(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="")

#classes = [DefaultCollection]
classes = []
node_categories = []

def getConfig():
    return bpy.data.worlds[0].jsonNodes

# Implementation of custom nodes from Python
def loadJSON(filename):
    file = open(filename,"r")
    result = file.read()
    jsonResult = json.loads(result)
    print("File:"+str(result))
    return jsonResult


def feedback(output,type=""):
    print("Feedback: %s" % output)

class MyCustomSocket(NodeSocket):
    # Description string
    '''Custom node socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CustomSocketType'
    # Label for nice name display
    bl_label = "Custom Node Socket"

    # Enum items list
    my_items = (
        ('DOWN', "Down", "Where your feet are"),
        ('UP', "Up", "Where your head should be"),
        ('LEFT', "Left", "Not right"),
        ('RIGHT', "Right", "Not left")
    )

    my_enum_prop = bpy.props.EnumProperty(name="Direction", description="Just an example", items=my_items, default='UP')

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "my_enum_prop", text=text)

    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)


### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


def createNodeTree(data):
    
    categoryMap={}
    
    def jsontype2NodeType(jsontype):
        if jsontype=="float":
            return "NodeSocketFloat";
        elif jsontype=="int":
            return "NodeSocketInt";
        elif jsontype=="bool":
            return "NodeSocketBool";
        elif jsontype=="string":
            return "NodeSocketString";
        elif jsontype=="vector":
            return "NodeSocketVector";
        else: 
            raise Exception("Unknown jsontype:"+jsontype)

    # Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
    class MyCustomTree(NodeTree):
        # Description string
        '''A custom node tree type that will show up in the node editor header'''
        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = data["id"]
        # Label for nice name display
        bl_label = data["name"]
        # Icon identifier
        bl_icon = data.get("icon",'NODETREE')
        
        @classmethod
        def get_from_context(cls, context):
            current_object = context.object
            space_data = context.space_data
            
            show_nodetree = space_data.node_tree
            
            config = getConfig()
            
            # automatically select nodetree of the current object?
            if current_object.nodetreeName!="" and config.autoSelectObjectNodetree == True:
               # check if the corresponding nodetree acutally exists
               if current_object.nodetreeName in bpy.data.node_groups:
                   # node tree is known
                   show_nodetree = bpy.data.node_groups[current_object.nodetreeName]
                   feedback("found nodetree: %s" % current_object.nodetreeName) 
               else:
                   # inconsistend data. a nodetree is referenced that is not known
                   feedback("Unknown nodetree(%s) assigned to object %s" % (current_object.nodetreeName,current_object.name))
            
            return show_nodetree,show_nodetree,current_object
            
            
            


    # Mix-in class for all custom nodes in this tree type.
    # Defines a poll function to enable instantiation.
    class MyCustomTreeNode:
        @classmethod
        def poll(cls, ntree):
            return ntree.bl_idname == data["id"]
        
    # our own base class with an appropriate poll function,
    # so the categories only show up in our own tree type
    class MyNodeCategory(NodeCategory):
        @classmethod
        def poll(cls, context):
            return context.space_data.tree_type == data["id"]
        
    def createNode(data):
        print("CREATE NODE:"+str(data))
        class InnerCustomNode(Node, MyCustomTreeNode):
            # === Basics ===
            # Description string
            '''A custom node'''
            # Optional identifier string. If not explicitly defined, the python class name is used.
            bl_idname = data["id"]
            # Label for nice name display
            bl_label = data["name"]
            # Icon identifier
            bl_icon = data.get("icon","SOUND")


            # === Custom Properties ===
            # These work just like custom properties in ID data blocks
            # Extensive information can be found under
            # http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
            propNames=[]

            
            # === Optional Functions ===
            # Initialization function, called when a new node is created.
            # This is the most common place to create the sockets for a node, as shown below.
            # NOTE: this is not the same as the standard __init__ function in Python, which is
            #       a purely internal Python method and unknown to the node system!
            def init(self, context):
                for insock in data.get("inputsockets",[]):
                    name = insock.get("name","noname")
                    type = insock.get("type","float")
                    defaultValue = insock.get("default",None)

                    btype = jsontype2NodeType(type)
                    newsocket = self.inputs.new(btype,name)
                    if defaultValue:
                        newsocket.default_value=defaultValue
                    

                for outsock in data.get("outputsockets",[]):
                    name = outsock.get("name","noname")
                    type = outsock.get("type","float")
                    defaultValue = outsock.get("default",None)

                    btype = jsontype2NodeType(type)
                    newsocket = self.outputs.new(btype,name)
                    if defaultValue:
                        newsocket.default_value=defaultValue
                    
                    
            # Copy function to initialize a copied node from an existing one.
            def copy(self, node):
                print("Copying from node ", node)

            # Free function to clean up on removal.
            def free(self):
                print("Removing node ", self, ", Goodbye!")

            # Additional buttons displayed on the node.
            def draw_buttons(self, context, layout):
                layout.label("Node settings")

                for propName in self.propNames:
                    try:
                        # override? CustomMethod.[NodeName]_[PropName]
                        #print("TRYING: CustomMethod.UI_"+data["id"]+"_"+propName+"(self,context,layout)")
                        exec("CustomMethod.UI_"+data["id"]+"_"+propName+"(self,context,layout,propName)")
                    except:
                        # standard view
                        layout.prop(self,propName) 

            # Detail buttons in the sidebar.
            # If this function is not defined, the draw_buttons function is used instead
            def draw_buttons_ext(self, context, layout):
                for propName in self.propNames:
                    layout.prop(self,propName) 


            # Optional: custom label
            # Explicit user label overrides this, but here we can define a label dynamically
            #def draw_label(self):
            #    return "I am a custom node"
        

        def createProperty(prop):
            name = prop["name"];
            type = prop["type"];
            label = prop.get("label",name)
            description = prop.get("description",name)
            
            InnerCustomNode.propNames.append(name);

            print("prop: %s => %s" % (name,type) )
            
            if type=="float":
               default = prop.get("default",0.0);
               exec("InnerCustomNode.%s=bpy.props.FloatProperty(name='%s',default=%s,description='%s')" % ( name,label,default,description ))
            elif type=="string":
               default = prop.get("default","");
               exec("InnerCustomNode.%s=bpy.props.StringProperty(name='%s',default='%s',description='%s')" % ( name,label,default,description ))
            elif type=="bool":
               default = prop.get("default","False")=="true" or "True";
               exec("InnerCustomNode.%s=bpy.props.BoolProperty(name='%s',default=%s,description='%s')" % ( name,label,default,description ))
            elif type=="int":
               print("INT")
               default = prop.get("default",0);
               exec("InnerCustomNode.%s=bpy.props.IntProperty(name='%s',default=%s,description='%s')" % ( name,label,default,description ))
            elif type=="vector2":
               default = eval(prop.get("default",(0.0,0.0)));
               exec("InnerCustomNode.%s=bpy.props.FloatVectorProperty(name='%s',default=%s,size=2,description='%s')" % ( name,label,default,description ))
            elif type=="vector3":
               default = eval(prop.get("default",(0.0,0.0,0.0)));
               exec("InnerCustomNode.%s=bpy.props.FloatVectorProperty(name='%s',default=%s,size=3,description='%s')" % ( name,label,default,description ))
            elif type=="vector4":
               default = eval(prop.get("default",(0.0,0.0,0.0,0.0)));
               exec("InnerCustomNode.%s=bpy.props.FloatVectorProperty(name='%s',default=%s,size=4,description='%s')" % ( name,label,default,description ))
            elif type=="color":
               default = eval(prop.get("default",(1.0,1.0,1.0,1.0)));
               exec("InnerCustomNode.%s=bpy.props.FloatVectorProperty(name='%s',default=%s,size=4,subtype='COLOR',description='%s',min=0.0,max=1.0 )" % ( name,label,default,description))
            elif type=="collection":
               default = prop.get("default",0.0);
               exec("InnerCustomNode.%s=bpy.props.CollectionProperty(type=DefaultCollection,description='%s')" % ( name ))
            elif type=="enum":
               default = eval(prop.get("default",0));               
               elements = []
               count=0
               defaultID = None
               for elem in prop["elements"]:
                   id = elem.get("id",("%s-%i" % (name,count)))
                   ename = elem.get("name",("%s-%i" % (name,count)))
                   descr = elem.get("description","")
                   icon = elem.get("icon","")
                   elements.append((id,ename,descr,icon,count))
                   
                   # find the defaultID (but to be sure take the firstID in case we don't get to the real defaultID)
                   if count==default or defaultID==None:
                       defaultID=id

                   count = count + 1
                   
               exec("InnerCustomNode.%s=bpy.props.EnumProperty(name='%s',items=elements,default='%s')" % (name,label,defaultID))
                           
            else:
               raise Exception("Unknown property-type:"+type)
    
        properties=data.get("props",[])
        items = []
        for prop in properties:
            try:
                createProperty(prop)
            except:
                print("error creating property from:%s" % prop["name"])
                e = sys.exc_info()[0]
                print("exception %s" % str(e))

        categoryName = data.get("category","nocategory")

        category = categoryMap.get(categoryName,None)
        if (category == None): 
            # create item-array
            category = []
            categoryMap[categoryName]=category

        category.append(NodeItem(data["id"]))        
        # push the node to the registry
        classes.append(InnerCustomNode)
        
        return InnerCustomNode                       
    
    print("Create tree: %s" % (data["id"]) )           
    classes.append(MyCustomTree)
    #classes.append(MyNodeCategor)
        
    # create the nodes    
    for nodeData in data["nodes"]:
        createNode(nodeData)
        
    print("CATEGORYMAP:"+str(categoryMap))    
    # create categories
    for catName,catItems in categoryMap.items():
        node_categories.append(MyNodeCategory(data["id"]+"."+catName,catName,items=catItems))
        



def createNodeTrees(data):
    unregister()
    global classes
    global node_categories
    
    classes=[]
    node_categories=[]
    # create nodetrees
    for nodetree in data["trees"]:
        createNodeTree(nodetree)
    
    # create categories
    

#nodeData = loadJSON("/home/ttrocha/_dev/_projects/blendertools/BlenderAddon/src/nodetree.json")
#createNodeTrees(nodeData)

categoryItems = []



# all categories in a list
#node_categories = [
    # identifier, label, items list
#    MyNodeCategory('SOMENODES', "Some Nodes", items=[
        # our basic node
#        NodeItem("CustomNodeType"),
#        NodeItem("org.tt.boolNode")
#    ]),
#    MyNodeCategory("Generated","Gen-Nodes",items=categoryItems),
#    MyNodeCategory('OTHERNODES', "Other Nodes", items=[
        # the node item can have additional settings,
        # which are applied to new nodes
        # NB: settings values are stored as string expressions,
        # for this reason they should be converted to strings using repr()
#        NodeItem("CustomNodeType", label="Node A", settings={
#            "my_string_prop": repr("Lorem ipsum dolor sit amet"),
#            "my_float_prop": repr(1.0),
#        }),
#        NodeItem("CustomNodeType", label="Node B", settings={
#            "my_string_prop": repr("consectetur adipisicing elit"),
#            "my_float_prop": repr(2.0),
#        }),
#    ]),
#]

def register():
    from bpy.utils import register_class
    for cls in classes:
        try:
            print("UNREGISTER:"+str(cls))
            bpy.utils.unregister_class(cls)
        except NameError as err:
            print("Name error:"+str(err))
        except:
            e = sys.exc_info()[0]
            print("error:"+str(e))

        print("REGISTER:"+str(cls))
        register_class(cls)

    try:
        print("TRY TO UNREGISTER")
        nodeitems_utils.unregister_node_categories('CUSTOMNODES')
        print("success")
    except RuntimeError as err:
        print("runtimeerror:"+str(err))
    except:
        e = sys.exc_info()[0]
        print("error:"+str(e))
    
    print("REGISTER NODE-Cats:"+str(node_categories))

    nodeitems_utils.register_node_categories('CUSTOMNODES', node_categories)


def unregister():
    try:
        nodeitems_utils.unregister_node_categories('CUSTOMNODES')
    except:
        pass

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass



if __name__ == "__main__":
    register()
