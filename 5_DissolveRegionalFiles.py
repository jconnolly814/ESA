import os
import csv
import datetime

import arcpy

dissolveFields = ['NAME', 'Name_sci', 'SPCode', 'VIPCode', 'FileName', 'EntityID']

masterlist = 'J:\Workspace\MasterLists\CSV\MasterListESA_April2015_20151015_20151124.csv'

gdbRegions_dict = 'J:\Workspace\ESA_Species\ForCoOccur\Dict\gdbRegions_dict.csv'

skipgroup = []
skipregions= []

while True:
    user_input = raw_input('Are you running range files Yes or No? ')
    if user_input not in ['Yes', 'No']:
        print 'This is not a valid answer'
    else:
        if user_input == 'Yes':
            infolder = 'J:\Workspace\ESA_Species\ForCoOccur\Range'

            proj_Folder = 'J:\Workspace\projections'
            print 'Running range files output will be located at {0}'.format(infolder)
            break
        else:
            infolder = 'J:\Workspace\ESA_Species\ForCoOccur\CriticalHabitat'

            proj_Folder = 'J:\Workspace\projections'
            print 'Running critical habitat files output will be located at {0}'.format(infolder)
            break


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


def create_outtable(listname, csvlocation):
    with open(csvlocation, "wb") as output:
        writer = csv.writer(output, lineterminator='\n')
        for val in listname:
            writer.writerow([val])


def createdicts(csvfile):
    with open(csvfile, 'rb') as dictfile:
        group = csv.reader(dictfile)
        dictname = {rows[0]: rows[1] for rows in group}
        return dictname


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


arcpy.env.overwriteOutput = True  # ## Change this to False if you don't want GDB to be overwritten
arcpy.env.scratchWorkspace = ""
start_script = datetime.datetime.now()

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
    if group in skipgroup:
        continue
    groupfolder = infolder + os.sep + group + os.sep + "Regions"
    with open(gdbRegions_dict, 'rU') as inputFile2:
        for line in inputFile2:
            line = line.split(',')
            gdb = str(line[0])
            gdb = gdb.strip("\n")
            regionsgdb = groupfolder + os.sep + "ProjectedSinglePart" + os.sep + gdb
            print regionsgdb
            if not arcpy.Exists(regionsgdb):
                continue
            else:

                regionname = gdb.split("_")
                regionname = regionname[0]
                if regionname in skipregions:
                    continue
                # print regionname
                print "\nWorking on {0} in {1}".format(group, regionname)
                arcpy.env.workspace = regionsgdb
                # print InGDB
                fcList = arcpy.ListFeatureClasses()
                total = len(fcList)
                if total == 0:
                    print "There are no {1} species in {0}".format(regionname, group)
                    continue
                else:
                    outgdb_name = gdb.strip('\n')
                    outGDB = groupfolder + os.sep + outgdb_name
                    if not arcpy.Exists(outGDB):
                        print outGDB
                        CreateGDB(groupfolder, outgdb_name, outGDB)
                    else:
                        arcpy.env.workspace = outGDB
                        fcList2 = arcpy.ListFeatureClasses()
                        total2 = len(fcList2)
                        if total == total2:
                            print "\nAll {0} species files Dissolved in {1}".format(group, regionname)
                            continue
                        else:
                            arcpy.env.workspace = regionsgdb


                    # print regionsgdb
                    for fc in fcList:
                        #print fc
                        outgdb_name = gdb.strip('\n')



                        infile = regionsgdb + os.sep + fc
                        outfile = outGDB + os.sep + fc
                        #print outGDB

                        if arcpy.Exists(outfile):
                            #print "Already dissolved {0}".format(fc)
                            continue
                        else:

                            arcpy.Delete_management("temp_lyr")
                            arcpy.MakeFeatureLayer_management(infile, "temp_lyr")

                            arcpy.Dissolve_management("temp_lyr", outfile, dissolveFields, "", "MULTI_PART",
                                                      "DISSOLVE_LINES")
                            print "Dissolving {0} in {1}".format(fc, regionname)
                            print "completed {0} {1} remaining in {2}".format(fc, total, group)
                            total -= 1

                    arcpy.env.workspace = outGDB
                    fcList2 = arcpy.ListFeatureClasses()
                    if len(fcList) == len(fcList2):
                        print "\nAll {0} species files Dissolved in {1}".format(group, regionname)
                    else:
                        print "\nCheck for missing {0} dissolved files in {1}".format(group, regionname)
                        break
    inputFile2.close()

end = datetime.datetime.now()
print "Elapse time {0}".format(end - start_script)
