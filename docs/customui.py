# customizing the UI
# VERY EXPERIMENTAL


#add custom properties to node
#first define a function that creates the property-description:
def UI_UrhoEngine__NavArea_props():
    return [
        {
                        "name": "auto",
                        "type": "bool",
                        "default": "true"
        }
    ]
#then add this to the Custom-class with the notation:
#Custom.UI_[TreeName]__[NodeName]_props = prop-function(name doesn't matter)
Custom.UI_props_urho3dcomponents__NavArea=UI_UrhoEngine__NavArea_props

## overwrite visual
def UI_UrhoEngine__NavArea_prop_Bounding_Box_Min(self,context,layout,propName):
    layout.label("MIXI MOXI TOXI")
    layout.prop(self,propName)
    layout.operator("nodetree.jsonload")

Custom.UI_UrhoEngine__NavArea_prop_Bounding_Box_Min=UI_UrhoEngine__NavArea_prop_Bounding_Box_Min

def UI_UrhoEngine__PlayAnimation_prop_animationFile(self,context,layout,propName):
    layout.prop(self,"absolutePath")
    if self.prop_absolutePath:
        layout.prop(self,propName)
    else:
        layout.prop_search(self, propName, bpy.data, "actions")

Custom.UI_UrhoEngine__PlayAnimation_prop_animationFile = UI_UrhoEngine__PlayAnimation_prop_animationFile

def UI_UrhoEngine__PlayAnimation_props():
    return [
        {
                        "name": "absolutePath",
                        "type": "bool",
                        "default": "false"
        }
    ]

Custom.UI_UrhoEngine__PlayAnimation_props=UI_UrhoEngine__PlayAnimation_props