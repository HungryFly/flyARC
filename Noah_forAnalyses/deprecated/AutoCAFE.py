#   autocafe.py - A script to maintain Image J Tracker and JA lab plugin
#                 Data files for Drosophila AutoCafe feeding bout prediction
#                 ,revision, and analysis
#   Copyright (C) 2013 Keith Murphy, James Quinn
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import copy
                            # --------------
                            # Script Outline
                            # --------------
# The 'AUTOCAFE' script is used to interpret Image J or Tracker files. The
# contents are interpreted to automate the process of finding 'meals', rather
# than performing this task by hand. The output of the script is two files,
# which display the time/frame a meal occurred, as well as the meal size in
# microliters.
#
# The 'Collated' file, puts the time/frame and meal size side by side,
# 'collating' the data. The second file 'Stacks' the information with
# time/frames on the top of the file and the meal size on the bottom.
#
# Both files are comma delimited '.csv' files that can be opened in excel or
# google spreadsheets.
#
                            # -------------
                            # User Workflow
                            # -------------

# The user is required to provide a tab delimitted file generated Image J's
# Tracker or JaLab Plugins. Proper knowledge of Image J's Tracker or Ja Lab Plugin
# is required.
#
# The user must have a metric ruler on screen to provide the number of pixels
# per centimeter. Three values are provided and averaged to calculate the
# microliters per meal.
#
# Once these are provided, the script chooses meals based on simple statistical
# algorithms. The list of the meals can be editted manually prior to the excel
# output files being written.
#
# Optionally, users may choose to convert frame numbers into Zeitgeiber times.
# Once the data has been reviewed/editted and the optionaly settings have been
# provided, the files are named and output. This can be validated, tweaked, and
# redone any number of times in a single session.

                            # --------------------
                            # Implementation Notes
                            # --------------------

# The core components of the script are broken up into individual functions
# rather than the original scripts fairly linear style. Each function describes
# itself inline immediately following the function definition.
#
# The script's entry point is located on the last line of the script with a
# call to the 'runAutoCafe' funciton. This will kick off the script, read in
# the user specified input file, and begin processing. 


                            # ---------
                            # Constants
                            # ---------
                            
SIMPLE_DEVIATION = 2.0   # The naive standard deviation meal model
FRAME            = 1     # The column index for 'Frame Number' in a JA File
PIXEL_DISTANCE   = 7     # The column index for 'Pixel Distance' in a JA File
CM_PER_UL        = 1.145 # Calculated value for cm/uL
HOURS_PER_DAY    = 24    # Number of hours in a day
MINUTES_PER_HOUR = 60    # Number of minutes per hour
DEFAULT_FRAME    = 0     # A default frame offset for Zeitgeiber times
DEFAULT_INTERVAL = 1     # A default frame interval for Zeitgeiber times
MEALPULL_SD      = 4.0   # The meal pull sd for recalculating noise sd's
FINAL_SD         = 3.5   # Final SD threshold for pulling meals
ORIGINAL_VOL     = 4.0   # Original Volume of liquid food in capillary 

def printBanner():
    # This function is used to print the name and description
    # of this script. Returns the name of the input file to
    # be processed.
    print("   AutoCafe.py - A script to maintain Image J Tracker and JA lab plugin\n"
          "                 Data files for Drosophila AutoCafe feeding bout prediction\n"
          "                 ,revision, and analysis\n"
          "   Copyright (C) 2013 Keith Murphy, James Quinn\n"
          "\n"
          "   This program is free software: you can redistribute it and/or modify\n"
          "   it under the terms of the GNU General Public License as published by\n"
          "   the Free Software Foundation, either version 3 of the License, or\n"
          "   any later version.\n"
          "\n"
          "   This program is distributed in the hope that it will be useful,\n"
          "   but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
          "   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
          "   GNU General Public License for more details.\n"
          "\n"
          "   You should have received a copy of the GNU General Public License\n"
          "   along with this program.  If not, see <http://www.gnu.org/licenses/>.\n"
          "\n"
          "\n"
          "                 --------\n"
          "                  AUTOCAFE\n"
          "                  --------\n"
          "\n"
          "Input file should be standard .txt notepad file\n"
          "and should be copied from an Image J Tracker\n"
          "Plugin output file.\n\n"
          "\n"
          "This should have eight columns with the first\n"
          "being capillary text and the last being the pixel\n"
          "distal values.\n\n"
          "\n"
          "Note: This program treats dropouts or 0 distal reads \n"
          "as linear continuations to the next valid value. \n"
          "Accuracy of AutoCAFE's MEal prediction can be \n"
          "improved by increasing frame capture rate, camera \n"
          "resolution and proximity, and by careful thresholding \n"
          "of images. Max frame rate should be 1 per minute. \n"
          "Standard deviations for meal selection should be \n"
          "calibrated to your system and can be edited in \n"
          "the constant's section.\n")

