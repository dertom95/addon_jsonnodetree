**JSON-Nodetree**

This blender-addon let you define simple nodetree-definitions via json

Sample:
```json
{
    "trees":[
    {
        "id":"org.tt.materials",
        "name":"MaterialTree",
        "icon":"ERROR",
        "nodes":[
            {
                "id":"org.tt.Color",
                "name":"ColorNode",
                "props":[
                    {"name":"floatProp","type":"float","default":1895.0},    
                ],
                "inputsockets":[ 
                    {"name":"factor","type":"float"}
                ],
                "outputsockets":[ 
                    {"name":"result","type":"float"}
                ]
            }
        ]
    }
}
```
 
**Install**

Animated gif: see docs/install.gif 

**INPUT-Format**
see docs/inputformat.md


Usage:

* Open compositing-tab
* Choose MISC
* Search 'JSON-Nodetree-Loader'
* select Nodetree-JSON-File in path-Field
* Load
* Add nodetrees to objects
* Export as JSON, which will export all links and component-data != default (afaik)

