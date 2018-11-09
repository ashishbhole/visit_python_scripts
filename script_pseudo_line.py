#----------------------------------------------------------------------------
# To run this script, use following command
# 'visit -cli -nowin -s scriptname.py <database_filename_with_path> <variable_name_in_visit_file>'
# For example 'visit -cli -nowin -s scriptname.py ../omg.xdmf Vorticity > log.txt &'
#
# Description:
# This visit python script saves figures in png format for 2D time dependent
# solutions. First minimum and maximum of the variable is found using 'Query'
# operator of the visit. Then pseudocolor and contour plot is added. Finally
# a png file os stored for all time steps.
#---------------------------------------------------------------------------

from visit_utils import *
import sys

# functions
def find_min_max_over_time(database, variable):
   OpenDatabase(database, 0)
   AddPlot("Pseudocolor", variable)
   DrawPlots()
   var_min = 1.e20
   var_max = 1.e-20
   w = GetWindowInformation()
   for i in range(TimeSliderGetNStates()):
      print "query over time (MinMax) at ", i, " in ", TimeSliderGetNStates()  
      SetTimeSliderState(i)
      Query("MinMax")
      var_min = min(var_min, GetQueryOutputValue()[0])
      var_max = max(var_max, GetQueryOutputValue()[1])
   DeleteAllPlots()
   CloseDatabase(database)   
   return var_min, var_max

def add_pseudocolor_plot(variable, var_min, var_max):
   AddPlot("Pseudocolor", variable)
   DrawPlots()
   pseudo = PseudocolorAttributes()
   pseudo.min = var_min                      # set minimum value for variable
   pseudo.minFlag = 1
   pseudo.max = var_max                        # set maximum value of variable
   pseudo.maxFlag = 1
   pseudo.colorTableName = "hot_desaturated"  # set color table
   pseudo.invertColorTable = 0 # default 0
   SetPlotOptions(pseudo)

def add_contour_plot(variable, var_min, var_max):
   AddPlot("Contour", variable)
   DrawPlots()
   contour = ContourAttributes()
   contour.lineWidth = 1                    # Set line width of contours from here
   contour.colorType = 0                    # (0, 1): This selects color by (single, multiple) color/s: 
   contour.singleColor = (0, 0, 0, 255)     # This combination is for black color
   contour.contourNLevels = 15              # Set number of contour levels from here.
   contour.legendFlag = 0                   # (0, 1): Disable/enable display of legend for contours
   SetPlotOptions(contour)

def set_legend_attributes():
   #formatting legend object for contours
   plotName= "pl"
   legend = GetAnnotationObject(GetPlotList().GetPlots(0).plotName)
   legend.managePosition = 0
   legend.position = (0.15, 0.1)
   legend.fontFamily = 2  # Arial, Courier, Times
   legend.fontBold = 0
   legend.fontItalic = 1
   legend.drawBoundingBox = 0
   legend.numberFormat = "%# -9.2g"
   legend.drawLabels = 1 # None, Values, Labels, Both
   legend.fontHeight = 0.07
   legend.xScale = 3
   legend.yScale = 0.5
   legend.drawTitle = 0
   legend.drawMinMax = 0
   legend.orientation = 3  # VerticalRight, VerticalLeft, HorizontalTop, HorizontalBottom
   legend.controlTicks = 1
   legend.numTicks = 5          # set number of ticks
   legend.minMaxInclusive = 1