def isTrackerFile(file):
    # Return true if the file is a Tracker file, and false otherwise.
    # If the string contains a 'c' as from the word 'Capillary'
    # we return true. If not, its a tracker file so we return false
    file.seek(0)
    line = file.readline()

    isTracker = True

    try:
        line.lower().index('c')
        isTracker = False
    except:
        isTracker = True

    return isTracker
 
def fileDetails(file, frameIndex):
    # For a given file, return the max frame number and the number of lines in
    # the file. Use the supplied 'frameNumber' index to determine
    # maxFrameNumber.

    print("Analyzing file format...")
    file.seek(0)

    maxFrame  = 0
    lineCount = 0
      
    for line in file:
        lineCount  = lineCount + 1
        lineValues = line.split('\t')

        # Skip extra empty lines
        if 0 == len(lineValues):
            continue

        frame = int(lineValues[frameIndex])

        if frame > maxFrame:
            maxFrame = frame

    print("Done analyzing file.")
      
    return maxFrame, lineCount, int(lineCount/maxFrame)
             
def parseData(file):
    # For a given Image J file, parse the contents into a
    # two dimensional matrix. The data will be broken down
    # into an array of the form data[capillary][frame] = pixel
    print("Parsing file contents...")
    
    isTracker  = isTrackerFile(file)
    frameIndex = FRAME
    pixelIndex = PIXEL_DISTANCE

    if True == isTracker:
        frameIndex = frameIndex - 1
        pixelIndex = pixelIndex - 1

    maxFrame, lineCount, numCapillaries = fileDetails(file, frameIndex)
    file.seek(0)

    dataSet = []
    
    for i in range(0, int(numCapillaries)):
        dataSet.append([])

    capillary = 0
            
    for line in file:
        lineValues = line.split('\t')

        try:
            frame      = int(lineValues[frameIndex])
            pixelValue = float(lineValues[pixelIndex])

            dataSet[capillary].append(pixelValue)
            
            if frame == maxFrame:
                capillary = capillary + 1
           
        except Exception as e:
            errorMsg = "Invalid Input File"
            raise Exception(errorMsg)

    print("Done parsing file.")

    return dataSet
   
def getDeltas(inputData):
    # This function takes a list of lists and returns a new matrix
    # made up of all the delta values for each capillary. These are
    # absolute values between each frame.

    allDeltas = []
    for capillary in inputData:

        deltas = []

        for x in range(1, len(capillary)):

            if capillary[x] == 0:
                y = 1
                try:
                    while capillary[x] + capillary[x + y] == 0:
                        y = y + 1
                    shift =  ((capillary[x+y]-capillary[x-1])/ (y + 1)) 
                    capillary[x] = capillary[x-1] + shift
                except: capillary[x] = capillary[x-1]
            
            deltas.append(capillary[x] - capillary[x - 1])
        allDeltas.append(deltas)

    ulConversion       = getUnitConversion()
    return allDeltas, ulConversion

