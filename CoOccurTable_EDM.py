import datetime
import os
import arcpy

import pandas as pd

## TODO Make this specific ot step 3 and summing the prefered hab

# TODO When running for skipperling it extract Corn as the use when it was Pasture
# TODO for pref hab the column head of zonal table was cause it to not run
# TODO change intervals so that 0 is alone then it goes to 30 and up by 30
# TODO export table that is just 0 ground and aerial drift

infolder = 'C:\Workspace\ESA_Species\FinalBE_ForCoOccur\Results_Clipped\Range\PracticeCSV2'

unioned_gdb ='C:\WorkSpace\ESA_Species\FinalBE_ForCoOccur\Projected_UnionRange_20160705.gdb\Amphibians_Union_Final_20160705_AlbersEqualArea'
unioned_fields =['OBJECTID','ZoneSpecies']
# inlocation = r'J:\Workspace\ESA_Species\SpeciesWorkshop\ExportTableZoneHis\ZonalGAP_patch7Shrub.csv'
masterlist = 'C:\Users\JConno02\Documents\Projects\ESA\MasterLists\MasterListESA_June2016_20160628.csv'
outcsv = r'C:\\Workspace\\ESA_Species\\FinalBE_ForCoOccur\\Results_Clipped\\Range\\PracticeCSV2\\PracticeOverlap5.csv'
colstart = 1
labelCol = 0
intveral = 30
maxdis = 1500
useindex = 2  # place to extract use from tablename
groupindex =4
completedUses = []
useLookup = {'10': 'Corn',
             '20': 'Cotton',
             '30': 'Rice',
             '40': 'Soybean',
             '50': 'Wheat',
             '60': 'Veg Ground Fruit',
             '70': 'Other trees',
             '80': 'Other grains',
             '90': ' Other row crops',
             '100': 'Other Crops',
             '110': 'Pasture/Hay/Forage'
             }

colincluded = {'EntityID': 0,
               'Group': 1,
               'ComName': 2,
               'SciName': 3,
               'Status_text': 4}


def sum_by_interval(colstart, maxdis, intervalDict, indf, colcount, use):
    col = colstart
    rowcount = indf.count(axis=0, level=None, numeric_only=False)
    rowindex = rowcount.values[0]
    while col <= (colcount - 1):
        intervals = []
        row = 0
        currentdis = 0
        entid = listheader[col]
        ent_listID = entid.split('_')
        lislen = len(entid)
        ent_listID = str(entid[lislen - 1])
        currentinterval = 0
        while long(currentdis) < long(maxdis):
            while row <= (rowindex - 1):

                if currentinterval > maxdis:
                    currentinterval = maxdis
                intervals.append(str(currentinterval) + '_' + str(use))
                print currentinterval
                # print "Working on species {0} at interval {1}".format(entid,currentinterval)
                sum_pixel = 0
                while long(currentdis) <= long(currentinterval):
                    if currentdis == currentinterval:
                        # print '{0},{1}'.format(row,col)
                        value = indf.iloc[row, col].astype(float)

                        sum_pixel += value

                        sp_results = intervalDict.get(ent_listID)

                        if sp_results is None:
                            intervalDict[ent_listID] = [str(currentinterval) + "_" + str(sum_pixel)]

                        else:
                            sp_results.append(str(currentinterval) + "_" + str(sum_pixel))
                            # print value
                            #print "Total Pixels for species {0} at interval {1} was {2}".format(entid,currentinterval,sum_pixel)

                    else:
                        # print '{0},{1}'.format(row,col)
                        value = int(indf.iloc[row, col])

                        sum_pixel += value

                    row += 1
                    if row == rowindex:
                        break
                    else:

                        currentdis = indf.iloc[(row), labelCol]
                currentinterval += intveral

        col += 1
    return intervalDict, intervals


def ask_user_entityid(colincluded):
    listKeys = colincluded.keys()
    listKeys.sort()

    if colincluded['EntityID'] != 0:
        user_input = raw_input('What is the column index for the EntityID (base 0): ')
        user_input2 = raw_input('Is the Column Heading for the EntityID [EntityID] Yes or No:')
        if user_input2 == 'Yes':
            colincluded['EntityID'] = user_input

        else:
            entheading = str(user_input2)
            colincluded[entheading] = user_input
            if 'EntityID' in colincluded: del colincluded['EntityID']
    return colincluded, user_input

