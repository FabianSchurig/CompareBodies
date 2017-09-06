#Author-Fabian
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

commandId = 'CompareBodies'
commandName = 'Compare'
commandDescription = 'Compare command input examples.'
rowNumber = 0

# Global set of event handlers to keep them referenced for the duration of the command
handlers = []

def compareBRepBodiesByArea(firstBRepBody, secondBRepBody):
    return math.isclose(firstBRepBody.area,secondBRepBody.area)
    
def compareBRepBodiesByVolume(firstBRepBody, secondBRepBody):
    return math.isclose(firstBRepBody.volume,secondBRepBody.volume)

'''
compare vertices [Vertex1,Vertex2,Vertex3,Vertex4] [Vertex1,Vertex2,Vertex3,Vertex4]
'''
def compareVerticesList(firstVertices, secondVertices, comDifference):    
    for first in firstVertices:
        res = False
        for second in secondVertices:
            if compareVertices(first, second, comDifference):#first.geometry.isEqualTo(second.geometry):#                                
                res = True
                break
        if not res:
            return False
    return True

def compareVertices(firstVertex,secondVertex, comDifference):
    #ui.messageBox(str(firstVertex.geometry.x) + " " + str(firstVertex.geometry.y) + " " + str(firstVertex.geometry.z) + "\n" + str(secondVertex.geometry.x) + " " + str(secondVertex.geometry.y) + " " + str(secondVertex.geometry.z))    
    if math.isclose(firstVertex.geometry.x,secondVertex.geometry.x + comDifference[0], abs_tol=1e-09) and math.isclose(firstVertex.geometry.y,secondVertex.geometry.y + comDifference[1], abs_tol=1e-09) and math.isclose(firstVertex.geometry.z,secondVertex.geometry.z + comDifference[2], abs_tol=1e-09):
        return True
    return False

''' Center of Mass/ CoM difference of two BRepBodies'''
def getCoMDifference(firstBRep,secondBRep):
    diff = []
    #(returnValue, xAxis, yAxis, zAxis) = firstBRep.physicalProperties.getPrincipalAxes()
    #ui.messageBox("x: "+str(xAxis.asArray()) +"\ny:"+str(yAxis.asArray()) + "\nz: "+str(zAxis.asArray()) )
    #(returnValue, xAxis, yAxis, zAxis) = secondBRep.physicalProperties.getPrincipalAxes()
    #ui.messageBox("x: "+str(xAxis.asArray()) +"\ny:"+str(yAxis.asArray()) + "\nz: "+str(zAxis.asArray()) )
    #ui.messageBox("first: "+str(firstBRep.physicalProperties.getRotationToPrincipal()) + "\nsecond: "+str(secondBRep.physicalProperties.getRotationToPrincipal()))
    diff.append(firstBRep.physicalProperties.centerOfMass.x - secondBRep.physicalProperties.centerOfMass.x)
    diff.append(firstBRep.physicalProperties.centerOfMass.y - secondBRep.physicalProperties.centerOfMass.y)
    diff.append(firstBRep.physicalProperties.centerOfMass.z - secondBRep.physicalProperties.centerOfMass.z)
    return diff

def printVertices(face):
    res = ""
    res += str(face.vertices.count) + "\n"
    for i in range(0,face.vertices.count):
        res += str(i) + " "
        res += str(face.vertices.item(i).geometry.asArray()) + "\n"
    ui.messageBox(res)

