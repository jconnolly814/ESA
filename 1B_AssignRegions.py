import os
import datetime

import pandas as pd
import arcpy

IncludeAcres = False
masterlist = 'J:\Workspace\MasterLists\April2015Lists\CSV\MasterListESA_April2015_20151015_20151124.csv'
outfile = r'J:\Workspace\MasterOverlap\Panda\Insects_NAD83_Range_SpeciesRegions_all_20160421.csv'
regionsfc = 'J:\Workspace\ESA_Species\ForCoOccur\Composites\GDB\CompositesForClip\Boundaries.gdb\State_territories_NAD83'

# TODO split this so that it generates one file for the Range and one for the Critical habitat

compGDB = ['J:\Workspace\ESA_Species\Range\NAD83\Amphibians.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Arachnids.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Birds.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Clams.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Conifers and Cycads.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Corals.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Crustaceans.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Ferns and Allies.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Fishes.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Flowering Plants.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Insects.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Lichens.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Mammals.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Reptiles.gdb',
           'J:\Workspace\ESA_Species\Range\NAD83\Snails.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Amphibians.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Arachnids.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Birds.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Clams.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Corals.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Crustaceans.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Ferns and Allies.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Fishes.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Flowering Plants.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Insects.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Mammals.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Reptiles.gdb',
           'J:\Workspace\ESA_Species\CriticalHabitat\NAD_Final\Snails.gdb']



# dictionary, col name and index number- base 0
# Note entid if hard code for tracking!!!!
colincluded = {'EntityID': 0,
               'Group': 1,
               'ComName': 7,
               'SciName': 8,
               'Status_text': 11}

regions = ['AK', 'AS', 'CNMI', 'GU', 'HI', 'Howland Baker Jarvis', 'Johnston', 'L48', 'Palmyra Kingman', 'PR', 'VI',
           'Wake', 'Mona', 'Laysan', 'Nihoa', 'Necker', 'NorthwesternHI']

start_script = datetime.datetime.now()
print "Script started at: {0}".format(start_script)

listKeys = colincluded.keys()
regions.sort()
listKeys.sort()
regionsindex = {}
listheader = []

if colincluded['EntityID'] != 0:
    user_input = raw_input('What is the column index for the EntityID (base 0): ')
    user_input2 = raw_input('Is the Column Heading for the EntityID [EntityID] Yes or No:')
    if user_input2 == 'Yes':
        entheading = 'EntityID'
    else:
        entheading = user_input2
    regionsindex['EntityID'] = user_input
    index = 0
else:
    entheading = 'EntityID'
    regionsindex['EntityID'] = 0
    index = 1

listheader.append('EntityID')
for value in listKeys:
    if value == entheading:
        continue
    else:
        listheader.append(value)

for value in regions:
    listheader.append(value)

# print listheader
for value in listheader:
    try:
        indexvalue = regionsindex[value]
        index += 1
    except KeyError:
        regionsindex[value] = index
        index += 1

# print regionsindex
# print listheader
# print listKeys
# print regions
grouplist = []
allspecies = []
rowindex = 0
rowdict = {}
with open(masterlist, 'rU') as inputFile:
    speciesinfo = {}
    header = next(inputFile)
    for line in inputFile:
        currentline = []
        line = line.split(',')
        if colincluded['EntityID'] == 0:
            entid = str(line[0])
        else:
            entid = str(line[int(user_input)])
        rowdict[entid] = rowindex

        currentline.append(entid)
        for value in listheader:
            if value == 'EntityID':
                continue
            elif value in listKeys:
                vars()[value] = line[colincluded[value]]
                currentline.append(vars()[value])
            else:
                nan = 'nan'
                currentline.append(nan)
        speciesinfo[entid] = currentline
        allspecies.append(currentline)
        rowindex += 1
# print rowdict
inputFile.close()

outDF = pd.DataFrame(allspecies, columns=listheader)
arcpy.MakeFeatureLayer_management(regionsfc, "regions")
totalGDB = len(compGDB)
countGBD = 1
for ingdb in compGDB:
    print "\nWorking on GDB {0} of {1}...".format(countGBD, totalGDB)
    arcpy.env.workspace = ingdb
    fclist = arcpy.ListFeatureClasses()
    totalfc = len(fclist)
    countFC = 1
    for fc in fclist:
        infc = ingdb + os.sep + fc
        print "Working on fc {2}, {0} of {1}...and GDB {3} of {4} ".format(countFC, totalfc, fc, countGBD, totalGDB)
        with arcpy.da.SearchCursor(infc, ["EntityID"]) as cursor:
            for row in cursor:
                id = str(row[0])
                whereclause = "EntityID = '%s'" % id
                # print whereclause
                arcpy.Delete_management("lyr")
                arcpy.Delete_management("slt_lyr")
                arcpy.MakeFeatureLayer_management(fc, "lyr", whereclause)
                # print "Creating layer {0}".format(id)
                arcpy.SelectLayerByLocation_management("regions", "INTERSECT", "lyr")
                arcpy.MakeFeatureLayer_management("regions", "slt_lyr")
                result = arcpy.GetCount_management("slt_lyr")
                count = int(result.getOutput(0))
                if count == 0:
                    regions = []
                else:
                    with arcpy.da.SearchCursor("slt_lyr", ["Region"]) as regionscursor:
                        regions = []
                        for line in regionscursor:
                            inregion = line[0]
                            regions.append(inregion)
                setregions = set(regions)
                # print setregions
                regions = list(setregions)
                # print regions
                irow = rowdict[id]
                for s in regions:
                    # if 'Mona' in regions:
                    # print "updated species {0} to be included in regions {1} at row {3} comp file name {2}".format
                    col = regionsindex[s]
                    outDF.loc[irow, s] = 'Yes'
                    # print "updated species {0} to be included in regions {1} at row {3} comp file name {2}".format(id,setregions,fc, irow)
        countFC += 1
    countGBD += 1

print outDF
outDF.to_csv(outfile)
print "Script completed in: {0}".format(datetime.datetime.now() - start_script)