def noiseStats(capillaryDeltas):
    # This function begins by finding the standard deviation for capillary
    # delta values.
    #
    # It then proceeeds to pull standard deviations above 'MEALPULL_SD',
    # and recalculates the standard deviation. This process is repeated
    # until no meals are found.
    # 
    # This is done to remove the affects that a single outlier may have on the
    # data. If we have 'small', 'medium', and a single 'large' meal, it is
    # possible that the standard deviation is affected enough by the 'large'
    # meal, that smaller meals would be considered noise using a more naive
    # approach.
    #
    # Once it completes, it returns the mean and standard deviation of the
    # remaining noise.
    
    noiseData = copy.deepcopy(capillaryDeltas)

    oldSize  = -1 
    currSize = len(noiseData)
    while oldSize != currSize:
        oldSize = currSize

        mean, deviation = meanAndDeviation(noiseData)

        newNoiseData = []
        
        for i in range(0, len(noiseData)):
            if deviation * MEALPULL_SD > noiseData[i]:
                newNoiseData.append(noiseData[i])

        currSize  = len(newNoiseData)
        noiseData = newNoiseData       

    return meanAndDeviation(noiseData)
    
def getMealData(deltaMatrix,ulConversion,ORIGINAL_VOL):
    # Given the delta matrix, return a dictionary containing capillary
    # meals. This will be manipulated by users to determine the final
    # meal matrix.
    
    print("Calculating frames deltas ...")
   
    mealData  = {}
    volData   = {}
    
    ORIGINAL_VOL = ORIGINAL_VOL * ulConversion
        
    for i in range(0, len(deltaMatrix)):
        capillary   = deltaMatrix[i]
        noiseMean, noiseDeviation = noiseStats(capillary)

        meals   = dict()
        volumes = dict()
        
        # Remove average evaporation/noise from each delta.
        for j in range(0, len(capillary)):
            capillary[j] = (capillary[j] - noiseMean)

        # adjust volume to compensate for nutrient concentration shift from evaporation

        priorMeals = []     
        for j in range(0, len(capillary)):
            if capillary[j]  > (noiseDeviation * FINAL_SD):
                volumes[j + 1] = capillary[j]
                adjustmentFactor = ( (ORIGINAL_VOL - sum(priorMeals))  / ((ORIGINAL_VOL - sum(priorMeals)) - ((j-1)*noiseMean)))
                meals[j + 1] = capillary[j] * adjustmentFactor
                priorMeals.append(capillary[j])

        volData[i] = volumes
        mealData[i] = meals

 
    return mealData, volData
   
def meanAndDeviation(data):
    # Python algorithm to compute mean and standard deviation for a given list.
    # A faster algorithm exists in Knuth's "The Art of Programming", but this
    # will do.
    # Adapted from:
    # http://www.physics.rutgers.edu/~masud/computing/WPark_recipes_in_python.html
    from math import sqrt

    length = len(data)
    mean   = 0
    std    = 0
       
    for number in data:
        mean = mean + number
	
    mean = mean / float(length)
    
    for number in data:
        std = std + (number - mean)**2
	
    std = sqrt(std / float(length-1))
    
    return mean, std
          
def getInput():
    # This function asks the user for an input file. Once it's
    # opened, the data is parsed into a two-dimensional matrix.
    # Data is returned from the function once parsed succesfully.

    inputFile = input("Type input file path to continue: ")

    try:
        file = open(inputFile)
    except:
        errorMsg = "Error: Unable to open file: '" + inputFile + "'"
        raise Exception(errorMsg)
        
    return parseData(file)

def printData(data):
    # Simple pretty printing of the data. This serves as more of a
    # debugging functionality than anything else. Will be removed
    # in the final version.
    pp = pprint.PrettyPrinter()
    pp.pprint(data)

                            # --------------------
                            # User Input Functions
                            # --------------------

