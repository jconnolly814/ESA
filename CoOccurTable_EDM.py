import datetime

import pandas as pd

inlocation = r'C:\Users\JConno02\Desktop\active\AquSpecies\ExportTables\CSV\HUC12_10_Totals.csv'
masterlist = 'J:\Workspace\MasterLists\April2015Lists\CSV\MasterListESA_April2015_20151015_20151124.csv'
outcsv = r'C:\Users\JConno02\Desktop\active\AquSpecies\ExportTables\CSV\HUC12_10_outputIntervals2.csv'
colstart = 1
labelCol = 0
intveral = 30
maxdis = 1500

completedUses = ['10']
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
               'ComName': 7,
               'SciName': 8,
               'Status_text': 11}


def sum_by_interval(colstart, maxdis, intervalDict, indf, colcount, use):
    col = colstart
    rowcount = indf.count(axis=0, level=None, numeric_only=False)
    rowindex = rowcount.values[0]
    while col <= (colcount - 1):
        sum_pixel = 0
        intervals = []
        row = 0
        currentdis = 0
        entid = listheader[col]
        entid = entid.split('_')
        entid = str(entid[1])
        print entid
        currentinterval = 0
        while long(currentdis) < long(maxdis):
            while row <= (rowindex - 1):
                currentinterval += intveral
                if currentinterval > maxdis:
                    currentinterval = maxdis
                intervals.append(str(currentinterval) + '_' + str(use))
                # print "Working on species {0} at interval {1}".format(entid,currentinterval)
                sum_pixel = 0
                while long(currentdis) <= long(currentinterval):

                    if currentdis == currentinterval:
                        # print '{0},{1}'.format(row,col)
                        value = indf.iloc[row, col]
                        sum_pixel += value

                        sp_results = intervalDict.get(entid)

                        if sp_results is None:
                            intervalDict[entid] = [str(currentinterval) + "_" + str(sum_pixel)]

                        else:
                            sp_results.append(str(currentinterval) + "_" + str(sum_pixel))


                            # print value
                            # print "Total Pixels for species {0} at interval {1} was {2}".format(entid,currentinterval,sum_pixel)

                    else:
                        # print '{0},{1}'.format(row,col)
                        value = indf.iloc[row, col]
                        sum_pixel += value

                    row += 1
                    if row == rowindex:
                        break
                    else:

                        currentdis = indf.iloc[(row), labelCol]

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


start_script = datetime.datetime.now()
print "Script started at {0}".format(start_script)
outheader = []

speciesinfoDict, spheader = extract_speciesinfo(masterlist, colincluded)

intervalDict = {}


## add loop to loop through use tables
## loop start
usevalue = '10'  # extract from table name
use = useLookup[usevalue]
useResultdf = pd.read_csv(inlocation)
# print useResultdf
listheader = useResultdf.columns.values.tolist()
colcount = len(listheader)

intervalDict, intervals = sum_by_interval(colstart, maxdis, intervalDict, useResultdf, colcount, use)
print intervals
# print intervalDict
outheader.extend(spheader)
outheader.extend(intervals)
print outheader


##loop end
listentid = intervalDict.keys()
outlist = []
for value in listentid:
    currentspecies = []
    spinfo = speciesinfoDict[str(value)]
    for v in spinfo:
        currentspecies.append(str(v))
    spintervals = intervalDict[str(value)]
    for i in spintervals:
        print i
        breaklist = i.split('_')
        count = str(breaklist[1])
        interval = str(breaklist[0] + '_' + str(use))
        print interval
        if interval not in intervals:
            count = 0
        currentspecies.append(count)
    outlist.append(currentspecies)
    print currentspecies
print outlist

print intervals
outDF = pd.DataFrame(outlist, columns=outheader)
end = datetime.datetime.now()
print "Elapse time {0}".format(end - start_script)

# print outDF
outDF.to_csv(outcsv)
