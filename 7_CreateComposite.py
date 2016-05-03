import os

import datetime

import arcpy

masterlist = 'J:\Workspace\MasterLists\April2015Lists\CSV\MasterListESA_April2015_20151015_20151124.csv'
gdbRegions_dict = 'J:\Workspace\ESA_Species\ForCoOccur\Dict\gdbRegions_dict.csv'
outFolderCompGDB = r'J:\Workspace\ESA_Species\ForCoOccur\Composites\GDB\April_16Composites'
skipgroup = []
date = '20160502'
pdate = []
# pdate = ['201501116']
compfield = ['EntityID', 'FileName', 'NAME', 'Name_sci', 'SPCODE', 'VPCode']
while True:
    user_input = raw_input('Are you running range files Yes or No? ')
    if user_input not in ['Yes', 'No']:
        print 'This is not a valid answer'
    else:
        if user_input == 'Yes':
            RangeFolder = r"J:\Workspace\ESA_Species\ForCoOccur\Range"
            RangeFile = True
            FileType = "R_"
            filetype = '_R_'
            infolder = r"J:\Workspace\ESA_Species\ForCoOccur\Range"
            break
        else:
            CritHabFolder = r"J:\Workspace\ESA_Species\ForCoOccur\CriticalHabitat"
            RangeFile = False
            FileType = "CH_"
            filetype = '_CH_'
            infolder = r"J:\Workspace\ESA_Species\ForCoOccur\CriticalHabitat"
            break
while True:
    user_input2 = raw_input('Are you running the Lower48? Yes or No ')
    if user_input2 not in ['Yes', 'No']:
        print 'This is not a valid answer'
    else:
        if user_input2 == 'Yes':
            L48 = True
            outGDB = outFolderCompGDB + os.sep + 'L48_' + FileType + 'SpGroup_Composite.gdb'
            regiontype ="_L48_"
            break
        else:
            L48 = False
            outGDB = outFolderCompGDB + os.sep + 'NL48_' + FileType + 'SpGroup_Composite.gdb'
            regiontype = "_NL48_"
            break

arcpy.env.overwriteOutput = True  # ## Change this to False if you don't want GDB to be overwritten
arcpy.env.scratchWorkspace = ""


def CreateGDB(OutFolder, OutName, outpath):
    if not arcpy.Exists(outpath):
        arcpy.CreateFileGDB_management(OutFolder, OutName, "CURRENT")


def CreateDirectory(path_dir, outLocationCSV, OutFolderGDB):
    if not os.path.exists(path_dir):
        os.mkdir(path_dir)
        print "created directory {0}".format(path_dir)
    if not os.path.exists(outLocationCSV):
        os.mkdir(outLocationCSV)
        print "created directory {0}".format(outLocationCSV)
    if not os.path.exists(OutFolderGDB):
        os.mkdir(OutFolderGDB)
        print "created directory {0}".format(OutFolderGDB)

def createcomp (group,regionname,regiontype, regionsgdb, date, filetype,projection,outGDB):
    print "\nWorking on {0} in {1} inGDB is {2}".format(group, regionname, regionsgdb)
    Comp_FileName = regionname + filetype + group + regiontype + projection + "_" + str(date)
    filepath = outGDB + os.sep + Comp_FileName
    print filepath

    if not arcpy.Exists(filepath):
        print regionsgdb
        arcpy.env.workspace = regionsgdb
        FeatureType = "Polygon"
        wildcard = str(regionname +"_"+FileType) + "*"
        print wildcard
        fcList = arcpy.ListFeatureClasses(wildcard, FeatureType)
        print fcList
        print len(fcList)
        if len(fcList) == 0:
            pass
        else: # Setup field mappings
            pathlist =[]
            for v in fcList:
                pathfc = regionsgdb + os.sep + v
                pathlist.append(pathfc)
            skipfields = ["OBJECTID", "FID", "Shape"]
            infc = pathlist[0]

            fields = arcpy.ListFields(infc)
            fms = arcpy.FieldMappings()
            fieldname = 'FileName'
            fieldlen = 75
            for field in fields:
                if field.name in skipfields:
                     pass
                else:
                    fm = arcpy.FieldMap()
                    fm.addInputField(infc, field.name)
                    if field.name == fieldname:
                        newfield = fm.outputField
                        newfield.length = fieldlen
                        fm.outputField = newfield
                    fms.addFieldMap(fm)


            arcpy.env.workspace = outGDB
            arcpy.env.overwriteOutput = True
            arcpy.Merge_management(pathlist, filepath, fms)
            print filepath

            count = int(arcpy.GetCount_management(filepath).getOutput(0))

            if count != len(fcList):
                print "Check {0} for missing files {1} ".format(group, regionname)

            loop = datetime.datetime.now()
            print "Elapse time for loop {0}".format(loop - start_script)
    else:
        pass

start_script = datetime.datetime.now()
if not os.path.exists(outGDB):
    path, gdb = os.path.split(outGDB)
    CreateGDB(outFolderCompGDB, gdb, outGDB)

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
    pcreated = False
    if group in skipgroup:
        continue
    #print group
    groupfolder = infolder + os.sep + group + os.sep + "Regions"
    if group == "Ferns and Allies":
        group = "Ferns"
    elif group == 'Conifers and Cycads':
        group = 'Conifers'
    elif group == 'Flowering Plants':
        group = 'Plants'
    with open(gdbRegions_dict, 'rU') as inputFile2:
        for line in inputFile2:
            line = line.split(',')
            gdb = str(line[0])
            gdb = gdb.strip("\n")
            regionsplit = gdb.split("_")
            regionname = regionsplit[0]
            projection = regionsplit[1]
            projection = projection.strip('.gdb')
            regionsgdb = groupfolder + os.sep + gdb
            if not arcpy.Exists(regionsgdb):
                continue
            if L48:

                if regionname != "Lower48Only":
                    continue
                else:
                    createcomp(group,regionname,regiontype,regionsgdb,date,filetype,projection,outGDB)
            else:

                if regionname == "Lower48Only":
                    continue
                else:
                    createcomp(group,regionname,regiontype,regionsgdb,date,filetype,projection,outGDB)
end = datetime.datetime.now()
print "Elapse time {0}".format(end - start_script)
