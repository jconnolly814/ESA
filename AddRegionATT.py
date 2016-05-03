import datetime

import arcpy

inlocation = 'J:\Workspace\ESA_Species\ForCoOccur\Composites\GDB\April_16Composites\L48_CH_SpGroup_Composite.gdb'
arcpy.env.workspace = inlocation
listfiles = arcpy.ListFeatureClasses()

start_script = datetime.datetime.now()
print listfiles
for v in listfiles:
    regions = v.split("_")
    regions = regions[0]
    print 'Adding {0} to file {1}'.format(regions, v)
    arcpy.AddField_management(v, "Region", "TEXT")
    with arcpy.da.UpdateCursor(v, "Region") as cursor:
        for row in cursor:
            row[0] = regions
            cursor.updateRow(row)

end = datetime.datetime.now()
print "Elapse time {0}".format(end - start_script)
