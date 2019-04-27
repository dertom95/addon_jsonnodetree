# customizing the UI
# VERY EXPERIMENTAL


Custom.UI_props_urho3dcomponents__CNavigationMesh = [
        {
            "name": "Shape Type",
            "type": "enum",
            "elements": [
                {
                    "id": "Box",
                    "name": "Box",
                    "description": "Box",
                    "icon": "COLOR",
                    "number": "0"
                },
                {
                    "id": "Sphere",
                    "name": "Sphere",
                    "description": "Sphere",
                    "icon": "COLOR",
                    "number": "0"
                },
                {
                    "id": "StaticPlane",
                    "name": "StaticPlane",
                    "description": "StaticPlane",
                    "icon": "COLOR",
                    "number": "0"
                }
            ],
            "default": "0"
        }
]

def UI_urho3dcomponents__CNavigationMesh(self,context,layout,propName):
    layout.label(text="FORTUNA")
    layout.operator("object.simple_operator")
    
Custom.UI_urho3dcomponents__CNavigationMesh_prop_debug_color=UI_urho3dcomponents__CNavigationMesh

class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        print("FORTUNA FORTUNA")
        return {'FINISHED'}

Custom.UI_registerClasses=[SimpleOperator]