def compareBRepBodiesByFaces(firstBRepBody, secondBRepBody):
    volumeIsEqual = compareBRepBodiesByVolume(firstBRepBody,secondBRepBody)
    if firstBRepBody.faces.count != secondBRepBody.faces.count:
        return False
    firstFaces = []
    secondFaces = []
    for i in range(0,firstBRepBody.faces.count):
        firstVertices = []
        secondVertices = []
        #printVertices(firstBRepBody.faces.item(i))
        for j in range(0, firstBRepBody.faces.item(i).vertices.count):
            firstVertices.append(firstBRepBody.faces.item(i).vertices.item(j))         
            secondVertices.append(secondBRepBody.faces.item(i).vertices.item(j))
        secondFaces.append(secondVertices)
        firstFaces.append(firstVertices)
    isEqual = True
    i = 0
    
    #if volume is equal the translation can be calculated by the center of mass
    if volumeIsEqual:
        diff = getCoMDifference(firstBRepBody,secondBRepBody)
    else:
        diff = [0,0,0]
    ui.messageBox("difference center of mass:\nx: "+str(diff[0])+"\ny: "+str(diff[1])+"\nz: "+str(diff[2]))
    for first in firstFaces:
        
        res = False
        for second in secondFaces:
            if compareVerticesList(first, second, diff):
                res = True
                break
            
        if not res:
            isEqual = False
            firstBRepBody.faces.item(i).appearance = libAppear
            #ui.messageBox(str(i))
        i += 1
        
    if not isEqual:
        secondBRepBody.isLightBulbOn = False
    return isEqual

class CompareExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
           command = args.firingEvent.sender                  
           inputs = command.commandInputs
           
           selectionInput = inputs.itemById(commandId + '_selection')
           
           if selectionInput.selectionCount == 2:
               firstBase = selectionInput.selection(0).entity
               secondBase = selectionInput.selection(1).entity
               print(str(compareBRepBodiesByArea(firstBase,secondBase)))

               ui.messageBox("Area: "+ str(compareBRepBodiesByArea(firstBase,secondBase)) + "\nVolume:" + str(compareBRepBodiesByVolume(firstBase,secondBase)) + "\nFaces: " + str(compareBRepBodiesByFaces(firstBase,secondBase)))
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CompareCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
           command = args.firingEvent.sender   
           cmdInput = args.input                   
           inputs = command.commandInputs 
           
           addButtonInput = inputs.itemById(commandId + '_add')
           print(str(addButtonInput.value))
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
class CompareCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers         
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CompareCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            
            onExecute = CompareExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
            onExecutePreview = CompareExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            handlers.append(onExecutePreview)
            
            onDestroy = CompareCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # Keep the handler referenced beyond this function
            handlers.append(onDestroy)
            
            onInputChanged = CompareCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)
            
            
            inputs = cmd.commandInputs
            global commandId
            
            # Create selection input
            selectionInput = inputs.addSelectionInput(commandId + '_selection', 'Select', 'Basic select command input')
            selectionInput.setSelectionLimits(0)
            selectionInput.addSelectionFilter("SolidBodies")
            
            #Create selection for design in current directory
            
            addButtonInput = inputs.addBoolValueInput(commandId + '_add', ' ', False, '', True)
            addButtonInput.text = "Körper auswählen"
            addButtonInput.isFullWidth = True
            #tableInput.addToolbarCommandInput(addButtonInput)
            
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    ui = None
    try:
        global app        
        app = adsk.core.Application.get()
        global ui        
        ui = app.userInterface

        global commandId
        global commandName
        global commandDescription
        
        global libAppear
        # Get a reference to an appearance in the library.
        lib = app.materialLibraries.item(2) 
        #ui.messageBox(str(app.materialLibraries.count))
        
        #for i in range(0,app.materialLibraries.count):
            #ui.messageBox(str(app.materialLibraries.item(i).name))
        
        #ui.messageBox(str(app.materialLibraries.item(2).appearances.count))

        #ree = ""
        #for i in range(0,lib.appearances.count):
        #    ree += str(i) + " " + str(lib.appearances.item(i).name) + "\n"
            
        #ui.messageBox(ree)
        libAppear = lib.appearances.item(92)

        # Create command defintion
        cmdDef = ui.commandDefinitions.itemById(commandId)
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription)

        # Add command created event
        onCommandCreated = CompareCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # Keep the handler referenced beyond this function
        handlers.append(onCommandCreated)

        # Execute command
        cmdDef.execute()

        # Prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))