def set_annotation_attributes():
   a = AnnotationAttributes()
   a.axes2D.autoSetTicks = 1  # default 1
   a.axes2D.autoSetScaling = 1
   a.axes2D.lineWidth = 0
   a.axes2D.tickLocation = 0 # Inside, Outside, Both
   a.axes2D.tickAxes = 3 # Off, Bottom, Left, BottomLeft, All   
   a.axes2D.xAxis.title.visible=0             # disables default axis title
   a.axes2D.yAxis.title.visible=0
   a.axes2D.xAxis.label.font.font = 2         # set font size for axis label (0, 1, 2) Arial, Courier, Times
   a.axes2D.yAxis.label.font.font = 2
   a.axes2D.xAxis.label.font.scale = 1.5        # set font size for axis label
   a.axes2D.yAxis.label.font.scale = 1.5
   a.axes2D.xAxis.label.font.bold = 0 # defualt 1
   a.axes2D.xAxis.label.font.italic = 0 # defualt 1
   a.axes2D.yAxis.label.font.bold = 0 # defualt 1
   a.axes2D.yAxis.label.font.italic = 0 # defualt 1   
   a.userInfoFlag = 0                         # disable display of user info
   a.databaseInfoFlag = 0                     # disable display of database info
   SetAnnotationAttributes(a)

def format_axis_annotations():
   #x-axis title
   tx = CreateAnnotationObject("Text2D")       # add a text box
   tx.visible = 0  # 0, 1
   tx.active = 1
   tx.position = (0.5, 0.1)                    # set position of text box on screen
   tx.height = 0.025                            # set height of text
   tx.textColor = (0, 0, 0, 255)               # set color of text
   tx.useForegroundForTextColor = 1
   tx.text = "x"                               # set string for title
   tx.fontFamily = 2  # Arial, Courier, Times  # set font
   tx.fontBold = 0
   tx.fontItalic = 1
   # y-axis title
   ty = CreateAnnotationObject("Text2D")
   ty.visible = 0
   ty.active = 1
   ty.position = (0.1, 0.4)
   ty.height = 0.025
   ty.textColor = (0, 0, 0, 255)
   ty.useForegroundForTextColor = 1
   ty.text = "y"
   ty.fontFamily = 2  # Arial, Courier, Times
   ty.fontBold = 0
   ty.fontItalic = 1
   

def set_figure_title(t):
   #figure title
   title = CreateAnnotationObject("Text2D")
   title.visible = 1
   title.position = (0.48, 0.96)
   title.height = 0.03
   title.textColor = (0, 0, 0, 255)
   title.text = "t = $time"
   title.fontFamily = 2  # Arial, Courier, Times
   title.fontBold = 0
   title.fontItalic = 1

def set_view2d():
   view = GetView2D()
   view.windowCoords = (-1, 1, -1, 1)
   view.viewportCoords = (0.15, 0.95, 0.15, 0.95)
   view.fullFrameActivationMode = 2  # On, Off, Auto
   view.fullFrameAutoThreshold = 100
   view.xScale = 0  # LINEAR, LOG
   view.yScale = 0  # LINEAR, LOG
   view.windowValid = 1
   SetView2D(view)

def save_figures():
   # Save a files
   s = SaveWindowAttributes()
   s.format = s.PNG                  # set output image format
   s.fileName = variable            # set name of output files
   s.width, s.height = 1024,768      # set resolution of output files
   s.screenCapture = 1               # disable screen capture
   SetSaveWindowAttributes(s)
   # Save images of all timesteps and add each image filename to a list.
   names = []
   for state in range(TimeSliderGetNStates()):
      SetTimeSliderState(state)
      n = SaveWindow()

# Main progam
arguments = sys.argv[1:]
count = len(arguments)
if count != 2 :
    print "Please specify database filename and variable name"
    print "Usage: visit -cli -nowin -s scriptname.py <database_filename_with_path> <variable_name_in_visit_files> "
    sys.exit(1)

database = sys.argv[1]   #"../omg.xdmf"
variable = sys.argv[2]   #"Vorticity"
print "database is located at : ", database
print "variable chosen for plotting if : ", variable

var_min, var_max = find_min_max_over_time(database, variable)
OpenDatabase(database, 0)
add_pseudocolor_plot(variable, var_min, var_max)
add_contour_plot(variable, var_min, var_max)
set_legend_attributes()
set_annotation_attributes()
format_axis_annotations() # create new axes titles and figure titles
Query("Time")
t = GetQueryOutputValue()
set_figure_title(t)
set_view2d()
MoveAndResizeWindow(1,100,0,1000,1000) # id of window, new x & y position, new width & height
DrawPlots()
save_figures()

exit()      
