import os
import datetime

import arcpy

Range = True
masterlist = 'J:\Workspace\MasterLists\CSV\MasterListESA_April2015_20151015_20151118.csv'

if Range:
    infolder = 'J:\Workspace\ESA_Species\Range\NAD83'
    outGDBFolder = "J:\Workspace\ESA_Species\Range\NAD83_SinglePart"
else:
    infolder = 'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final'
    outGDBFolder = "J:\Workspace\ESA_Species\CriticalHabitat\NAD83_SinglePart"

skip =[]

def fcs_in_workspace(workspace):
    arcpy.env.workspace = workspace
    for fc in arcpy.ListFeatureClasses():
        yield (fc)
    for ws in arcpy.ListWorkspaces():
        for fc in fcs_in_workspace(ws):
            yield fc


def CreateGDB(OutFolder, OutName, outpath):
    if not arcpy.Exists(outpath):
        arcpy.CreateFileGDB_management(OutFolder, OutName, "CURRENT")

def CreateDirectory(OutFolderGDB):

    if not os.path.exists(OutFolderGDB):
        os.mkdir(OutFolderGDB)
        print "created directory {0}".format(OutFolderGDB)

start_script = datetime.datetime.now()
print "Script started at {0}".format(start_script)

grouplist = []

with open(masterlist, 'rU') as inputFile:
    header = next(inputFile)
    for line in inputFile:
        line = line.split(',')
        group = line[1]
        grouplist.append(group)
inputFile.close()

unq_grps = set(grouplist)
alpha_group = sorted(unq_grps)

for group in alpha_group:
    if group in skip:
        continue
    print "Current group is {0}".format(group)
    gdb =str(group) + '.gdb'
    #print gdb
    if not os.path.exists(outGDBFolder):
        CreateDirectory(outGDBFolder)
    outpath = str(outGDBFolder) + os.sep + str(group) + '.gdb'
    #print outpath
    if not arcpy.Exists(outpath):
        CreateGDB(outGDBFolder, gdb, outpath)

    group_gdb = infolder + os.sep + str(group) + '.gdb'

    arcpy.env.workspace = group_gdb
    fclist = arcpy.ListFeatureClasses()
    total = len(fclist)
    entlist_fc = []
    for fc in fclist:
        infile = group_gdb + os.sep + fc
        outfile = outGDBFolder + os.sep + str(group) + '.gdb' + os.sep + fc
        if not arcpy.Exists(outfile):
            print "Generate SinglePart for {0} remaining files {1}  {2}".format(fc,total,group)
            total -= 1
            arcpy.MultipartToSinglepart_management(infile, outfile)
        else:
            continue
    print "Current group is {0}".format(group)

end = datetime.datetime.now()
print "Elapse time {0}".format(end - start_script)