def extract_speciesinfo(masterlist, colincluded):
    speciesinfo = {}
    if colincluded['EntityID'] == 0:
        entindex = 0
    else:
        colincluded, entindex = ask_user_entityid(colincluded)
    listKeys = colincluded.keys()
    with open(masterlist, 'rU') as inputFile:
        speciesinfo = {}
        header = next(inputFile)
        for line in inputFile:
            currentline = []
            line = line.split(',')
            entid = str(line[int(entindex)])
            currentline.append(entid)
            for value in listKeys:
                if value == 'EntityID':
                    continue
                elif value in listKeys:
                    vars()[value] = line[colincluded[value]]
                    currentline.append(vars()[value])
                else:
                    nan = 'nan'
                    currentline.append(nan)
            speciesinfo[entid] = currentline
    inputFile.close()
    return speciesinfo, listKeys

def loop_outtables(infolder,intervalDict,current_group):
    listfolder = os.listdir(infolder)
    for folder in listfolder:
        try:
            listtable = os.listdir(infolder + os.sep + folder)
            for table in listtable:
                parse_fc = table.split("_")
                group =parse_fc [groupindex]
                if group == current_group:
                    use = parse_fc [useindex]
                    # usevalue =use[:-2]
                    usevalue = use.replace('x2', '')
                    use_group = useLookup[usevalue]
                    print use_group
                    useResultdf = pd.read_csv(infolder + os.sep + folder + os.sep + table)
                    useResultdf['LABEL'] = useResultdf['LABEL'].map(lambda x: x.replace(',', '')).astype(long)
                    listheader = useResultdf.columns.values.tolist()
                    colcount = len(listheader)
                    intervalDict, intervals = sum_by_interval(colstart, maxdis, intervalDict, useResultdf, colcount, use_group)
                    outheader.extend(spheader)
                    outheader.extend(intervals)
                    print outheader
                else:
                    continue
        except WindowsError:
            continue
    del listfolder
    print intervals
    return intervalDict, intervals, outheader

def add_species_info_overlap(id_dict,speciesinfoDict,intervalDict, outlist):
    id_keys =id_dict.keys()
    for t in id_keys:
        listentid = id_dict[t]
        for value in listentid:
            currentspecies = []
            try:
                spinfo = speciesinfoDict[str(value)]
            except KeyError:
                print value
                continue
            for v in spinfo:
                try:
                    currentspecies.append(str(v))
                except KeyError:
                    print v
                    continue
            spintervals = intervalDict[str(value)]
            print spintervals
            for i in spintervals:
                breaklist = i.split('_')
                count = str(breaklist[1])
                interval = str(breaklist[0] + '_' + str(use_group))
                #print interval
                if interval not in intervals:
                    count = 0
                currentspecies.append(count)
            #print currentspecies
            outlist.append(currentspecies)
            print currentspecies
    return outlist

def extract_unionIDfromshapes(unioned_gdb,fc,unioned_fields):
        unioned_entlist={}
        infc = unioned_gdb+os.sep+fc
        with arcpy.da.SearchCursor(infc, unioned_fields) as cursor:
            for row in cursor:
                row_id = row[0]
                entlist = row[1]
                unioned_entlist[row_id] = entlist
            del row, cursor
        return unioned_entlist


start_script = datetime.datetime.now()
print "Script started at {0}".format(start_script)
outheader = []

speciesinfoDict, spheader = extract_speciesinfo(masterlist, colincluded)

intervalDict = {}
outlist = []

arcpy.env.workspace = unioned_gdb
fclist = arcpy.ListFeatureClasses()
for fc in fclist:
    print fc
    sp_group = fc.split('_')
    sp_group=str(sp_group[0])
    print sp_group
    intervalDict, intervals =loop_outtables(infolder,intervalDict,sp_group)
    union_id_dict = extract_unionIDfromshapes(unioned_gdb,fc,unioned_fields)
    outlist= add_species_info_overlap(union_id_dict,speciesinfoDict,intervalDict, outlist)
del fclist

print outlist

# outDF = pd.DataFrame(outlist, columns= outheader )
outDF = pd.DataFrame(outlist)
end = datetime.datetime.now()
print "Elapse time {0}".format(end - start_script)

# print outDF
outDF.to_csv(outcsv)