def manipulateData(inputData, deltaMatrix, mealData, volData, ulConversion):
    # This is the entry point for user interaction. It is a recursive, menu
    # driven interface which allows users to set up Zeitberger time, add data
    # points, or remove data points from the mealData matrix.

    frameOffset        = DEFAULT_FRAME
    intervalConversion = DEFAULT_INTERVAL
    
    while True:
        print()
        print("-------------- Main Menu --------------");
        print()
        print("\t 1. View/Edit Capillary")
        print("\t 2. Output Excel file")
        print("\t 3. Reset Microliter Units")
        print("\t 4. Set Frames/Zeitgeiber Times")
        print("\t 0. Exit")
        try:
            option = int(input("\nPlease enter command number: "))

            if option == 0:
                quit = input("Are You Sure You Want To Quit? (yes or no): ")
                if quit=="yes":
                    return       
            elif option == 1:
                chooseCapillaryMenu(inputData,
                                    deltaMatrix,
                                    mealData,
                                    volData,
                                    ulConversion)
            elif option == 2:
                outputToExcel(mealData,
                              volData,
                              ulConversion,
                              frameOffset,
                              intervalConversion)
            elif option == 3:
                ulConversion = getUnitConversion()
            elif option == 4:
                frameOffset, intervalConversion = getZeitgeiberTime()
            else:
                raise Exception("Invalid Command Provided")
            
        except Exception as e:
            print(e)

def chooseCapillaryMenu(inputData, deltaMatrix, mealData, volData, ulConversion):
    # This function allows users to select any individual capillary, and drill
    # down into its details. When a user exits, they are returned to the main
    # menu.
    while True:
        print()
        print("-------------- Capillary List --------------");
        print()

        capillaryRange = len(inputData)

        for i in range(0, capillaryRange):
            print("\t{0:2d}. Capillary {0}".format(i+1))

        print("\t 0. Back to Main Menu")

        try:
            option = int(input("\nPlease enter capillary number: "))

            if option == 0:
                return
            
            elif option >= 1 and option <= capillaryRange:
                
                capillaryCommandMenu(inputData[option - 1],
                                     deltaMatrix[option - 1],
                                     mealData[option - 1],
                                     volData[option - 1],
                                     option,
                                     ulConversion)
            else:
                raise Exception("Invalid Command Provided")
            
        except Exception as e:
            print(e)

def outputToExcel(mealData,
                  volData,
                  microLiterConversion,
                  frameOffset,
                  intervalConversion):
    # Used to output the contents of the meals, applying the conversions
    # to the meal data

    print()
    print("-------------- Excel Output --------------");
    print()
    print("NOTE: Existing files will be overwritten...")
    print()


    collatedName = input("What is the collated file name?: ")
    stackedName  = input("What is the stacked file name?: ")

    directory    = os.getcwd()

    collatedName = directory + "/" + collatedName + ".csv"
    stackedName  = directory + "/" + stackedName  + ".csv"

    preparedData = prepareDataMatrix(mealData,
                                     volData,
                                     microLiterConversion,
                                     frameOffset,
                                     intervalConversion)
    #  preparedData type is list
    try:
        print()
        print("Writing collated data file...")
        
        collatedFile = open(collatedName, 'w')
        addCollatedData(collatedFile, preparedData)                        
        collatedFile.close()
        
        print("Done writing collated data file.")

        print()
        print("Writing stacked data file...")
        
        stackedFile = open(stackedName, 'w')
        addStackedData(stackedFile,preparedData)
        stackedFile.close()
        
        print("Done writing stacked data file.")
        print()

    except Exception as e:
        print(e)

