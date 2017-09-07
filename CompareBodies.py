#Author-Fabian
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math
import os

commandId = 'CompareBodies'
commandName = 'Compare'
commandDescription = 'Compare command input examples.'
rowNumber = 0

# Global set of event handlers to keep them referenced for the duration of the command
handlers = []

'''
compares two BRepBodies by their surface area
'''
def compareBRepBodiesByArea(firstBRepBody, secondBRepBody):
    return math.isclose(firstBRepBody.area,secondBRepBody.area)

'''
compares two BRepBodies by their volume
'''   
def compareBRepBodiesByVolume(firstBRepBody, secondBRepBody):
    return math.isclose(firstBRepBody.volume,secondBRepBody.volume)

''' 
addButtonOnClick(isMulti) opens a FileDialog and returns the users selections
boolean isMulti enables multi selections in the dialog if True
returns number of Files loaded into new components in current design
'''    
def addButtonOnClick(isMulti):
    global app
    design = adsk.fusion.Design.cast(app.activeProduct)
    
    #Create FileDialog
    dialog = ui.createFileDialog()
    dialog.isMultiSelectEnabled = isMulti
    dialog.filter = 'Fusion Archive (*.f3d)'
    dialog.initialDirectory = os.path.expanduser('~/Documents/')
    if dialog.showOpen() != adsk.core.DialogResults.DialogOK:
        return

    return dialog.filenames

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

'''
compares two vertices by also considers the centerOfMass difference (only when volume is equal)
'''
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

'''
prints vertices of a face in a messageBox
'''
def printVertices(face):
    res = ""
    res += str(face.vertices.count) + "\n"
    for i in range(0,face.vertices.count):
        res += str(i) + " "
        res += str(face.vertices.item(i).geometry.asArray()) + "\n"
    ui.messageBox(res)

'''
compares two BRepBodies by their faces
iterates through all faces and gets all vertices of each face
adds the array of vertices of a face to another array called firstFaces
iterate faces from BRep 1 and compares its vertices with the ones from BRep 2
'''
def compareBRepBodiesByFaces(firstBRepBody, secondBRepBody):
    volumeIsEqual = compareBRepBodiesByVolume(firstBRepBody,secondBRepBody)
    #how to get differences of bodies with different faces count?    
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
    #ui.messageBox("difference center of mass:\nx: "+str(diff[0])+"\ny: "+str(diff[1])+"\nz: "+str(diff[2]))
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
        
    #if not isEqual:
    #    secondBRepBody.isLightBulbOn = False
    return isEqual


class CompareExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
           command = args.firingEvent.sender                  
           inputs = command.commandInputs
           
           global documents
           
           product = app.activeProduct
           design = adsk.fusion.Design.cast(product)
            
           rootComp = design.rootComponent
           
           selectionRootInput = inputs.itemById(commandId + '_selection_root')
           selectionSecondInput = inputs.itemById(commandId + '_selection_second')
           
           textBoxInput = inputs.itemById(commandId + '_textBox')
           
           isMultiInput = inputs.itemById(commandId + '_multi')
           res = ""
           if selectionRootInput.selectionCount == 1 and selectionSecondInput.selectionCount == 1 and not isMultiInput.value:
               firstBase = selectionRootInput.selection(0).entity
               secondBase = selectionSecondInput.selection(0).entity
               checkArea = compareBRepBodiesByArea(firstBase,secondBase)
               checkVolume = compareBRepBodiesByVolume(firstBase,secondBase)
               checkFaces = compareBRepBodiesByFaces(firstBase,secondBase)
               res = "Area: "+str(checkArea)+ "\nVolume: " + str(checkVolume)+ "\nFaces: " + str(checkFaces)
               textBoxInput.formattedText = res
           if selectionRootInput and isMultiInput.value and len(documents) > 1:
               res = "number documents: " + str(len(documents)) + "\n"
               firstBase = selectionRootInput.selection(0).entity
               for document in documents[:]:
                   docDesign = adsk.fusion.Design.cast(document.products.itemByProductType('DesignProductType'))
                   docBodies = docDesign.rootComponent.bRepBodies
                   res += 'imported document {} with {} bodies\n'.format(document.name, docBodies.count)
                   if docDesign.rootComponent.bRepBodies.count == 1:
                       secondBase = docBodies.item(0)
                       checkArea = compareBRepBodiesByArea(firstBase,secondBase)
                       checkVolume = compareBRepBodiesByVolume(firstBase,secondBase)
                       checkFaces = compareBRepBodiesByFaces(secondBase,firstBase)
                       res += "Area: "+str(checkArea)+ "\nVolume: " + str(checkVolume)+ "\nFaces: " + str(checkFaces) + "\n"
                       diff = getCoMDifference(secondBase,firstBase)
                       res += "difference center of mass:\nx: "+str(diff[0])+"\ny: "+str(diff[1])+"\nz: "+str(diff[2]) + "\n"
                   textBoxInput.formattedText = res
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CompareCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
           global prevButtonState
           global filesToImport
           global documents
           global rootDocument
           
           command = args.firingEvent.sender   
           cmdInput = args.input                   
           inputs = command.commandInputs
           
           product = app.activeProduct
           
           design = adsk.fusion.Design.cast(product)
            
           rootComp = design.rootComponent
           
           secondSelectionInput = inputs.itemById(commandId + '_selection_second')
           
           isMultiInput = inputs.itemById(commandId + '_multi')
           if isMultiInput.value:
               secondSelectionInput.clearSelection()
               secondSelectionInput.isVisible = False
           else:
               secondSelectionInput.isVisible = True
           
           addButtonInput = inputs.itemById(commandId + '_add')
           if prevButtonState != addButtonInput.value:
               filesToImport = addButtonOnClick(isMultiInput.value)
               ui.messageBox("Import Files: "+str(filesToImport))
               countFiles = 0
               #import selected files
               for filename in filesToImport:
                   # Get import manager 
                   importManager = app.importManager
                   countFiles = countFiles + 1
                   # Get archive import options
                   archiveOptions = importManager.createFusionArchiveImportOptions(filename)
                   
                   # Import archive file to root component
                   importedDocument = importManager.importToNewDocument(archiveOptions)
                   documents.append(importedDocument)
               filesToImport = []
                   
                   #importManager.importToTarget(archiveOptions, newComponent)
               #ui.messageBox("Imported: " + str(countFiles))
               #rootDocument.activate() crashes Fusion
       
           if addButtonInput:
               prevButtonState = addButtonInput.value
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
            selectionInput = inputs.addSelectionInput(commandId + '_selection_root', 'Root Body', 'Basic select command input')
            selectionInput.setSelectionLimits(1,1)
            selectionInput.addSelectionFilter("SolidBodies")
            
            #Create selection for design in current directory
                        
            # Create selection input
            selectionInput = inputs.addSelectionInput(commandId + '_selection_second', 'Second Body', 'Basic select command input')
            selectionInput.setSelectionLimits(1,1)
            selectionInput.addSelectionFilter("SolidBodies")
            
            isMultiInput = inputs.addBoolValueInput(commandId + '_multi', 'Multible Bodies', True, '', False)
            
            addButtonInput = inputs.addBoolValueInput(commandId + '_add', 'Import Body', False, './resources/button/', True)
            #addButtonInput.text = "Use F3D"
            #addButtonInput.isFullWidth = False
            #tableInput.addToolbarCommandInput(addButtonInput)
            
            #CompareSettings group input
            groupCmdInput = inputs.addGroupCommandInput('group', 'Compare Settings')
            groupCmdInput.isExpanded = False
            #groupCmdInput.isEnabledCheckBoxDisplayed = True
            groupChildInputs = groupCmdInput.children
            
            checkAreaInput = groupChildInputs.addBoolValueInput(commandId + '_area', 'Area', True, '', True)
            checkVolumeInput = groupChildInputs.addBoolValueInput(commandId + '_volume', 'Volume', True, '', True)
            checkFacesInput = groupChildInputs.addBoolValueInput(commandId + '_faces', 'Face properties', True, '', True)
            
            #Create a TextBox for displaying results
            textBoxInput = inputs.addTextBoxCommandInput(commandId + '_textBox', ' ', 'To be calculated', 10, True)
            textBoxInput.isFullWidth = True
            
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
        global rootDocument
        
        rootDocument = app.activeDocument

        global commandId
        global commandName
        global commandDescription
        
        global prevButtonState
        prevButtonState = True
        
        global filesToImport
        filesToImport = []
        
        global documents
        documents = []
        
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