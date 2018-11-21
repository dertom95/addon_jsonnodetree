class Custom:
    def UI_TomEngine__NavArea_props():
        return [
            {
							"name": "auto",
							"type": "bool",
							"default": "true"
			}
        ]


    def UI_TomEngine__NavArea_prop_Bounding_Box_Min(self,context,layout,propName):
        layout.label("MIXI MOXI TOXI")
        layout.prop(self,propName)
        layout.operator("nodetree.jsonload")
