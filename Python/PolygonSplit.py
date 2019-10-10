__author__ = "John K. Tran, Tristan Forward"  
__contact__ = "jtran20@masonlive.gmu.edu, http://gis.stackexchange.com/users/6996/tristan-forward"  
__version__ = "2.0"  
__created__ = "7/3/15"  
__credits__ = "http://gis.stackexchange.com/questions/124198/optimizing-arcpy-code-to-cut-polygon"  
  
  
""" 
Cut polygons by polylines, splitting each polygon into slices. 
:param to_cut: The polygon to cut. 
:param cutter: The polylines that will each polygon. 
:param out_fc: The output with the split geometry added to it. 
"""  
  
  
import os  
import sys  
import arcpy  
  
  
arcpy.SetProgressor("default", "Firing up script...")  
  
  
to_cut = arcpy.GetParameterAsText(0)  
cutter = arcpy.GetParameterAsText(1)  
out_fc = arcpy.GetParameterAsText(2)  
  
  
spatialref = arcpy.Describe(to_cut).spatialReference  
polygons = []  
lines = []  
slices = []  
gcount = 0  
  
  
pcount = 0  
with arcpy.da.SearchCursor(to_cut, ["SHAPE@", "OID@"]) as pcursor:  
    for prow in pcursor:  
        arcpy.SetProgressorLabel("Generating slices: {0} rows complete".format(str(pcount)))  
        polygon = prow[0]  
        polyid = prow[1]  
        polygons.append((polygon, polyid))  
        pcount += 1  
del pcursor  
  
  
lcount= 0  
with arcpy.da.SearchCursor(cutter, ["SHAPE@", "OID@"]) as lcursor:  
    for lrow in lcursor:  
        line = lrow[0]  
        lineid = lrow[1]  
        lines.append((line, lineid))  
        lcount += 1  
del lcursor  
  
  
def cut_geometry():  
    global polygons  
    global lines  
    global slices  
    global gcount  
    for eachpoly, eachpolyid in polygons:  
        iscut = False  
        for eachline, eachlineid in lines:  
            if eachline.crosses(eachpoly):  
                try:  
                    slice1, slice2 = eachpoly.cut(eachline)  
                    polygons.insert(0, (slice1, eachpolyid))  
                    polygons.insert(0, (slice2, eachpolyid))  
                    iscut = True  
                except RuntimeError:  
                    continue  
        if iscut == False:  
            slices.append((eachpoly, eachpolyid))  
            gcount += 1  
            if gcount % 10 == 0:  
                arcpy.SetProgressorLabel("Cutting polygons: {0} rows complete".format(str(gcount)))  
        polygons.remove((eachpoly, eachpolyid))  
  
  
while polygons:  
    cut_geometry()  
  
  
arcpy.SetProgressorLabel("Creating output feature class")  
arcpy.CreateFeatureclass_management(os.path.dirname(out_fc), os.path.basename(out_fc), "POLYGON",  
                                    spatial_reference = spatialref)  
arcpy.AddField_management(out_fc, "SOURCE_OID", "LONG")  
scount = 0  
with arcpy.da.InsertCursor(out_fc, ["SHAPE@", "SOURCE_OID"]) as icursor:  
    for eachslice in slices:  
        if scount % 10 == 0:  
            arcpy.SetProgressorLabel("Inserting slices: {0} rows complete".format(str(scount)))  
        icursor.insertRow(eachslice)  
        scount += 1  
del icursor  
  
  
arcpy.ResetProgressor()  
