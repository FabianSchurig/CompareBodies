# CompareBodies
Fusion 360 Script to compare bodies

An Autodesk Screencast showing how to compare different Bodies.
[![image](https://user-images.githubusercontent.com/11216482/30242206-9728a476-9592-11e7-9d6e-075b92cf4b68.png)](https://screencast.autodesk.com/Embed/Timeline/5a09383f-236c-4b92-b04b-fb22d3fbc89c)

### Logic and Documentation
#### Compare BRep Bodies by Area 
Method ``` compareBRepBodiesByArea(firstBRepBody, secondBRepBody) ```  
Use the property ``` BRepBody.area ``` and ``` math.isClose() ``` to compare two BRep Bodies by their surface area.  
Returns True if the Area is the same.
#### Compare BRep Bodies by Volume
Method ``` compareBRepBodiesByVolume(firstBRepBody, secondBRepBody) ```  
Use the property ``` BRepBody.volume ``` and ``` math.isClose() ``` to compare two BRep Bodies by their volume.  
Returns True if the Volume is the same.
#### Compare BRep Bodies by Faces
Method ``` compareBRepBodiesByFaces(firstBRepBody, secondBRepBody) ```  
A BRepBody ```(firstBRepBody, secondBRepBody)``` has BRepFaces.  
A BRepFace has BRepVertices.  
I can get a Point3D Object with ```BRepVertex.geometry```  
A Point3D Object has a method called ```.asArray()```, which returns ```(x,y,z)``` and also properties for x,y,z coordinates.
Iterate through all Faces of each Body and get all Vertices. Store the Vertices coordinates in an Array of Faces where a Face is an Array of Vertices and where a Vertex is an Array of x,y,z Coordinates.  
Data Structure:  
``` {Face1,Face2,...,FaceN} -> {{Vertex1,Vertex2,...,VertexN},...,FaceN} -> {{{x1,y1,z1},{x2,y3,z2},...,PointN},{x1,y1,z1},{x2,y3,z2},...,PointN},...,VertexN},...,FaceN} ```  
Iterate through all BRepFaces of the firstBRepBody. For every BRepFace of the firstBrepBody iterate through all BRepFaces of secondBRepBody and call ```compareVerticesList(first,second,diff)```
Breaks if the BRepFaces match each other. If there is no matching face from firstBRepBody to a face of the second BRepBody the current face will be colored.   
Returns False if one face of firstBRepBody is not matching with a face in secondBRepBody.

#### Compare Vertices
Method ``` compareVertices(firstVertex, secondVertex, comDifference) ```
- ```comDifference``` is an Array of the center of mass difference ```{x,y,z}``` (should be ```{0,0,0}``` if the volume is not the same)

#### Compare Vertices List
TBD

#### Compare all Bodies in a Document
TBD
