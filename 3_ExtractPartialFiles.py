import datetime
import os

import arcpy

masterlist = 'C:\Users\Admin\Documents\Jen\Workspace\MasterLists\CSV\MasterListESA_April2015_20151015_20151124.csv'
regionsgdb_csv = r'C:\Users\Admin\Documents\Jen\Workspace\ESA_Species\BySpeciesGroup\ForCoOccur\Dict\regionsgdb.csv'
inFishnets = 'C:\Users\Admin\Documents\Jen\Workspace\ESA_Species\BySpeciesGroup\ForCoOccur\Composites\GDB\Fishnets_NAD83.gdb'

infolder = 'C:\Users\Admin\Documents\Jen\Workspace\ESA_Species\BySpeciesGroup\ForCoOccur\CriticalHabitat'
skiplist = []

PossAnswers = ['Yes', 'No']

user_input = raw_input('Are you running range files? Yes or No ')
if user_input not in PossAnswers:
    print 'This is not a valid answer'

else:
    if user_input == 'Yes':
        infolder = 'J:\Workspace\ESA_Species\ForCoOccur\Range'
        print 'Running range files output will be located at {0}'.format(infolder)
    else:
        infolder = 'J:\Workspace\ESA_Species\ForCoOccur\CriticalHabitat'
        print 'Running critical habitat files output will be located at {0}'.format(infolder)

gdblist = ["SingleNonLower48only.gdb", "SingleBoth.gdb"]


def CreateDirectory(DBF_dir):
    if not os.path.exists(DBF_dir):
        os.mkdir(DBF_dir)


def CreateGDB(OutFolder, OutName, outpath):
    if not arcpy.Exists(outpath):
        arcpy.CreateFileGDB_management(OutFolder, OutName, "CURRENT")


def fcs_in_workspace(workspace):
    arcpy.env.workspace = workspace
    for fc in arcpy.ListFeatureClasses():
        yield (fc)
    for ws in arcpy.ListWorkspaces():
        for fc in fcs_in_workspace(ws):
            yield fc


start_script = datetime.datetime.now()
print "Started: {0}".format(start_script)
grouplist = []
AK = []
AS = []
CNMI = []
GU = []
HI = []
Lower48 = []
PR = []
VI = []
with open(masterlist, 'rU') as inputFile:
    header = next(inputFile)
    for line in inputFile:
        line = line.split(',')
        entid = line[0]
        group = line[1]
        grouplist.append(group)

inputFile.close()

unq_grps = set(grouplist)
alpha_group = sorted(unq_grps)

for group in alpha_group:
    if group in skiplist:
        continue

    print "\nWorking on {0}".format(group)

    for fish in fcs_in_workspace(inFishnets):
        print "Working with {0}".format(fish)

        arcpy.Delete_management("fish_lyr")
        infish = inFishnets + os.sep + fish
        arcpy.MakeFeatureLayer_management(infish, "fish_lyr")

        resultfolder = infolder + os.sep + group

        regionsDIR = resultfolder + os.sep + "Regions"
        CreateDirectory(regionsDIR)

        NAD83DIR = regionsDIR + os.sep + 'NAD83'
        CreateDirectory(NAD83DIR)

        region = fish.split("_")
        region = str(region[0])
        # print region
        with open(regionsgdb_csv, 'rU') as inputFile2:
            for line in inputFile2:
                line = line.split(',')
                fishnet = line[0]
                if fishnet == fish:
                    # print fishnet
                    outgbdname = str(line[1])
                    # print outgbdname
                    list2 = str(line[2])
                    list2 = list2.strip("\n")
                else:
                    continue
        inputFile2.close()

        regionGDB = outgbdname
        outpathgdb = NAD83DIR + os.sep + regionGDB

        if not arcpy.Exists(outpathgdb):
            CreateGDB(NAD83DIR, regionGDB, outpathgdb)

        for value in gdblist:
            inGDB = resultfolder + os.sep + value
            for fc in fcs_in_workspace(inGDB):

                arcpy.Delete_management("fc_lyr")
                infc = inGDB + os.sep + fc
                arcpy.MakeFeatureLayer_management(infc, "fc_lyr")
                arcpy.SelectLayerByLocation_management("fc_lyr", 'intersect', "fish_lyr", "#", "NEW_SELECTION")
                arcpy.Delete_management("sel_lyr")
                arcpy.MakeFeatureLayer_management("fc_lyr", "sel_lyr")
                count = int(arcpy.GetCount_management("sel_lyr").getOutput(0))
                if count > 0:
                    outfc = outpathgdb + os.sep + region + "_" + str(fc)
                    if not arcpy.Exists(outfc):
                        arcpy.CopyFeatures_management("fc_lyr", outfc)
                        vars()[list2].append(fc)
                        print "Export regional file for {0}".format(fc)
                else:
                    continue
print "species in AK {0}".format(AK)
print "species in AS {0}".format(AS)
print "species in CNMMI {0}".format(CNMI)
print "species in GU {0}".format(GU)
print "species in HI {0}".format(HI)
print "species in PLower48 {0}".format(Lower48)
print "species in PR {0}".format(PR)
print "species in VI {0}".format(VI)

print "Script completed in: {0}".format(datetime.datetime.now() - start_script)
