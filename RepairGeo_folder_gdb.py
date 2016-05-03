import arcpy
import os

# inpout folder or GDB- will look through all GDBs if it is a folder as a list, can be multiple locations
inlocation = ['J:\Workspace\ESA_Species\ForCoOccur\Range\Amphibians\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Arachnids\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Birds\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Clams\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Conifers and Cycads\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Corals\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Crustaceans\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Ferns and Allies\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Flowering Plants\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Insects\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Lichens\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Mammals\Regions'
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Reptiles\Regions',
              'J:\Workspace\ESA_Species\ForCoOccur\Range\Snails\Regions']


def fcs_in_workspace(workspace):
    arcpy.env.workspace = workspace
    for fc in arcpy.ListFeatureClasses():
        yield (fc)
    for ws in arcpy.ListWorkspaces():
        for fc in fcs_in_workspace(ws):
            yield fc


def checkgeo(ingdb):
    for fc in fcs_in_workspace(ingdb):
        print "\nProcessing " + fc
        lyr = 'temporary_layer'

        arcpy.MakeFeatureLayer_management(fc, lyr)
        arcpy.RepairGeometry_management(lyr)
        print(arcpy.GetMessages(0))
        arcpy.Delete_management(lyr)


for value in inlocation:
    path, tail = os.path.split(value)

    if tail.endswith('.gdb'):
        inGDB = value
        checkgeo(inGDB)
    else:
        gdblist = os.listdir(value)
        for v in gdblist:
            if v.endswith('.gdb'):
                inGDB = value
                checkgeo(inGDB)
            else:
                continue