def prepareDataMatrix(mealData, volData, ulConversion, frameOffset, intervalOffset):
    # Our data structures are built in a way to make it easy to add or remove
    # frames on the user interface side of the program. This function takes
    # that data structure and converts it into the data required for the excel
    # output files.
    #
    # It works by 'flattening' the dictionary layers into a two-
    # dimensional matrix called 'preparedData'. Each capillary's meals are
    # pulled out, put in order, and prepared to be output.
    #
    # If meals are in adjacent frames, they are combined into a single meal,
    # starting at the first frame. When output, only the single large meal
    # will be added.

    capillaryIds = []
    maxLength = 0

    for capillary in mealData:
        capillaryIds.append(capillary)

        if maxLength  < len(mealData[capillary]):
            maxLength = len(mealData[capillary])
        
    capillaryIds.sort()

    preparedData = []

    for i in range(0, len(capillaryIds)):

        capillaryMeals    = mealData[capillaryIds[i]]
        capillaryVolMeals = volData[capillaryIds[i]]
        sortedMeals       = []
        sortedVolMeals    = []
        
        for meal in capillaryMeals:
            sortedMeals.append(meal)
        for meal in capillaryVolMeals:
            sortedVolMeals.append(meal)

        sortedMeals.sort()
        sortedVolMeals.sort()

        preparedMeals = []

        for j in range(0, len(sortedMeals)):
            if j == len(sortedMeals):
                break
            frameNumber  = sortedMeals[j]
            meal         = capillaryMeals[frameNumber]
            volMeal      = capillaryVolMeals[frameNumber]
            
            # Roll meals that are in adjacent frames into a single meal.
            combineOffset = 1
            
            while j + 1 < len(sortedMeals):
                if sortedMeals[j] + combineOffset == sortedMeals[ j + 1]:
                    combineOffset = combineOffset + 1
                    meal          = meal + capillaryMeals[ sortedMeals[j+1] ]
                    volMeal       = volMeal + capillaryVolMeals[ sortedVolMeals[j+1] ]
                    sortedMeals.pop(j+1)
                    sortedVolMeals.pop(j+1)
                else:
                    break

            # frameNumber is offset by -1 to compensate for 1 indexed dict format  
            preparedMeals.append(
                {"frame" : "{0:5.5f}".format(frameOffset + (frameNumber - 1) * intervalOffset),
                 "meal"  : "{0:5.5f}".format(meal / ulConversion),
                 "volume": "{0:5.5f}".format(volMeal / ulConversion) })
            
        while len(preparedMeals) < maxLength:
            preparedMeals.append({"frame": "", "meal": "", "volume": ""})
 
        preparedData.append(preparedMeals)

    return preparedData
         
def addCollatedData(file, preparedData):
    # Output the contents of the 'preparedData' in a 'Collated' format to
    # 'file'. The 'collated' contents place each frame next to the meal size
    # that occurred there.

    for i in range(0, len(preparedData)):
        file.write("Capillary {0:d},,, ".format(i + 1))   #.format(i+1) labels capillaries starting at 0+1
                                                          # to get rid of 0 index
    file.write("\n")                   # moves filewriter 1 line down

    if 0 == len(preparedData):
        return

    length = len(preparedData[0])

    for i in range(0, length):
        for j in range(0, len(preparedData)):
            file.write("{0:s},{1:s},{2:s},".format(
                preparedData[j][i]["frame"],
                preparedData[j][i]["volume"],
                preparedData[j][i]["meal"]))
            
        file.write("\n")
    
                
def addStackedData(file, preparedData):
    # Output the contents of the 'preparedData' in a 'Stacked' format to 'file'.
    # 'Stacked' files place the Frame/Times at the top of the spreadsheet, and
    # the meals in microliters at the bottom.
    for i in range(0, len(preparedData)):
        file.write("Capillary {0:d},".format(i + 1))

    file.write("\n")

    if 0 == len(preparedData):
        return

    length = len(preparedData[0])

    for i in range(0, length):
        for j in range(0, len(preparedData)):
            file.write("{0:s},".format(
                preparedData[j][i]["frame"]))
        file.write("\n")
        
    file.write("\n")

    for i in range(0, length):
        for j in range(0, len(preparedData)):
            file.write("{0:s},".format(
                preparedData[j][i]["volume"]))
        file.write("\n")

    file.write("\n")

    for i in range(0, length):
        for j in range(0, len(preparedData)):
            file.write("{0:s},".format(
                preparedData[j][i]["meal"]))
        file.write("\n")

    file.write("\n")
                       
