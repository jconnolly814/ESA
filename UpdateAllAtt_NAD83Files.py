import arcpy
import os
import datetime

masterlist = 'J:\Workspace\MasterLists\CSV\MasterListESA_April2015_20151015_20151124.csv'
infolder = 'J:\Workspace\ESA_Species\Range\NAD83'  # folder of GDB

# species groups to skip
skiplist = []

ColIndexDict = dict(comname=7, sciname=8, spcode=26, vipcode=27, entid=0, group=1)
final_fields = ['NAME', 'Name_sci', 'SPCode', 'VIPCode', 'FileName', 'EntityID']
final_fieldsindex = dict(NAME=0, Name_sci=3, SPCode=4, VIPCode=5, EntityID=1)

########Static variables
reqindex = {'entid': 'Q1', 'group': 'Q2'}
entid_indexfilenm = 1
inputlist = ['Yes', 'No']
speciestoQA = '1'
updatefiles = False
singleGDB = False
DissolveFiles = False
extention = infolder.split(".")
cnt = len(extention)
if cnt > 1:
    if extention[1] == 'gdb':
        singleGDB = True
    else:
        singleGDB = False
else:
    singleGDB = False

start_script = datetime.datetime.now()
print "Script started at {0}".format(start_script)


# Functions
def fcs_in_workspace(workspace):
    arcpy.env.workspace = workspace
    for fc in arcpy.ListFeatureClasses():
        yield (fc)
    for ws in arcpy.ListWorkspaces():
        for fc in fcs_in_workspace(ws):
            yield fc


def askuser(col, q, list):
    if q == 'Q1':
        user_input = raw_input('What is the column index for the EntityID (base 0): ')
        return user_input
    else:
        print list
        user_input = raw_input('What is the column index for the {0}(base 0): '.format(col))
        return user_input


def output_update(fc, value):
    print "     Updated {0} for files {1}".format(value, fc)


def CreateGDB(OutFolder, OutName, outpath):
    if not arcpy.Exists(outpath):
        arcpy.CreateFileGDB_management(OutFolder, OutName, "CURRENT")


## may be able to call dissolve field in update and so that is does  not need to re-load the fc list
def updateFilesloop(inGDB, final_fields, speinfodict, DissolveFiles):
    group_gdb = inGDB
    arcpy.env.workspace = group_gdb
    fclist = arcpy.ListFeatureClasses()
    entlist_fc = []
    for fc in fclist:
        print fc
        result = arcpy.GetCount_management(fc)
        count = int(result.getOutput(0))
        if count > 1:
            DissolveFiles = True
        entid = fc.split('_')
        entid = str(entid[entid_indexfilenm])
        fclist_field = [f.name for f in arcpy.ListFields(fc) if not f.required]
        for field in final_fields:
            if field not in fclist_field:
                arcpy.AddField_management(fc, field, "TEXT")
                print "added field {1} for {0}".format(fc, field)
                with arcpy.da.UpdateCursor(fc, field) as cursor:
                    if field == 'FileName':
                        for row in cursor:
                            fcname = fc.strip("_STD_NAD83")
                            # print fcname
                            value = str(fcname)
                            row[0] = value
                            cursor.updateRow(row)
                            output_update(fc, field)
                    if field == 'EntityID':
                        for row in cursor:
                            value = entid
                            row[0] = value
                            cursor.updateRow(row)
                            output_update(fc, field)
                    else:
                        for row in cursor:
                            indexfield = final_fieldsindex[field]
                            listspecies = speinfodict[entid]
                            value = listspecies[indexfield]
                            row[0] = value
                            cursor.updateRow(row)
                            output_update(fc, field)
            else:
                with arcpy.da.UpdateCursor(fc, field) as cursor:
                    if field == 'FileName':
                        for row in cursor:
                            current = row[0]
                            fcnamelist = fc.split("_")
                            try:
                                fcname = fcnamelist[0] +"_" +fcnamelist[1] +"_" +fcnamelist[2] +"_" +fcnamelist[3]
                            except:
                                fcname = fc
                            if current == fcname:
                                continue
                            else:
                                try:
                                    row[0] = fcname
                                    cursor.updateRow(row)
                                    output_update(fc, field)
                                except:
                                    continue
                    if field == 'EntityID':
                        value = entid
                        for row in cursor:
                            current = row[0]
                            if current == value:
                                continue
                            else:
                                row[0] = value
                                cursor.updateRow(row)
                                output_update(fc, field)
                    else:
                        for row in cursor:
                            current = row[0]
                            indexfield = final_fieldsindex[field]
                            listspecies = speinfodict[entid]
                            value = listspecies[indexfield]
                            if current == value:
                                continue
                            else:
                                row[0] = value
                                cursor.updateRow(row)
                                output_update(fc, field)
        for field in fclist_field:
            if field not in final_fields:
                arcpy.DeleteField_management(fc, field)
            else:
                continue
    return DissolveFiles


