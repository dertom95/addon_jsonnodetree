At the bottom a more complexe example. 
 
**nodetree-format**: 
```json
{
    "id"    : "some random unique identifier",
    "name"  : "name of the nodetree-type",
    "icon"  : "the name of the blender-icon to be shown in the nodeeditor. e.g. ERROR,BLENDER,...",
    "nodes" : [] // here the nodes that should be shown in this nodetree-type
}
```

**node-format**:
```json
{
    "id"    : "some random unique identifier",
    "name"  : "the node-type name",
    "props" : [], // properties
    "inputsockets"  : [], // the input sockets
    "outputsockets" : [] // the output sockets
}
```
 
**property-format**:
```json
{
    "name"  :   "name of the property",
    "type"  :   "type of the property", // atm: float,int,bool,string,enum,vector2,vector3,vector4,color
	"default" : "defaultvalue",
	// for number-types:
	"min"	:   -10,	// minvalue
	"max"   : 	 10,	// maxvalue
	"step"	:	  1,	// step (float: default:3 => 1/100; int=not used) 
	// subtypes:
	"subtype": "NONE",/*default*/ // "NONE","PIXEL","UNSIGNED","FACTOR","ANGLE","TIME","DISTANCE"
	// **float only** :
	"unit": "NONE",/*default*/ // "LENGTH","AREA","VOLUME","ROTATION","TIME","VELOCITY","ACCELERATION"
	"precision" : 3   //  number of decimal digits

}
```
 
Sample float (for int,bool,string same) 
```json
{"name":"fortuna","type":"float","default":1895.0}
```

Sample enum: 
```json
{"name":"Node Operation"
		,"type":"enum"
		,"elements":[ // specify the elements
				{
					"id":"AND", 
					"name":"AND-Name",
					"description":"Boolean AND-Operation",
					"icon":"FILE_MOVIE"
				},
				{
					"id":"OR",
					"name":"OR-Name",
					"description":"Boolean OR-Operation",
			 		"icon":"ARMATURE_DATA"  
				}
			]
		}
```

**socket - format**(same for in- and out-socket): 
```json 
{
    "name":"name of the socket", // the name
    "type":"the type"  // types atm: float,bool,string,vector
}
```
 
Sample(same for all types): 
```json
{"name":"floatIn","type":"float"}
```


On bigger sample with 2 NodeTrees:
```json
{"trees":[
{
"id":"org.tt.materials",
"name":"MaterialTree",
"icon":"ERROR",
"nodes":[
	{
		"id":"org.tt.Color",
		"name":"ColorNode",
		"inputsockets":[ 
			{"name":"factor","type":"float"}
		 ]
	}
]

},
{
"id":"org.tt.logictree",
"name":"LogicTree",
"icon":"BLENDER",
"nodes":[
{"id":"org.tt.boolNode"
,"name":"BoolNode"
,"inputsockets":[
	{"name":"floatIn","type":"float"},
	{"name":"boolIn","type":"bool"},
	{"name":"intIn","type":"int"}
	]
,"outputsockets":[
	{"name":"floatOut2","type":"float"},
	{"name":"boolOut","type":"bool"},
	{"name":"intOut","type":"int"}
	]
,"props":[
		{"name":"fortuna","type":"float","default":18951.0},
		{"name":"factor","type":"string","default":"Fortuna"},
		{"name":"collection","type":"string","default":"Fortuna"},
		{"name":"type"
		,"type":"enum"
		,"default":"Fortuna"
		,"elements":[
				{
					"id":"AND",
					"name":"AND-Name",
					"description":"Boolean AND-Operation",
					"icon":"FILE_MOVIE"
				},
				{
					"id":"OR",
					"name":"OR-Name",
					"description":"Boolean OR-Operation",
			 		"icon":"ARMATURE_DATA"  
				}
			]
		}
	]
}
,
{"id":"org.tt.MathNode"
,"name":"MathNode"
,"inputsockets":[
	{"name":"A1","type":"float"},
	{"name":"B","type":"float"}
	]
,"outputsockets":[
	{"name":"result","type":"float"}
	]
,"props":[
		{"name":"type"
		,"type":"enum"
		,"elements":[
				{
					"id":"ADD",
					"name":"ADD",
					"description":"Add two values"
				},
				{
					"id":"DIV",
					"name":"DIV",
					"description":"Div two values"
				},
				{
					"id":"MUL",
					"name":"MUL",
					"description":"MUL two values"
				},
				{
					"id":"SUB",
					"name":"SUB",
					"description":"Sub two values"
				}
			]
		}
	]
}


]}
]}
```
