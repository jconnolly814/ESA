import os
import datetime

import arcpy





# TODO make updated for append so that the len list is equal to the len count of rows of comp

refFC = 'J:\Workspace\ESA_Species\ForCoOccur\Composites\GDB\April_16Composites\WebApp\Composites\L48_CH_SpGroup_Composite_Web.gdb\Lower48_CH_Amphibians_L48_AlbersEqualArea_20160503_NAD83_WGS84_WebMercator'

outFolderCompGDB = r'J:\Workspace\ESA_Species\ForCoOccur\Composites\CurrentComps\WebApp'
skipgroup = []

while True:
    user_input = raw_input('Are you running range files Yes or No? ')
    if user_input not in ['Yes', 'No']:
        print 'This is not a valid answer'
    else:
        if user_input == 'Yes':
            FilesGDB = [
                'J:\Workspace\ESA_Species\ForCoOccur\Composites\CurrentComps\NL48_R_SpGroup_Composite.gdb',
                'J:\Workspace\ESA_Species\ForCoOccur\Composites\CurrentComps\L48_R_SpGroup_Composite.gdb',
                'J:\Workspace\ESA_Species\ForCoOccur\Composites\CurrentComps\MinorIsland_R_SpGroup_Composite.gdb']
            RangeFile = True
            FileType = "R_"
            outGDB = outFolderCompGDB + os.sep + 'R_WebApp_Composite.gdb'
            break
        else:

            FilesGDB = [
                'J:\Workspace\ESA_Species\ForCoOccur\Composites\CurrentComps\L48_CH_SpGroup_Composite.gdb',
                'J:\Workspace\ESA_Species\ForCoOccur\Composites\CurrentComps\MinorIsland_CH_SpGroup_Composite.gdb',
                'J:\Workspace\ESA_Species\ForCoOccur\Composites\CurrentComps\NL48_CH_SpGroup_Composite.gdb']
            RangeFile = False
            FileType = "CH_"
            outGDB = outFolderCompGDB + os.sep + 'CH_WebApp_Composite.gdb'
            break

arcpy.env.overwriteOutput = True  # ## Change this to False if you don't want GDB to be overwritten
arcpy.env.scratchWorkspace = ""
boolbreak = False


def creategdb(outfolder, outname, outpath):
    if not arcpy.Exists(outpath):
        arcpy.CreateFileGDB_management(outfolder, outname, "CURRENT")


def createdirectory(path_dir, outfoldergdb):
    if not os.path.exists(path_dir):
        os.mkdir(path_dir)
        print "created directory {0}".format(path_dir)
    if not os.path.exists(outfoldergdb):
        os.mkdir(outfoldergdb)
        print "created directory {0}".format(outfoldergdb)


def createcomp(filetype, spgroup, infiles, outlocation, reffc, datedict):
    indate = datedict[spgroup]
    comp_filename = filetype + spgroup + "_" + "WebApp_" + str(indate)
    filepath = outlocation + os.sep + comp_filename
    if arcpy.Exists(filepath):
        count = int(arcpy.GetCount_management(filepath).getOutput(0))
    else:
        count = 0
    allfc = []
    totalcount = 0
    for v in infiles:
        countfc = int(arcpy.GetCount_management(v).getOutput(0))
        totalcount += countfc
        allfc.append(v)
    if len(allfc) == 0:
        pass
    elif count == totalcount:
        print "  \n  Working on group {0}...".format(spgroup)
        print "    Already completed {0}".format(comp_filename)
    else:
        print "  \n  Working on group {0}...".format(spgroup)
        print "  \n  Updated on {0}...".format(indate)
        print '    Total files are {0}, total rows {1}'.format(len(allfc), totalcount)
        arcpy.env.workspace = outlocation
        arcpy.env.overwriteOutput = True

        orgdsc = arcpy.Describe(reffc)
        orgsr = orgdsc.spatialReference
        print '    Spatial projections is: {0}'.format(orgsr.name)
        arcpy.CreateFeatureclass_management(outlocation, comp_filename, "POLYGON", refFC, 'DISABLED', 'DISABLED', orgsr)
        count = int(arcpy.GetCount_management(filepath).getOutput(0))
        print '    Created blank fc {0} with row count {1}'.format(comp_filename, count)
        print '    Appending files for {0} ....'.format(spgroup)
        arcpy.Append_management(allfc, filepath)
        count = int(arcpy.GetCount_management(filepath).getOutput(0))
        if count != totalcount:
            print "    Check {0} for missing files {1}, projection , {2}".format(spgroup, orgsr, count)

        loop = datetime.datetime.now()
        print "Elapse time for loop {0}".format(loop - start_script)


start_script = datetime.datetime.now()
print "Script started at {0}".format(start_script)

if not os.path.exists(outGDB):
    path, gdb = os.path.split(outGDB)
    creategdb(outFolderCompGDB, gdb, outGDB)

grouplist = []
fulllist = []
regionlist = []

for v in FilesGDB:
    print v
    arcpy.env.workspace = v
    singlelist = arcpy.ListFeatureClasses()
    for fc in singlelist:
        group = fc.split("_")
        region = group[0]
        group = str(group[2])
        regiongroup = region + "_" + group

        if group not in grouplist:
            grouplist.append(group)
        if regiongroup not in regionlist:
            path = v + os.sep + fc

            fulllist.append(path)
            regionlist.append(regiongroup)

print grouplist

datedict = {}
for value in grouplist:
    currentgroup = []
    date = 0
    for v in fulllist:
        path, fc = os.path.split(v)
        fcparse = fc.split("_")
        group = str(fcparse[2])

        if group == value:
            if date != int(fcparse[5]):
                if date > int(fcparse[5]):
                    pass
                else:
                    date = int(fcparse[5])
            path = v
            datedict[value] = date
            currentgroup.append(path)
    ingdbs = currentgroup
    print datedict
    print ingdbs

    createcomp(FileType, value, ingdbs, outGDB, refFC, datedict)

end = datetime.datetime.now()
print "Elapse time {0}".format(end - start_script)
