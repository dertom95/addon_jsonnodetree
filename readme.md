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

TODO

Usage:

* Open node-editor sidebar(right)
* scroll to 'JSON-Nodetree'
* select Nodetree-JSON-File
* Load