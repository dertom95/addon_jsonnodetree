import json
import bpy
import sys, traceback
from bpy.types import NodeTree, Node, NodeSocket
import base64


from JSONNodetreeCustom import Custom
import JSONNodetreeUtils
from JSONNodetreeUtils import CreateStringHash

#import rxUtils
#from rx.subjects import Subject




class DefaultCollection(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(default="")

#classes = [DefaultCollection]
classes = []
node_categories = []
# this data object (dictionary) is filled during nodetree-creation
globalData=None

# function to get textures for template_icon_preview (thx, andreas esau)
def get_icons(self,context):
    icons = []
#    for i,tex in enumerate(bpy.data.t  extures):
#        icons.append((tex.name,tex.name,tex.name,tex.preview.icon_id,i))
    for i,tex in enumerate(bpy.data.images):
        id = JSONNodetreeUtils.getID(tex,True)
        icons.append((str(id),tex.name,tex.name,tex.preview.icon_id,id))
    return icons    

def getConfig():
    return bpy.data.worlds[0].jsonNodes

# Implementation of custom nodes from Python
def loadJSON(filename):
    file = open(filename,"r")
    result = file.read()
    jsonResult = json.loads(result)
    #print("File:"+str(result))
    return jsonResult


def feedback(output,type=""):
    print("Feedback: %s" % output)

def propValue(node,propName):
    prop = eval("node.%s" % propName)
    propType = node.propTypes[propName]
    if (propType in ["vector4","vector3","vector2","color"]):
        output="("
        arraySize = len(prop)
        for idx in range(arraySize):
            output+=str(prop[idx])
            if (idx+1 < arraySize):
                output+=","
        output +=")"
        return output
    else:
        return str(prop)

def exportScene(scene):
    objectNodetreeMapping = {
        "sceneName" : scene.name,
        "objectMapping" : []
    }

    objMapping = objectNodetreeMapping["objectMapping"]
    for obj in scene.objects:
        if (not obj.nodetree):
            continue

        objMap = {
            "objectName": obj.name,
            "nodetreeName": obj.nodetree.name,
            "nodetreeFilename": "nt_"+obj.nodetree.name
        }
        objMapping.append(objMap)

    return objectNodetreeMapping


def exportNodes(nodetree,onlyValueDifferentFromDefault=False):
    tree = {
        "name" : nodetree.name,
        "nodes": [],
        "links" : []
    }
    print("1")
    exportNodes = tree["nodes"]
    links = tree["links"]

    print("11")
    for ntlink in nodetree.links:
        link = {
            "from_node_name" : ntlink.from_node.name,
            "from_node_type"     : ntlink.from_node.bl_idname,
            "from_socket"   : ntlink.from_socket.name,
            "to_node_type"       : ntlink.to_node.bl_idname,
            "to_socket"     : ntlink.to_socket.name,
            "to_node_name" :  ntlink.to_node.name
        }

        links.append(link)

    print("111")
    nodeCache = {}
    id = 0
    # first pass create the nodes
    for node in nodetree.nodes:
        if (node.bl_idname=="NodeReroute"):
            # ignore reroute node (this things that separate connections)
            continue

        print("export NODE:%s" % node.name)
        dictNode = {
            "id"    :   id,
            "type"  :   node.bl_idname,
            "label" :   node.bl_label,
            "name"  :   node.name,
            "props" :   [],
            "inputsockets" : [],
            "outputsockets" : []
        }
        nodeCache[node]=dictNode
        id=id+1
        exportNodes.append(dictNode)

        props = dictNode["props"]

        for propName in node.propNames:
            print("MAPBACK: %s",propName)
            mapBackName = ""
            try:
                mapBackName = node.propNameMapping[propName]
            except:
                print("Couldnt mapback:%s",propName)
                mapBackName = propName[5:]
            
            propertyDefault = eval("node.bl_rna.properties['"+propName+"']").default
            
            prop = { 
         #       "name" : propName[5:],
                "name" : mapBackName,
                "value" : propValue(node,propName),
                "type"  : node.propTypes[propName],
                "default" : propertyDefault
            }

            if onlyValueDifferentFromDefault:
                try:
                    print("node.bl_rna.properties['"+propName+"'].default")
                    
                    if prop["value"]!=str(propertyDefault):
                        # value changed
                        props.append(prop)
                except:
                    print("Problem getting default value for %s",propName)
            else:
                props.append(prop)

    


    # 2nd pass create the connections
    #for node in nodetree.nodes:
        
           # store id for this node
    return tree


            
        

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

    my_enum_prop : bpy.props.EnumProperty(name="Direction", description="Just an example", items=my_items, default='UP')

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
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
            
            # check if someone have a custom selection for the current node-tree selection
            # use this mechanism to use a custom nodetree selection in your addon
            overrideNodetree = JSONNodetreeUtils.overrideAutoNodetree(current_object,space_data.tree_type,show_nodetree)

            if overrideNodetree=="NOTREE":
                return None,None,current_object
            elif overrideNodetree:
                return overrideNodetree,overrideNodetree,current_object

            # automatically select nodetree of the current object?
            if config.autoSelectObjectNodetree == True:
                if current_object.nodetree:
                    show_nodetree = current_object.nodetree
                    # check if the corresponding nodetree acutally exists
                    if current_object.nodetree:
                        # node tree is known
                        return current_object.nodetree,current_object.nodetree,current_object
                        feedback("found nodetree: %s" % current_object.nodetree.name) 
                    else:
                        # inconsistend data. a nodetree is referenced that is not known
                        feedback("Unknown nodetree(%s) assigned to object %s" % (current_object.nodetree.name,current_object.name))

                return None,None,current_object
            
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
        try:
            #exec("Custom.UI_sidebar_"+data["id"]+"_"+propName+"(self,context,layout,propName)")
            #print('data["props"].extend(Custom.UI_props_'+data["id"]+'() )')
            exec('data["props"].extend(Custom.UI_props_'+data["id"]+'() )')
            print("successully added custom-props for %s" % data["id"])
        except:
            pass

        #print("CREATE NODE:"+str(data))

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
            propTypes={} # propName=>type(string)
            customData={}
            # for some reason all type I get from node2.bl_rna.properties['prop'] is FloatProperty....a bug? For now keep a separate dict for all defaultValues

            defaultValues ={}
            # TODO: do I need this? I have the name as it was exported already in the label!?
            propNameMapping={} # map property-conformont name with original name (e.g. 'Occlusion_Culling' =>  'Occluision Culling')

            __annotations__={}
            
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
                layout.label(text="Node settings")

                try:
                    # here you have the chance to add additional buttons at the bottom
                    if bpy.data.worlds[0].jsonNodes.outputHooks:
                        print("HOOK UI additional props: Node("+data["id"]+"): Custom.UI_"+data['id']+"_top(self,context,layout)")

                    exec("Custom.UI_"+data["id"]+"_top(self,context,layout)")
                    #print("FOUND NODE-Hook Custom.UI_"+data["id"]+"(self,context,layout)")
                except:
                    pass


                for propName in self.propNames:
                    try:
                        # override? Custom.[NodeName]_[PropName]
                        if bpy.data.worlds[0].jsonNodes.outputHooks:
                            print("HOOK UI: Node("+data["id"]+"): Custom.UI_"+data["id"]+"_"+propName+"(self,context,layout,propName)")

                        exec("Custom.UI_"+data["id"]+"_"+propName+"(self,context,layout,propName)")
                        #print("FOUND HOOK:Custom.UI_"+data["id"]+"_"+propName+"(self,context,layout,propName)")
                    except:
                        propType = self.propTypes[propName]

                        parent = layout


                        if hasattr(self,propName+"_cat"):
                            parent = layout.box()
                            row = parent.row()
                            row.label(text=data["name"])

                            row = parent.row()
                            try:
                                row.prop(self,propName+"_cat",text="category")
                            except:
                                pass
                        else:
                            row = parent.row()

                        if propType == "enumPreview":
                            #print("Check: %s %s" % (self.name,propName))
                            parent.template_icon_view(self,propName,show_labels=True)
                            parent.prop(self,propName)
                        else:
                            # standard view
                            parent.prop(self,propName)

                try:
                    # here you have the chance to add additional buttons at the bottom
                    if bpy.data.worlds[0].jsonNodes.outputHooks:
                        print("HOOK UI additional props: Node("+data["id"]+"): Custom.UI_"+data['id']+"_bottom(self,context,layout)")

                    exec("Custom.UI_"+data["id"]+"_bottom(self,context,layout)")
                    #print("FOUND NODE-Hook Custom.UI_"+data["id"]+"(self,context,layout)")
                except:
                    pass

                     

            # Detail buttons in the sidebar.
            # If this function is not defined, the draw_buttons function is used instead
            def draw_buttons_ext(self, context, layout):
                for propName in self.propNames:
                    try:
                        # override? Custom.[NodeName]_[PropName]
                        if bpy.data.worlds[0].jsonNodes.outputHooks:
                            print("HOOK UI: SideBar("+data["id"]+"): Custom.UI_"+data["id"]+"_"+propName+"(self,context,layout)")
                        exec("Custom.UI_sidebar_"+data["id"]+"_"+propName+"(self,context,layout,propName)")
                    except:
                        propType = self.propTypes[propName]
                        if propType == "texture":
                            layout.template_icon_view(self,propName)
                        else:
                            # standard view
                            layout.prop(self,propName)

                try:
                    # here you have the chance to add additional buttons
                    if bpy.data.worlds[0].jsonNodes.outputHooks:
                        print("HOOK UI additional props: Node("+data["id"]+"): Custom.UI_"+data['id']+"(self,context,layout,propName)")

                    exec("Custom.UI_sidebar_"+data["id"]+"(self,context,layout)")
                except:
                    pass 

            # Optional: custom label
            # Explicit user label overrides this, but here we can define a label dynamically
            #def draw_label(self):
            #    return "I am a custom node"
        def export(self):
            print("EXPORT") 

        def createProperty(prop):
            name = "prop_"+prop["name"].replace(" ","_").replace("/","_").replace("-","_");
            #print("CREATE %s" %name)
            type = prop["type"]
            label = prop.get("label",prop["name"])
            description = prop.get("description",name)
            
            InnerCustomNode.propNames.append(name)
            InnerCustomNode.propTypes[name]=type
            InnerCustomNode.propNameMapping[name]=prop["name"]

            #print("prop: %s => %s" % (name,type) )
            default = None
            if type=="float":
                mini = prop.get("min",-65535.0)
                maxi = prop.get("max",65535.0)
                step = prop.get("step",3)
                subtype = prop.get("subtype","NONE")
                precision = prop.get("precision",3)
                unit = prop.get("unit","NONE")
                default = prop.get("default",0.0)
                exec("InnerCustomNode.__annotations__['%s']=bpy.props.FloatProperty(subtype='%s',name='%s',default=%s,description='%s',min=%s,max=%s,step=%s,unit='%s',precision=%s)" % ( name,subtype,label,default,description,mini,maxi,step,unit,precision ))
            elif type=="string":
                default = prop.get("default","")
                exec("InnerCustomNode.__annotations__['%s']=bpy.props.StringProperty(name='%s',default='%s',description='%s')" % ( name,label,default,description ))
            elif type=="bool":
                default = prop.get("default","False")=="true"
                exec("InnerCustomNode.__annotations__['%s']=bpy.props.BoolProperty(name='%s',default=%s,description='%s')" % ( name,label,default,description ))
            elif type=="int":
                mini = prop.get("min",-65535)
                maxi = prop.get("max",65535)
                step = prop.get("step",1)
                subtype = prop.get("subtype","NONE")
                default = 0
                try:
                    default = int(prop.get("default",0))
                except:
                    default = 0
                exeStr = "InnerCustomNode.__annotations__['%s']=bpy.props.IntProperty(subtype='%s',name='%s',default=%s,description='%s',min=%s,max=%s,step=%s)" % ( name,subtype,label,default,description,mini,maxi,step )
                exec(exeStr)
            elif type=="vector2":
                default = prop.get("default",(0.0,0.0));
                exec("InnerCustomNode.__annotations__['%s']=bpy.props.FloatVectorProperty(name='%s',default=%s,size=2,description='%s')" % ( name,label,default,description ))
            elif type=="vector3":
                default = prop.get("default",None) or (0.0,0.0,0.0)
                exec("InnerCustomNode.__annotations__['%s']=bpy.props.FloatVectorProperty(name='%s',default=%s,size=3,description='%s')" % ( name,label,default,description ))
            elif type=="vector4":
                default = eval(prop.get("default",(0.0,0.0,0.0,0.0)));
                exec("InnerCustomNode.__annotations__['%s']=bpy.props.FloatVectorProperty(name='%s',default=%s,size=4,description='%s')" % ( name,label,default,description ))
            elif type=="color":
                default = eval(prop.get("default",(1.0,1.0,1.0,1.0)));
                exec("InnerCustomNode.__annotations__['%s']=bpy.props.FloatVectorProperty(name='%s',default=%s,size=4,subtype='COLOR',description='%s',min=0.0,max=1.0 )" % ( name,label,default,description))
            elif type=="collection":
                default = prop.get("default",0.0);
                exec("InnerCustomNode.__annotations__['%s']=bpy.props.CollectionProperty(type=DefaultCollection,description='%s')" % ( name ))
 #           elif type=="texture":
 #               exec("InnerCustomNode.__annotations__['%s']=bpy.props.EnumProperty(items=get_icons,update=JSONNodetreeUtils.modalStarter)" % name)
            elif type=="enum" or type=="enumPreview":
                #print("2222")
                default = int(prop.get("default",0));               
                delimiter="/"        
                categories={} 
                
                InnerCustomNode.customData["%s_cat"%name]=categories

                def add_to_category(category,elem):
                    if category in categories:
                        categories[category].append(elem)
                    else:
                        categories[category]=[elem]

                elements = []
                count=0
                defaultID = None
                no_category = prop.get("use_category","false").lower()=="false"

                if (len(prop["elements"])==0):
                    id = "%s-%i" % (name,count)
                    ename = "No Elements"
                    descr = "No Elements"
                    icon = ""
                    number = count
                    defaultID = id
                    elements.append((id,ename,descr,icon,number))
                    type="enum"
                else:
                    if type=="enum":
                        for elem in prop["elements"]:
                            id = elem.get("id",("%s-%i" % (name,count)))
                            ename = elem.get("name",("%s-%i" % (name,count)))
                            if (count == default):
                                descr = "%s - %s[default]" % (count,elem.get("description",""))
                            else:
                                descr = "%s - %s" % (count,elem.get("description",""))
                            icon = elem.get("icon","")
                            number = count
                            try:
                                number = int(elem.get("number",count))
                                #print("FOUND ENUM-Number:%s" % number)
                                if number==0:
                                    number=count
                            except:
                                pass


                            #print("USING NUMBER:%s" % number)
                            enumelem = (id,ename,descr,icon,number)
                            elements.append(enumelem)

                            if not no_category:
                                add_to_category("all",enumelem)
                                categoryname = elem.get("category","")
                                if categoryname and categoryname=="" and delimiter in ename:
                                    categoryname=ename[:ename.rfind(delimiter)]
                                if categoryname!="":
                                    add_to_category(categoryname,enumelem)
                            else:
                                pass
                                #print("NO CATE")


                        # find the defaultID (but to be sure take the firstID in case we don't get to the real defaultID)
                            if number==default or defaultID==None:
                                defaultID=id
                                #print("DEFAULT ID %s" % id)
                            else:
                                #print("NOT DEFAULT ID (%s) %s!=%s" %(id,number,default))
                                pass

                            count = count + 1
                    else: # preview-enum
                        try:
                            pcoll = JSONNodetreeUtils.pcoll
                            for elem in prop["elements"]:
                                filename = elem.get("description",None)
                                if filename:
                                    thumb = pcoll.load(filename,filename,'IMAGE')
                                    #print("THUMB: %s - %s" % (filename,str(thumb.icon_id)))
                                    if not thumb:
                                        print("SOMETHING WENT WRONG WITH THUMB CREATION")
                                        continue

                                    id = elem.get("id",("%s-%i" % (name,count)))
                                    ename = elem.get("name",("%s-%i" % (name,count)))
                                    if (count == default):
                                        descr = "%s - %s[default]" % (count,elem.get("description",""))
                                    else:
                                        descr = "%s - %s" % (count,elem.get("description",""))
                                    icon = elem.get("icon","")
                                    number = count
                                    try:
                                        number = int(elem.get("number",count))
                                        #print("FOUND ENUM-Number:%s thumbid %s" % (number,str(thumb.icon_id)))
                                        if number==0:
                                            number=count
                                    except:
                                        pass
                                    #print("USING NUMBER:%s" % number)
                                    enumelem=(id,ename,descr,thumb.icon_id,number)
                                    elements.append(enumelem)

                                    if not no_category:
                                        add_to_category("all",enumelem)
                                        categoryname = elem.get("category",None)
                                        if not categoryname and delimiter in ename:
                                            categoryname=ename[:ename.rfind(delimiter)]
                                        if categoryname:
                                            add_to_category(categoryname,enumelem)

                            # find the defaultID (but to be sure take the firstID in case we don't get to the real defaultID)
                                if count==default or defaultID==None:
                                    defaultID=id

                                count = count + 1     

                        except NameError as err:
                            print ("error: NameError %s",str(err))
                            traceback.print_exc(file=sys.stdout)                
                        except TypeError as terr:
                            print ("error: TypeError %s",str(terr))
                            traceback.print_exc(file=sys.stdout)                
                        except AttributeError as aerr:
                            print ("attributeError: %s",str(aerr))
                        except KeyError as keyerr:
                            print ("error: KeyError %s",str(keyerr))
                            traceback.print_exc(file=sys.stdout)                

                        except:
                            print("error creating property from:%s" % prop["name"])
                            e = sys.exc_info()[0]
                            traceback.print_exc(file=sys.stdout)
                            print("exception %s" % str(e))                            




 #               categories["all"]=elements
 #               if not no_category:
 #                   print("NOoOO CAT")
 #                   for e in elements:
 #                       print("ELEM:%s" % str(e))
 #                       try:
 #                           idx = e[1].rfind(delimiter)
 #                           category = str(e[1][:idx])
 #                           add_to_category(category,e)
 #                       except:
 #                           print("EX")
 #                           pass
                    catElems=[]
 
                    for catName in categories.keys():
                        catElems.append((catName,catName,catName,CreateStringHash(catName)))

                def dynamicElements(self,context):
                    catEnum = eval("self.%s_cat"%name)
                    #print ("cat:%s" % catEnum)
                    return categories[str(catEnum)]
                    #return categories["all"]

                if len(categories)>1:
                    #print("CREATE InnerCustomNode.__annotations__['%s']=bpy.props.EnumProperty(name='%s'.." % (name,label))
                    exec("InnerCustomNode.__annotations__['%s']=bpy.props.EnumProperty(name='%s',items=dynamicElements)" % (name,label))
                    exec("InnerCustomNode.__annotations__['%s_cat']=bpy.props.EnumProperty(name='%s_cat',items=catElems)" % (name,label))
                else:
                    #print("2:CREATE InnerCustomNode.__annotations__['%s']=bpy.props.EnumProperty(name='%s'.." % (name,label))
                    try:
                        exec("InnerCustomNode.__annotations__['%s']=bpy.props.EnumProperty(name='%s',items=elements,default='%s')" % (name,label,defaultID))
                    except:
                        traceback.print_exc(file=sys.stdout)                  
            else:
                raise Exception("Unknown property-type:"+type)

            if default:
                InnerCustomNode.defaultValues[name]=default

        properties=data.get("props",[])


        items = []
        for prop in properties:
            try:
                createProperty(prop)
            except NameError as err:
                print ("error: NameError %s",str(err))
                traceback.print_exc(file=sys.stdout)                
            except TypeError as terr:
                print ("error: TypeError %s",str(terr))
                traceback.print_exc(file=sys.stdout)
            except AttributeError as aerr:
                print ("attributeError: %s",str(aerr))
                traceback.print_exc(file=sys.stdout)
            except:
                print("error creating property from:%s" % prop["name"])
                e = sys.exc_info()[0]
                print("exception %s" % str(e))
                traceback.print_exc(file=sys.stdout)

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
    
    #print("Create tree: %s" % (data["id"]) )           
    classes.append(MyCustomTree)
    #classes.append(MyNodeCategor)
        
    # create the nodes    
    for nodeData in data["nodes"]:
        createNode(nodeData)
        
    #print("CATEGORYMAP:"+str(categoryMap))    
    # create categories
    for catName,catItems in categoryMap.items():
        node_categories.append(MyNodeCategory(data["id"]+"."+catName,catName,items=catItems))
        

def convertGlobalDataToEnumItems(key):
    global globalData
    elements=[]
    for elem in globalData[key]:
        try:
            descr = elem.get("description",None)
            id = elem.get("id","noid")
            name = elem.get("name","noname")
            number = int(elem.get("number","0"))
            enumelem=(id,name,descr,number)
            elements.append(enumelem)
        except:
            print("[%s] Problem with: %s" % (key,elem))
    return elements

def createNodeTrees(data):
    #ntUnregister()
    global classes
    global node_categories
    global globalData
    
    classes=[]
    node_categories=[]

    if "globalData" in data:
        globalData = data["globalData"]
        try:
            for global_key in list(globalData.keys()):
                try:
                    globalData["%s_elemitems"%global_key]=convertGlobalDataToEnumItems(global_key)
                except:
                    print("Could not convert globalData['%s'] to enum-items)" % global_key)
                    e = sys.exc_info()[0]
                    print("error:"+str(e))
        except:
            e = sys.exc_info()[0]
            print("error:"+str(e))
            print("Something went wrong converting globaldata!")

    else:
        globalData = None

    if "customUI" in data:
        for customUI in data["customUI"]:
            try:
                customUIScript = base64.b64decode(customUI)
                customUIScript = customUIScript.decode("utf-8")
                print("CUSTOMUI:"+customUIScript )
                exec(customUIScript)
                print("FINISHED CUSTOMUI")
                print("TYPE: "+str(type(Custom)))
            except:
                print("Something went wrong with customui (base64)")

        customUIFile = bpy.data.worlds[0].jsonNodes.customUIFile
        if customUIFile!="":
            print("try to load customfile:"+customUIFile)
            try:
                customuiFileData = open(customUIFile).read();
                print("CUSTOMUI+++++++++++++++++++++++++-------------------_");
                print(customuiFileData)
                if customuiFileData:
                    print("\nTRY TO EXECUTE\n")
                    exec(customuiFileData)
                    print("successs")

            except NameError as err:
                print("Could not process customUI-file %s" % data["customUI-file"])
                print("Name error:"+str(err))
            except RuntimeError as rer:
                print("Could not process customUI-file %s" % data["customUI-file"])
                print("RuntimeError:%s" % str(rer))
            except:
                print("Could not process customUI-file %s" % data["customUI-file"])
                e = sys.exc_info()[0]
                print("error:"+str(e))

    # create nodetrees
    for nodetree in data["trees"]:
        createNodeTree(nodetree)            

    try:
        JSONNodetreeUtils.AfterNodeTreeCreationCallback()
    except:
        pass
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

def ntRegister():
    from bpy.utils import register_class

    print("1")

    try:
        print("__ää REGISTER:%s" % str(Custom.UI_registerClasses))
        classes.extend(Custom.UI_registerClasses)
        print("FOUND ADDITIONAL CLASSES:"+str(Custom.UI_registerClasses))
    except:
        pass

    for cls in classes:
        try:
            print("UNREGISTER:"+str(cls))
            bpy.utils.unregister_class(cls)
        except NameError as err:
            print("Name error:"+str(err))
        except KeyError as ker:
            print("KeyError:%s" % str(ker))
        except RuntimeError as rer:
            print("RuntimeError:%s" % str(rer))
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
        tb = traceback.format_exc()
        print("error:"+str(e))
        print(tb)
    
    print("REGISTER NODE-Cats:"+str(node_categories))

    nodeitems_utils.register_node_categories('CUSTOMNODES', node_categories)
    print("AFTER")


def ntUnregister():
    try:
        nodeitems_utils.unregister_node_categories('CUSTOMNODES')
    except:
        pass

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass



#if __name__ == "__main__":
#    register()