def capillaryCommandMenu(inputData, deltas, meals, volumes, capillaryNumber, ulConversion):
    # Once a capillary is selected, its data is passed here to be viewed/manipulated.
    # The meals are editted here for data. Any frame can be added and any frame
    # can be removed. Utility functions are used to perform that logic.

    while True:
        print()
        print("-------------- Capillary {0} --------------".format(capillaryNumber));
        print()
        print("\t 1. View Current Meals")
        print("\t 2. Add Frame to Meals")
        print("\t 3. Remove Frame from Meals")
        print("\t 4. Clear All Meals from List")
        print("\t 0. Back to Capillary List")

        try:
            option = int(input("\nPlease enter command number: "))

            if option == 0:
                return
            elif option == 1:
                viewMeals(meals, volumes, ulConversion)   
            elif option == 2:
                addMeal(inputData, deltas, meals, volumes)
            elif option == 3:
                removeMeal(inputData, deltas, meals, volumes)
            elif option == 4:
                clearAllMeals(inputData, deltas, meals, volumes)
            else:
                raise Exception("Invalid Command Provided")
        except Exception as e:
            print(e)

def viewMeals(meals, volumes, ulConversion):
    # A utility function to present the contents of the 'Meals' for any given
    # capillary in a clean format. Expects a meal dictionary for a capillary as
    # input.
    
    print()
    print("\tFrame\tMeal Size (uL)")

    mealList = []
    for m in meals:
        mealList.append(m)

    mealList.sort()
    
    for m in mealList:
        print("\t{0:5d}\t{1:5f}".format(m+1, meals[m]/ulConversion))

    print()
    

def addMeal(data, deltas, meals, volumes):
    # A utility function used to allow users to add individual meals to the
    # working set. This is completely user driven. Error checking mechanisms
    # are in place to prevent users from shooting themself in the foot.
    frameCount = len(data)

    print()
    print("Valid Frame Numbers are in the range 2 to {0}".format(frameCount))

    try:
        frame = int(input("Enter Frame Number to be added: "))
        print()
        
        frameIndex = frame - 1
        deltaIndex = frame - 2

        if 2 > frame or frame > frameCount:
            print("Frame number is out of range.")
            return

        if frameIndex in meals:
            print("That frame already exists in this capillary's meals.")
            return

        print("Selected Frame: ")
        print(" Number: {0:3d}\tPixel Distance: {1:3.3f}\tDelta: {2:3.3f}".format(
            frame, data[frameIndex], deltas[deltaIndex]))
 
        if frame > 2 :
            print()
            print("Previous Frame: ")
            print(" Number: {0:3d}\tPixel Distance: {1:3.3f}\tDelta: {2:3.3f}".format(
                frame - 1, data[frameIndex - 1], deltas[deltaIndex - 1]))

        if frame < frameCount:
            print()
            print("Next Frame: ")
            print(" Number: {0:3d}\tPixel Distance: {1:3.3f}\tDelta: {2:3.3f}".format(
                frame + 1, data[frameIndex + 1], deltas[deltaIndex + 1]))

        print() 
        confirmation = "y" # input("Is {0:1d} the correct frame? Confirm (y/n)?: ".format(frame))

        if "y" == confirmation:
            print("Added frame {0:d}".format(frame))
            meals[frameIndex] = deltas[deltaIndex]
            volumes[frameIndex] = deltas[deltaIndex]

        else:
            print("Did not add frame {0}".format(frame))
      
    except Exception as e:
        print(e)

def clearAllMeals(data, deltas, meals, volumes):
    #A utility to clear all meals from meal list in the event that a large number of
    #meals were selected as meals

    print()
    removeAll = input("Clear all meals from list?(y/n): ")
    try:
        print(type(meals))
        if "y" == removeAll:
            meals.clear()
            volumes.clear()
            print("Meal list cleared.")
        else:
            print("List was not cleared.")

    except Exception as e:
        print(e)                      
                      
                      
