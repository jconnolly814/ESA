import os

import arcpy


# TODO generate table first then repait based on table

# inpout folder or GDB- will look through all GDBs if it is a folder as a list, can be multiple locations
# inlocation = ['J:\Workspace\ESA_Species\ForCoOccur\Range\Corals',
#             'J:\Workspace\ESA_Species\ForCoOccur\Range\Crustaceans',
#            'J:\Workspace\ESA_Species\ForCoOccur\Range\Ferns and Allies',
#           'J:\Workspace\ESA_Species\ForCoOccur\Range\Fishes',
#          ,
inlocation = ['J:\Workspace\ESA_Species\ForCoOccur\Range\Corals\Regions\AS_WGSUTMZone2S.gdb'

              ]

inlocation = ['J:\Workspace\ESA_Species\Range\NAD83\Corals.gdb']
# J:\Workspace\ESA_Species\ForCoOccur\Composites\GDB\April_16Composites\WebApp\R_WebApp_Composite.gdb

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
