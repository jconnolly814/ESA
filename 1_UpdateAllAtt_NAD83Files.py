import os
import datetime

import arcpy
import pandas as pd

masterlist = 'J:\Workspace\MasterLists\April2015Lists\CSV\MasterListESA_April2015_20151015_20151124.csv'
infolder = 'J:\Workspace\ESA_Species\Range\NAD83\RawAquatics\Catch_notdissolved\Crustaceans_catchment.gdb'  # folder of GDB

# species groups to skip
skiplist = []

final_fields = ['FileName', 'EntityID', 'NAME', 'Name_sci', 'SPCode', 'VIPCode', 'Status']  # in order to be added
colorderDict = dict(EntityID='entityid', NAME='comname', Name_sci='sciname', SPCode='spcode', VIPCode='vipcode',
                    Status='status')  # link the var used to store species info from table to a col in fc
final_fieldsindex = dict(NAME=2, Name_sci=3, SPCode=4, VIPCode=5, EntityID=1, Status=6,
                         FileName=0)  # used to check if FC has field in the correct order

CheckForChanges_col = ['entityid', 'spcode', 'vipcode', 'sciname', 'comname', 'group',
                       'status']  # col that will be looked up in master

oldColindex = {'entityid': 0,
               'spcode': 26,
               'vipcode': 27,
               'sciname': 8,
               'comname': 7,
               'group': 1,
               'status': 11}
########Static variables

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
def CreatDicts(list_vars):
    for v in list_vars:
        dictname = "{0}".format(v)
        globals()[dictname] = {}


def list_dicts():
    # global spcode, vipcode, sciname, comname, invname, pop_abbrev, pop_desc, family, status, status_text, lead_agency, lead_region, country, listing_date, dps, refuge_occurrence
    listitems = []
    listdicts = []
    for name in globals():
        if not name.startswith('__'):
            listitems.append(name)
    for value in listitems:
        if type((globals()[value])) is dict:
            listdicts.append(value)
    return listdicts


def LoadDatainDicts(incsv, colIndex, dict_list):
    df = pd.read_csv(incsv)
    group_df = df['Group']
    unq_groups = group_df.drop_duplicates()

    header = list(df.columns.values)

    entidindex = colIndex["entityid"]

    rowcount = df.count(axis=0, level=None, numeric_only=False)
    rowindex = rowcount.values[0]
    colindex = len(header) - 1  # to make base 0

    row = 0
    while row < (rowindex):
        entid = str(df.iloc[row, entidindex])
        # print "Working on species {0}, row {1}".format(entid, row)
        for dictionary in dict_list:
            col = colIndex[str(dictionary)]  ## assuming an index row from pandas export
            value = df.iloc[row, col]
            ((globals()[dictionary][entid])) = str(value)

        row += 1
    return group_df


def fcs_in_workspace(workspace):
    arcpy.env.workspace = workspace
    for fc in arcpy.ListFeatureClasses():
        yield (fc)
    for ws in arcpy.ListWorkspaces():
        for fc in fcs_in_workspace(ws):
            yield fc


def output_update(fc, value):
    print "     Updated {0} for files {1}".format(value, fc)


def CreateGDB(OutFolder, OutName, outpath):
    if not arcpy.Exists(outpath):
        arcpy.CreateFileGDB_management(OutFolder, OutName, "CURRENT")


def CheckFieldOrder(inGDB, final_fieldsindex, DissolveField):
    group_gdb = inGDB
    arcpy.env.workspace = group_gdb
    fclist = arcpy.ListFeatureClasses()
    checkorder = {}
    for fc in fclist:
        print fc
        result = arcpy.GetCount_management(fc)
        count = int(result.getOutput(0))
        if count > 1:
            DissolveFiles = True
        entid = fc.split('_')
        entid = str(entid[entid_indexfilenm])
        order_correct = True
        fclist_field = [f.name for f in arcpy.ListFields(fc) if not f.required]
        for field in fclist_field:
            i = fclist_field.index(field)
            checkorder[field] = i
            j = final_fieldsindex[field]
            if i != j:
                order_correct = False
            else:
                continue
        if not order_correct:
            for field in fclist_field:
                arcpy.DeleteField_management(fc, field)
            for field in final_fields:
                arcpy.AddField_management(fc, field, "TEXT")
                print "added field {1} for {0}".format(fc, field)

        fclist_field = [f.name for f in arcpy.ListFields(fc) if not f.required]

        for field in fclist_field:
            print field
            with arcpy.da.UpdateCursor(fc, field) as cursor:
                if field == 'FileName':
                    for row in cursor:
                        current = row[0]
                        if current is None:
                            value = str(fc)
                            row[0] = value
                            cursor.updateRow(row)
                            output_update(fc, field)
                        else:
                            continue
                    continue
                if field == 'EntityID':
                    for row in cursor:
                        current = row[0]
                        if current != entid:
                            value = entid
                            row[0] = value
                            cursor.updateRow(row)
                            output_update(fc, field)
                        else:
                            continue
                else:
                    val_dict = colorderDict[field]
                    value = ((globals()[val_dict][entid]))
                    for row in cursor:
                        current = row[0]
                        if current != value:
                            row[0] = value
                            cursor.updateRow(row)
                            output_update(fc, field)
                        else:
                            continue

        for field in fclist_field:
            if field not in final_fields:
                arcpy.DeleteField_management(fc, field)
            else:
                continue
    return DissolveFiles


## may be able to call dissolve field in update and so that is does  not need to re-load the fc list
# TODO update files so that character limits in the attribute table doesn't block data update


def dissolveloop(inGDB, final_fields):
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


CreatDicts(CheckForChanges_col)
allDicts = list_dicts()
group_df = LoadDatainDicts(masterlist, oldColindex, CheckForChanges_col)

if singleGDB:
    inGDB = infolder
    DissolveFiles = CheckFieldOrder(inGDB, final_fieldsindex, DissolveFiles)
    if DissolveFiles:
        dissolveloop(inGDB, final_fields)
    DissolveFiles = False
else:
    alpha_group = group_df['Group'].values.tolist
    for group in alpha_group:
        start_loop = datetime.datetime.now()
        if group in skiplist:
            continue
        print "\nWorking on {0}".format(group)
        inGDB = infolder + os.sep + str(group) + '.gdb'
        DissolveFiles = CheckFieldOrder(inGDB, final_fieldsindex, DissolveFiles)
        if DissolveFiles:
            dissolveloop(inGDB, final_fields)
        DissolveFiles = False

        endloop = datetime.datetime.now()
        print "Elapse time {0}".format(endloop - start_script)

end = datetime.datetime.now()
print "Elapse time {0}".format(end - start_script)