def dissolveLoop(inGDB, final_fields):
    group_gdb = inGDB
    arcpy.env.workspace = group_gdb
    fclist = arcpy.ListFeatureClasses()
    for fc in fclist:
        result = arcpy.GetCount_management(fc)
        count = int(result.getOutput(0))
        if count > 1:
            infc = inGDB + os.sep + fc
            path, tail = os.path.split(inGDB)
            outname = "Dissolve" + tail
            outGDB = path + os.sep + outname
            if not os.path.exists(outGDB):
                CreateGDB(path, outname, outGDB)
            outFC = outGDB + os.sep + str(fc)
            if not arcpy.Exists(outFC):
                arcpy.Dissolve_management(infc, outFC, final_fields)
                print "Dissolved {0}".format(fc)
            else:
                continue


def LoadSpeciesinfo_frommaster(ColIndexDict, reqindex, masterlist):
    grouplist = []
    speciesinfo_dict = {}
    listKeys = ColIndexDict.keys()
    listKeys.sort()
    reqlistkeys = sorted(reqindex.keys())
    Q1 = False
    Q2 = False
    for val in reqlistkeys:
        if val in listKeys:
            continue
        else:
            question = reqindex[val]
            vars()[question] = True
            vars()[val] = askuser(val, question, listKeys)
            if Q1:
                ColIndexDict['entid'] = vars()[val]
            if Q2:
                ColIndexDict['group'] = vars()[val]

    listKeys = ColIndexDict.keys()
    listKeys.sort()
    with open(masterlist, 'rU') as inputFile:
        header = next(inputFile)
        for line in inputFile:
            speciesinfo = []
            line = line.split(',')
            entid = line[int(ColIndexDict['entid'])]
            group = line[int(ColIndexDict['group'])]
            if group not in grouplist:
                grouplist.append(group)
            for v in listKeys:
                vars()[v] = line[int(ColIndexDict[v])]
                speciesinfo.append(vars()[v])
            speciesinfo_dict[entid] = speciesinfo
    inputFile.close()
    alpha_group = sorted(grouplist)
    # print alpha_group
    return listKeys, speciesinfo_dict, alpha_group


listKeys, speciesinfo_dict, alpha_group = LoadSpeciesinfo_frommaster(ColIndexDict, reqindex, masterlist)

print listKeys
print speciesinfo_dict[speciestoQA]

while updatefiles == False:
    user_inputupdated = raw_input('Please confirm that the species information is in the correct order: Yes or No: ')
    if user_inputupdated not in inputlist:
        print 'This is not a valid answer'
    elif user_inputupdated == 'Yes':
        updatefiles = True
        print 'Files will be updated now'
        if singleGDB:
            inGDB = infolder
            DissolveFiles = updateFilesloop(inGDB, final_fields, speciesinfo_dict, DissolveFiles)
            if DissolveFiles:
                dissolveLoop(inGDB, final_fields)
            DissolveFiles = False

        else:
            for group in alpha_group:
                start_loop = datetime.datetime.now()
                if group in skiplist:
                    continue
                print "\nWorking on {0}".format(group)
                inGDB = infolder + os.sep + str(group) + '.gdb'
                DissolveFiles = updateFilesloop(inGDB, final_fields, speciesinfo_dict, DissolveFiles)
                if DissolveFiles:
                    dissolveLoop(inGDB, final_fields)
                DissolveFiles = False

                endloop = datetime.datetime.now()
                print "Elapse time {0}".format(endloop - start_script)

    else:
        print 'Files will not be updated check the input indexes'
        updatefiles = True
        break

end = datetime.datetime.now()
print "Elapse time {0}".format(end - start_script)
