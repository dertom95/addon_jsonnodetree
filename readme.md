**JSON-Nodetree**

This blender-addon let you define simple nodetree-definitions via json

**Disclaimer**
This addon is highly experimental. Although it works most of the time consider it 'proof of concept'

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
                        {"name":"floatProp","type":"float","default":1895.0}
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
    ]
}
```
 
**Install** 
 
Animated gif: see [Install](docs/install.gif)  
 
**INPUT-Format** 
 
see [docs/inputformat.md](docs/inputformat.md)
 
**Usage** 
 
* Open compositing-tab
* Choose MISC
* Search 'JSON-Nodetree-Loader'
* select Nodetree-JSON-File in path-Field
* Load
* Add nodetrees to objects
* Export as JSON, which will export all links and component-data != default (afaik)

**Getting Started - Video** 

[![Getting Started](https://img.youtube.com/vi/P0d4nAOIOVI/0.jpg)](https://www.youtube.com/watch?v=P0d4nAOIOVI)