def removeMeal(data, deltas, meals, volumes):
    # A utility function used to allow users to remove individual meals from the
    # working set. This is completely user driven. Error checking mechanisms
    # are in place to prevent users from shooting themselves in the foot.  
    frameCount = len(data)

    print()
    print("Valid Frame Numbers are in the range 2 to {0}".format(frameCount))

    try:
        frame = int(input("Enter Frame Number to be removed: "))
        print()
        
        frameIndex = frame - 1
        deltaIndex = frame - 2

        if 2 > frame or frame > frameCount:
            print("Frame Number is out of range.")
            return

        if frameIndex not in meals:
            print("That Frame is not in the meal list.")
            return

        print("Selected Frame: ")
        print(" Number: {0:3d}\tPixel Distance: {1:3.3f}\tDelta: {2:3.3f}".format(
            frame, data[frameIndex], deltas[deltaIndex]))

        print() 
        confirmation = "y" #input("Is {0:1d} the correct frame? Confirm (y/n)?: ".format(frame))

        if "y" == confirmation:
            print("Removed frame {0:d}.".format(frame))
            del meals[frameIndex]
            del volumes[frameIndex]
            
        else:
            print("Frame {0} is still in the meal list.".format(frame))
      
    except Exception as e:
        print(e)
            
def getUnitConversion():
    # User input is used to determine the pixels per centimeter in each image.
    # This value, as well as a predetermined cm/uL value are used to provide a
    # unit conversion number. This number is used when outputting data
    # to a file, converting each pixel 'delta' into a meal 'delta'.
    
    print()
    print("-------------- Microliter Settings --------------")
    print() 
    print("In the capillary images, how many pixels are in one centimeter?")
    print()

    try:
##        cm_one   = float(input("Measurement one  : "))
##        cm_two   = float(input("Measurement two  : "))
##        cm_three = float(input("Measurement three: "))
        cm_avg   = float(input("Measurement: "))
        print()

        #cm_avg   = (cm_one + cm_two + cm_three) / 3.0
        print("Measurement Average: {0:2.3f}".format(cm_avg))

        units_conversion = cm_avg * CM_PER_UL

        return units_conversion

    except Exception as e:
        print(e)

def getZeitgeiberTime():
    # User input is used to determine the default frame offset and the frame
    # interval using Zeitgeiber time. The defaults 'DEFAULT_FRAME' and
    # 'DEFAULT_INTERVAL' are used in case frames are desired.
    #
    # IMPLEMENTATION NOTE: The defaults are numbers that when used in the
    # correct functions later on, result in simple frame numbers.
    print()
    print("-------------- Zeitgeiber Settings --------------") 
    print()
    try:
        useDefault  = input("Use frame numbers instead of Zeitgeiber Times? y/n: ")

        if "y" == useDefault:
            return DEFAULT_FRAME, DEFAULT_INTERVAL
                
        day         = int(input("How many days should be added to the zeitgeiber time?: "))
        start       = int(input("Enter start Zeitgeiber hour (wait for minutes!): "))
        startMin    = int(input("Minute of the Hour: "))
        start       = start + startMin / 60
        minPerFrame = float(input("What time interval in minutes were your pictures taken?: "))

        frameOffset = (day * HOURS_PER_DAY) + start
        interval    = minPerFrame / float(MINUTES_PER_HOUR)

        return frameOffset, interval

    except Exception as e:
        print(e)

                            # -------------
                            # Main Function 
                            # -------------
def runAutoCafe():
    # This is the primary function. The highest level description of the logic
    # belongs here.
    
    try:
        printBanner()
        inputData                 = getInput()
        deltaMatrix, ulConversion = getDeltas(inputData)
        mealData, volData         = getMealData(deltaMatrix,ulConversion,ORIGINAL_VOL)
       
        manipulateData(inputData, deltaMatrix, mealData, volData, ulConversion)

    except Exception as inst:
        print("-------------")
        input(inst)


                            # -----------
                            # Entry Point
                            # -----------
runAutoCafe()
