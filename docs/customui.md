**Custom-UI**

If jsonNodetree does not meet the requirements, it is possible to override every property draw-call and even possible to add properties in the class and draw them. There is a naming convention to find the right name for the hooks. See below.

Why would you want to do it? Add custom logic or maybe the nodetree is generated and you want to some nodes custom input wihtout the need to alter the generator and the data it is based on....

You can enable "output called hooks" in the JSON-Nodetrees settings (Compositing->'Misc'-Sidebar) to output all actually called hooks to stdout. (Add a node to the nodetree and move the mouse over the nodetree-space and watch the console explode with output )


**Caution**: as everything else this is highly experimental and not that well tested
-----------



**ON THE NODE**
properties: 

```
Custom.UI_[NODEID]_[propertyName](self,context,layout,propName)
```

Additional draw-calls: 

```
Custom.UI_[NODEID](self,context,layout,propName)
``` 


**ON THE SIDEBAR**

properties: 

```
Custom.UI_sidebar_[NODEID]_[propertyName](self,context,layout,propName)
```

Additional draw-calls:
```json
Custom.UI_sidebar_[NODEID](self,context,layout,propName)
``` 

**ADDITIONAL PROPERTIES**: 
```json
CUSTOM.UI_props_[NODEID]=[ { /*property-definition like in the nodetree.json*/ },... ]
```

**ADDITIONAL CLASSES TO BE REGISTERED**
```
CUSTOM.UI_registerclasses=[/*the classes*/]

```


