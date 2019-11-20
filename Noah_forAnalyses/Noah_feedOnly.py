
#   Noah.py - A script analyze and structure Autocafe software output (created by Keith Murphy)
#             as well as "Tracker" output(created by Robert Huber)
#                     
#   Copyright (C) 2013 Keith Murphy & James Quinn
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

                            # --------------------
                            # Implementation Notes
                            # --------------------

# The core components of the script are broken up into individual functions
#  Each function describes
# itself inline immediately following the function definition.
#
# The script's entry point is located on the last line of the script with a
# call to the 'runNoah' function. This will kick off the script, read in
# the user specified input file, and begin processing.

                           # ---------
                           # Constants
                           # ---------

numEntries    = 1
feedFrame     = 30         # feedFrame is the window size in secs for grabbing the mean position of a dye-band (reduces noise) 
                           # numEntries is number of elements / read / fly
                           # Typically depending on your version of JavaGrinders

                           # ---------
                           # AutoCAFE Constants
                           # ---------
                            
SIMPLE_DEVIATION = 2.0     # The naive standard deviation meal model
CM_PER_UL        = 1.0075   # Calculated value for cm/uL
HOURS_PER_DAY    = 24      # Number of hours in a day
MINUTES_PER_HOUR = 60      # Number of minutes per hour
SECS_PER_MIN     = 60      # Number of seconds per minute
DEFAULT_FRAME    = 0       # A default frame offset for Zeitgeiber times
DEFAULT_INTERVAL = 1       # A default frame interval for Zeitgeiber times
MEALPULL_SD      = 4.      # The meal pull sd for recalculating noise sd's
FINAL_SD         = 5       # Final SD threshold for pulling meals
ORIGINAL_VOL     = 5       # Original Volume of liquid food in capillary 


                           #   -------------------
                           #        Noah Script
                           #   -------------------

# Code for taking Drosophila "Tracker" program data and genrating distance
# traveled values for all the individual flies. Also maintains a binning
# function for quick compilation of data as well as a noise removal fuction


import os
import time
from math import acos
from math import atan2
global flyCount
global pixPerCM
global zeitStart


def printBanner():
    # This function is used to print the name and description
    # of this script. Returns the name of the input file to
    # be processed.
    print("\n   Noah_feedOnly.py - A script to analyzes data from the ARC\n"
          "   containing only the food tracking from ARCController.java\n"
          "     \n"
          "                 \n"
          "   Copyright (C) 2019 Scarlet Park and Keith Murphy \n"
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
          "\n")
    print("            -------------------\n"
          "               Noah_feedOnly\n"
          "            -------------------\n\n"
          "   Capillary tracking information processing code, modified from Noah15.7.py \n"
          "                                                   \n"
          "   Input files must be tracker output file(.txt) or autocafe output(.csv/.txt)\n"
          "   Requires python 3.3, found in download section of pythons homepage.")



def commandMenu():
    # This is the command menu list which allows the user to direct the
    # program to specified function

    while True:

        print("\n\n\t  ----- Noah Menu ----- ")
        print()
        print("\t 1.  Select ARC Data File")
        print("\t 2.  Select AutoCAFE Data File")
        print("\t 3.  Analyze/Synthesize Data")
        print("\t 4.  Bin Feeding Data")
        print("\t 5.  Individual Meals Output")
        print("\t 0.  Exit Program")
        print("")


        #print("\t 15. Bout Length / Freq array")
        #print("\t 16. Grooming integration")

        try:

            option = int(input("\nEnter Command Number: "))

            if option   == 0:
                return

            elif option == 1:
                file  = getInput()
                readsPerSec,workList,shortFileName,zeitStart,feedData,pixPerCM  = parseData(file)
                mealTimes, mealValues, mealDurations, feedFileName = autoCafe(feedData,readsPerSec,pixPerCM,shortFileName)
                
            elif option == 2:
                file = getInput()
                mealTimes, mealValues, mealDurations, feedFileName = parseMealData(file)


            elif option == 3:
                try:                                                    # This is just in case there is no meal data associated with data, if mealTimes reference returns an error it just makes mealtimes and mealvals empty lists
                    blank = mealTimes[0]
                except:
                    mealTimes     = []
                    mealValues    = []
                    mealDurations = []
                    blank = [0]
                    for x in range(len(sleep)):
                        mealTimes.append(blank)
                        mealValues.append(blank)
                        mealDurations.append(blank)
                    print("Alert! No feeding data loaded for synthesis")
                try:
                    useFileName = shortFileName
                except:
                    useFileName = feedFileName

                synth(mealTimes,mealValues,mealDurations,readsPerSec,workList,useFileName)

            elif option == 4:
                try:
                    mealBins, timeBins, header = feedBins(mealTimes,mealValues,mealDurations,feedFileName)
                except:
                    print("Alert! Feeding data may not be loaded.")

            elif option == 5:
                mealRelation(mealTimes,mealValues,mealDurations,feedFileName)


        except Exception as e:
            print(e)


def getInput():
    # This function asks the user for an input file. Once it's
    # opened, the data is parsed into a two-dimensional matrix.
    # Data is returned from the function once parsed successfully.
    global directory
    global zeitStart
    global pixPerCM

    try:
        del zeitStart
    except:
        pass

    inputFile = input("Type input file path (or click and drag) to continue: ")

    try:
        file = open(inputFile)
        fn = str(inputFile)
        if "\\" in fn:
            dL = fn.split("\\")
            directory = "\\".join(dL[0:-1])
        elif "/" in fn:
            dL = fn.split("/")
            directory = "\\".join(dL[0:-1])
        else:
            directory = os.getcwd()
        os.chdir(directory)
        print("working directory set to " + directory)

    except:
        errorMsg = "Error: Unable to open file: '" + inputFile + "'. Try removing spaces or hyphens in file name."
        raise Exception(errorMsg)

    return file

def getFileVectors(file):
    # This function gets any tab delmiited file and makes each column into a vector
    # and attempts to convert all elements into float values, but will pass on any
    # any string values

    print("Loading file contents...")
    myList = []
    for line in file:
        myList.append(line)
    print("File loaded.")
    print("Parsing file contents...")
    print("")
    workList = []

    x = 0
    for line in myList:
        prog = x / len(myList)
        update_progress(prog)
        lineValues = line.split('\t')
        workList.append(lineValues)

    exptLengthHr = len(workList) / 3600

    for a in range(len(workList)):
        prog = a / len(workList)
        update_progress(prog)
        for b in range(len(workList[a])):
            try:
                workList[a][b] = float(workList[a][b])
            except:
                pass
    workList = transpose(workList)
    print("")
    print("Parsing file contents complete.")
    return (workList, exptLengthHr)


def parseData(file):
    # This function removes the time stamp and creates a list of lists for each fly
    # which contains all time points with the x and y coordinate as well as size/direction data
    # which are then further reduced to euclidean distance between each time point.
    # IMPLEMENTATION NOTE: A noise removal if statement is incorporated to remove
    # small oscillating motions which are likely noise but you can comment it out
    # to get the exact perceived motion data if you'd like

    global pixPerCM

    workList, exptLengthHr = getFileVectors(file)
    print("length of experiment: " + str(exptLengthHr) + " hours")
    timeStamp = workList.pop(0)

    # if empty reads are given by javagrinders delete the column
    workList = [vector for vector in workList if vector[0] != ""]

    flyCount = len(workList)
    print("Dataset contains", flyCount, "flies.")
    try:
        pixPerCM == 1
    except:
        pixPerCM = int(input("Enter pixels / centimeter: "))
    readsPerSec = float(input("How many readings per second are there in your data: "))
    zeitStart = getZeitStart()

    # if first value is missing, fill in with first non -1 value

    for vector in range(len(workList)):
        i = 0
        while workList[vector][i] == -1:
            i = i + 1
            if i > len(workList):
                break
        try:
            workList[vector][0] = workList[vector][i]
        except:
            workList[vector][0] = 0

    # if last value is missing, fill in with last non -1 value
    for vector in range(len(workList)):
        i = 1
        try:
            while workList[vector][i*-1] == -1:
                i = i + 1
            workList[vector][-1] = workList[vector][i*-1]
        except:
            break

    div = int(len(workList)/numEntries)
    foodTrack   = workList[:div]

    print("Cleaning missed food tracking data...")
    print("")
    # linear interpolation across gaps of -1's (missed values), used to clean dye-band data
    missedFeed = []
    for capillary in range(len(foodTrack)):
        prog = capillary / len(foodTrack)
        update_progress(prog)
        miss = 0
        read = 1

        while read < len(foodTrack[capillary]):
            if foodTrack[capillary][read] == -1:
                gap = 1

                try:
                    while foodTrack[capillary][read + gap] == -1:
                        miss = miss + 1
                        gap = gap + 1

                    shift = ((foodTrack[capillary][read+gap]-foodTrack[capillary][read-1])/ (gap + 1))
                    for i in range(0,gap):
                        foodTrack[capillary][read+i] = foodTrack[capillary][read-1] + shift*i
                    read = read+gap
                except:
                    read = read+gap

            else:
                read = read + 1
        missedFeed.append( (miss / len(foodTrack[capillary]))*100)
 
    print("")
    print("Data cleaned.")
    print("Processing food tracking data.")

    feedFrameS = int(readsPerSec * feedFrame) # feed frame converted to seconds
    feedData = []
    for vector in range(len(foodTrack)):
        prog = vector / len(foodTrack)
        update_progress(prog)
        dataVector = []    
        for read in range(0,len(foodTrack[vector]),feedFrameS):
            tempList = foodTrack[vector][read:read+feedFrameS]
            try:
                modeT = mode(tempList)   # get mode of population to clear any far outliers

                for i in range(len(tempList)):
                    if tempList[i] - abs(modeT) > pixPerCM*0.3:
                        tempList[i] = modeT

            except:
                pass

            dataVector.append(avg(tempList))

        # Custom noise smoothing algorithm using a variation of moving average.
        # Takes advantage of the fact that the meniscus only moves in one direction,
        # and iterates through exponentially decreasing filter widths.
        # Contributed by Jin Hong Park

        for interval in [8,8,4,4,2,2,1,1]:                                                          # -----1---- Comment out these 5 lines
            fwidth = pow(2,interval)                                                                # -----2---- to remove the noise filter
            for j in range (fwidth, len(dataVector)-fwidth):                                        # -----3----
                if dataVector[j] < dataVector[j-fwidth] or dataVector[j]>dataVector[j+fwidth]:      # -----4----
                    dataVector[j]=(dataVector[j-fwidth]+dataVector[j+fwidth])/2                     # -----5----
        feedData.append(dataVector)

    shortFileName = cutFileName(file)
    toExcelNamed(feedData, "cleanedFeedTrack_" + shortFileName)

    print("")
    print("Done processing.")
       
    shortFileName = cutFileName(file)
    
    return(readsPerSec,workList,shortFileName,zeitStart,feedData,pixPerCM)

def parseMealData(file):

    # This function splits the lines of the import file named
    # file by tabs. It then generates a list of lists of all the flies
    # meal times and all of their meal sizes which are the outputs

    file.seek(0)
    print("Parsing file contents....")
    mealList    = []
    zeitTimes   = []
    zTimes      = []
    meals       = []
    durations   = []
    indivZTimes = []
    indivMeals  = []
    indivDurs   = []
    itemsPerFly = 3

    isLabeled = isLabeledFile(file)
    if False == isLabeled:
        file.seek(0)
        for line in file:
            lineValues = line.split(',')
            mealList.append(lineValues)
        flynum      = int(len(mealList[0])/3)
        mealList.pop(0)

    else:
        file.seek(0)
        for line in file:
            lineValues = line.split('\t')
            mealList.append(lineValues)
    try:
        skip = 0
        for f in range(flynum):
            for i in range(0,len(mealList)):                      # This code generates two lists of both the meals and the zeit times
                try:
                    float(mealList[i][f+skip])
                    indivZTimes.append(mealList[i][f + skip])
                    indivMeals.append(mealList[i][f + skip + 1])
                    indivDurs.append(mealList[i][f + skip + 2])
                except:
                    pass

            zTimes.append(indivZTimes)
            meals.append(indivMeals)
            durations.append(indivDurs)
            indivMeals  = []
            indivZTimes = []
            indivDurs   = []
            skip = skip + (itemsPerFly - 1)

        for a in range(len(zTimes)):
            for b in range(len(zTimes[a])):
                zTimes[a][b] = float(zTimes[a][b])
                meals[a][b]  = float(meals[a][b])
                durations[a][b]  = float(durations[a][b])


        zeitTimes = zTimes
        mealList  = meals
        mealDurs  = durations

    except:
        errorMsg = "Error: Check File Structure. Look for gaps in data."
        raise Exception(errorMsg)

    feedFileName = cutFileName(file)
    print("Parsing file contents complete....")
    print("n =",flynum)
    roll = input("Combine feeding bouts within given temporal distance?(y/n): ")

    if roll == 'y' or roll == 'yes' or roll == 'Yes' or roll == 'YES':
        mealList,mealDurs,zeitTimes = rollBouts(mealList,mealDurs,zeitTimes)

    return zeitTimes, mealList, mealDurs, feedFileName

def mealTimesToZS(mealTimes):
    # converts mealTimes to zeitgeber seconds

    mealTimesZS = []
    for i in range(len(mealTimes)):
        indieMeals = []
        for n in range(len(mealTimes[i])):
            indieMeals.append(round((mealTimes[i][n] * 60 * 60),0))
        mealTimesZS.append(indieMeals)

    return(mealTimesZS)
                        

def rollBouts(mealValues,mealDurations,mealTimes):
    # Because there is no formal definition for what a meal is,
    # this function allows the user to roll together
    # meals within a user specified temporal distance

    rollDistance = float(input("Enter temporal distance between bouts for compression(s): "))
    rollDistance = rollDistance / 3600

    for fly in range(len(mealTimes)):
        for meal in range(len(mealTimes[fly])):
            try:
                if mealTimes[fly][meal + 1] - mealTimes[fly][meal] <= rollDistance:
                    mealValues[fly][meal + 1] = mealValues[fly][meal] + mealValues[fly][meal + 1]
                    mealDurations[fly][meal + 1] = mealDurations[fly][meal] + mealDurations[fly][meal + 1]
                    mealValues[fly][meal]  = " "
                    mealDurations[fly][meal] = " "
                    mealTimes[fly][meal]   = " "
            except:
                pass

    for fly in range(len(mealTimes)):
        mealTimes[fly]     = [meal for meal in mealTimes[fly] if meal != " "]
        mealValues[fly]    = [meal for meal in mealValues[fly] if meal != " "]
        mealDurations[fly] = [meal for meal in mealDurations[fly] if meal != " "]

    return(mealValues,mealDurations,mealTimes)

################################################
############ General Stats Generator ###########
################################################

def synth(mealTimes,mealValues,mealDurations,readsPerSec,workList,useFileName):
    # This function runs a number of different procedures for capturing the basic behavior of a
    # fly. All outputs are initiated early on and listed at the end of function

    ###################
    #----CONSTANTS----#
    ###################

    flies          = len(mealValues)
    print("Assumes ZT 0 is start of lights on. ")
    print("Make sure that this matches your feeding dataset length")
    zeitStart = getZeitStart()


    # below is short code to convert mealTimes from hours into seconds for indexing purposes
    mealTimesZS = []      # mealTimes converted to z-time seconds
    for i in range(len(mealTimes)):
        indieMeals = []
        for n in range(len(mealTimes[i])):
            indieMeals.append(round((mealTimes[i][n] * 60 * 60),0))
        mealTimesZS.append(indieMeals)

    flyCount = ["Fly #"]              # Header with Fly # generator
    for x in range(len(mealValues)):
        flyCount.append(x + 1)

    # check if # of flies in feeding data matches tracking data
    if len(mealValues) == flies:

    # The section below creates all the lists of paramters we'll look at, each having a title describing the data as the 0th element
    # Many of these measurements will not show up in the output unless indicated in statsList at the end of this function

        Feed                = ["Feeding (ul)"]
        avgMeal             = ["Avg Bout Size "]
        numMeal             = ["Meal frequency"]
        avgDuration         = ["Meal Duration (s)"]
        dTotFeed            = ["Daytime feeding"]
        nTotFeed            = ["Nighttime feeding"]
        dAvgMeal            = ["Daytime meal size"]
        nAvgMeal            = ["Nighttime meal size"]
        dFreq               = ["Daytime feeding frequency"]
        nFreq               = ["Nighttime feeding frequency"]
        iMealInts           = ["Satiety ratio"]
        daySatiety          = ["NightTime satiety"]
        nightSatiety        = ["Daytime satiety"]
        firstMeal           = ["1st meal (ul)"]
        secondMeal          = ["2nd meal (ul)"]
        thirdMeal           = ["3rd meal (ul)"]
        fourthMeal          = ["4th meal (ul)"]
        lastMeal            = ["last meal (ul)"]
        allButFirstandLast  = ["All but 1st and last meal (ul)"]
        maxMeal             = ["Maximum meal size (ul)"]
        fastingPer          = ["Fasting period length (hr)"]
        firstMealTime       = ["First meal time"]
        secondMealTime      = ["Second meal time"]
        thirdMealTime       = ["Third meal time"]
        non                 = [""]

        print("Generating statistics...")

        mealTimeStats      = []
        intermealIntervals = []

        # i is general iterator for each fly
        for i in range(flies):
            prog = i / flies
            update_progress(prog)

            ################################################################
            ## Casual Calculations to describe basic features of behavior ##
            ################################################################

            try:
                Feed.append(sum(mealValues[i]))
            except:
                Feed.append("----")
            try:
                avgMeal.append(avg(mealValues[i]))
            except:
                avgMeal.append("----")
            try:
                avgDuration.append(avg(mealDurations[i]))
            except:
                avgDuration.append("----")
            try:
                if mealTimes[i][0] > 0:                      # Safety net in case feeding list is empty with
                    numMeal.append(len(mealValues[i]))       # 0's in which case it would normally count a freq of 1
                else:
                    numMeal.append("----")
            except:
                numMeal.append("----")
            try:
                firstMeal.append(mealValues[i][0])
            except:
                firstMeal.append("----")
            try:
                secondMeal.append(mealValues[i][1])
            except:
                secondMeal.append("----")
            try:
                thirdMeal.append(mealValues[i][2])
            except:
                thirdMeal.append("----")
            try:
                fourthMeal.append(mealValues[i][3])
            except:
                fourthMeal.append("----")
            try:
                lastMeal.append(mealValues[i][-1])
            except:
                lastMeal.append("----")
            try:
                allButFirstandLast.append(avg(mealValues[i][1:-1]))
            except:
                allButFirstandLast.append("----")
            try:
                firstMealTime.append(mealTimes[i][0])
            except:
                firstMealTime.append("----")
            try:
                secondMealTime.append(mealTimes[i][1])
            except:
                secondMealTime.append("----")
            try:
                thirdMealTime.append(mealTimes[i][2])
            except:
                thirdMealTime.append("----")
            try:
                maxMeal.append(max(mealValues[i]))
            except:
                maxMeal.append("----")

            ###############################
            #### Satiety Ratio#############
            ###############################
            if len(mealTimesZS[i]) > 2:
                try:
                    intermealIntList = []
                    for time in range(len(mealTimesZS[i]) - 1):
                        intermealInt = (mealTimesZS[i][time + 1] - mealTimesZS[i][time]) / 3600
                        intermealIntList.append(intermealInt)
                    fastingPer.append(avg(intermealIntList))
                    iMealInts.append(avg(intermealIntList)/ avg(mealValues[i]))
                except:
                    fastingPer.append("----")
                    iMealInts.append("----")
            else:
                fastingPer.append("----")
                iMealInts.append("----")

            #######################################
            #### Night Vs Day Feed calculations ###
            #######################################        
            dayMeals   = []
            nightMeals = []

            try:

                for n in range(len(mealTimesZS[i])):
                    if (mealTimesZS[i][n] % 86400) <= 43200:
                        dayMeals.append(mealValues[i][n])
                    else:
                        nightMeals.append(mealValues[i][n])

            except:
                blank = 0
            try:
                dTotFeed.append(sum(dayMeals))
            except:
                dTotFeed.append(0)
            try:
                nTotFeed.append(sum(nightMeals))
            except:
                nTotFeed.append(0)
            try:
                check = 10 / dayMeals[0]
                dAvgMeal.append(avg(dayMeals))
            except:
                dAvgMeal.append(0)
            try:
                check = 10 / nightMeals[0]
                nAvgMeal.append(avg(nightMeals))
            except:
                nAvgMeal.append(0)
            try:
                check = 10 / dayMeals[0]
                dFreq.append(len(dayMeals))
            except:
                dFreq.append(0)
            try:
                check = 10 / nightMeals[0]
                nFreq.append(len(nightMeals))
            except:
                nFreq.append(0)

        statsList = [flyCount,Feed,numMeal,avgMeal,avgDuration,dTotFeed,nTotFeed,dAvgMeal,nAvgMeal,dFreq,nFreq,iMealInts,firstMeal,
                    secondMeal,thirdMeal,fourthMeal,lastMeal,allButFirstandLast,maxMeal,fastingPer,firstMealTime,secondMealTime,thirdMealTime]

        print("")
        print("Statistics complete.")
        toExcelNamed(transpose(statsList),"stats_" + useFileName )


        tfList=[]
        for i in range (flies):
            try:
                tfList.append(mealValues[i])
            except:
                tfList.append("----")


    else:
        print("The data files do not match sampling parameters.")



def isLabeledFile(file):
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



######################################
########  Binning Functions ##########
######################################

def feedBins(mealTimes,mealValues,mealDurations,feedFileName):
    # This function goes through list and appends times and meal sizes
    # within specified range groups to separate lists. For instance if
    # your bin interval is 3 it will make lists of all times 0-3,3-6,6-9 etc
    # as well as the meals that correspond to their index couterpart in the
    # input file

    try:
        binSize = float(input("Enter Bin Size(mins): "))
        binSize = binSize / 60

    except:
        print("Invalid Entry")
        return
    try:
        masterMealBins    = []
        masterTimeBins    = []
        masterSatietyBins = []
        maxZeitTime       = Max2D(mealTimes)
        UsersBinStart     = getZeitStart()

        print("Binning Data....")
        for fly in range(len(mealTimes)):
            timeBins    = []
            mealBins    = []
            satietyBins = []
            binStart = float(UsersBinStart)

            while binStart < maxZeitTime:
                timeBin  = []
                mealBin  = []
                satBin   = []                                                      # time to next meal/ meal size
                for meal in range(len(mealTimes[fly])):
                    if  binStart < mealTimes[fly][meal] <= binStart + binSize:     # Check if time is above moving start and below moving start + binsize
                        timeBin.append(mealTimes[fly][meal])
                        mealBin.append(mealValues[fly][meal])

                        try:
                            satBin.append( (mealTimes[fly][meal+1] - mealTimes[fly][meal])/mealValues[fly][meal] )
                        except:
                            satBin.append("")
                if mealBin == []:
                    mealBin = [0]

                timeBins.append(timeBin)
                mealBins.append(mealBin)
                satietyBins.append(satBin)
                binStart = binStart + binSize

            masterMealBins.append(mealBins)
            masterTimeBins.append(timeBins)
            masterSatietyBins.append(satietyBins)

        header = []
        for i in range(len(masterMealBins[0])):
            header.append(float(UsersBinStart) + i*binSize)

        mealBins       = masterMealBins                   # 3D matrix layered   meals -> bins -> fly
        timeBins       = masterTimeBins
        satietyBins    = masterSatietyBins

        masterMealSum  = []
        masterMealFreq = []
        masterMealSize = []
        masterSatiety  = []

        for fly in range(len(mealBins)):
            flyMealSum  = []
            flyMealFreq = []
            flyMealSize = []
            flySatiety  = []

            for bins in range(len(mealBins[fly])):
                binSum = float(sum(mealBins[fly][bins]))
                flyMealSum.append(binSum)
                zeros = float(mealBins[fly][bins].count(0))                          # can't use len for frequency because empty lists contain [0]
                freq = int(len(mealBins[fly][bins])) - zeros
                flyMealFreq.append(freq)                                             #  so counting 0's and subtracting from len instead
                if freq > 0:
                    flyMealSize.append(binSum/freq)
                else:
                    flyMealSize.append("")
                try:
                    flySatiety.append(avg(satietyBins[fly][bins]))
                except:
                    flySatiety.append("")

            masterMealSum.append(flyMealSum)
            masterMealFreq.append(flyMealFreq)
            masterMealSize.append(flyMealSize)
            masterSatiety.append(flySatiety)

##        norm = input("Normalize Bins as fraction of total?(y/n): ")
##        if norm == "y" or norm == "yes" or norm == "YES" or norm == "Yes":
##                print("Note: Blanks are replaced with 0's and may skew data")
##                print("Note: Avg Meal Size is not normalized")
##                masterMealSum  = normalizeToMean(masterMealSum)
##                masterMealFreq = normalizeToMean(masterMealFreq)
                # does not normalize meal size

        masterMealSum.insert(0,header)
        masterMealFreq.insert(0,header)
        masterMealSize.insert(0,header)
        masterSatiety.insert(0,header)

        masterMealSum  = transpose(masterMealSum)
        masterMealFreq = transpose(masterMealFreq)
        masterMealSize = transpose(masterMealSize)
        masterSatiety  = transpose(masterSatiety)

        finalList = [["Total Feeding Bins (evaporation corrected)"]]
        finalList = finalList + masterMealSum

        addFreq = input("Add bins for frequency (y/n): ")
        addSize = input("Add bins for meal size (y/n): ")
        addSat  = input("Add bins for satiety (y/n): ")

        blank   = [[""]]
        if addFreq == "y":
            title = [["Meal Frequency Bins"]]
            finalList = finalList + blank + title + masterMealFreq
        if addSize == "y":
            title = [["Meal Size Bins"]]
            finalList = finalList + blank + title + masterMealSize
        if addSat  == "y":
            title = [["Satiety Ratio Bins"]]
            finalList = finalList + blank + title + masterSatiety

        print("Feeding bins generated.")

        toExcelNamed(finalList, "feedBins_" + str(int(binSize))+"hrs_"+feedFileName)

    except Exception as e:
        print(e)
    return mealBins, timeBins, header


def meanBinGen(thingToBin,readsPerSec,shortFileName,label):
    # This function averages values of any type into specified bin sizes as to reduce the
    # number of data points in a graph or data set, This could be used
    # for making the seconds readings into minutes, hours, etc. Takes a list of lists
    # organized as [fly][attribute]

    secChart()
    zeitStart = getZeitStart()
    binSize   = int(input("Enter bin size in seconds: "))
    binSize   = int(binSize*readsPerSec)

    ########################
    #### Bin generators ####
    ########################
    print("Generating bin's")
    thingBins = []
    for fly in range(len(thingToBin)):
        loc = 0                                           # loc is bin location
        indivBins = []
        while loc < len(thingToBin[fly]):                      # can also be while binLoc + step to cut any partial bins out entirely
            try:
                thingBin =  avg(thingToBin[fly][loc:loc+binSize])
            except:
                thingBin = ""
            indivBins.append(thingBin)
            loc = loc + binSize
        thingBins.append(indivBins)
    print("Bin's sucessfully generated.")

    ###############       
    ### Outputs ###
    ###############

    header = []
    for x in range(len(thingBins[0])):
        header.append(float(zeitStart + ((binSize*x)/3600)))
    title = ["Z Time"]
    for i in range(len(thingBins)):
        title.append(i+1)
    thingBins = transpose(thingBins)
    for i in range(len(thingBins)):
        thingBins[i].insert(0,header[i])

    thingBins.insert(0,title)
    finalBins= []
    addWord = ["Total Count Bins (seconds)",""]
    finalBins.append(addWord)
    for i in range(len(thingBins)):
        finalBins.append(thingBins[i])

    toExcelNamed(finalBins,label + str(int(binSize/60))+"_mins" + shortFileName)


def getZeitStart():
    # gets start zeitgeber time from user
    global zeitStart
    try:
        zeitStart == 1
    except:
        try:
            zeitStart = float(input("Enter start Zeitgeiber hour (wait for minutes!): "))
            zeitMin   = float(input("Minute of the hour: "))
            zeitStart = zeitStart + (zeitMin/60)
        except:
            zeitStart = 0
            print("Default ZT start time = 0")
    return zeitStart


def mealRelation(mealTimes,mealValues,mealDurations,feedFileName):

    flyNum         = []
    mealSizes      = []
    mealTime       = []
    mealDurs       = []
    timeSinceLast  = []
    timeToNext     = []


    # mealTimes converted to z-time seconds
    mealTimesZS = []
    for i in range(len(mealTimes)):
        indieMeals = []
        for n in range(len(mealTimes[i])):
            indieMeals.append(round((mealTimes[i][n] * 60 * 60),0))
        mealTimesZS.append(indieMeals)
    

    
    for fly in range(len(mealTimes)):
        for meal in range(len(mealTimes[fly])):
            mealSizes.append(mealValues[fly][meal])
            mealTime.append(mealTimes[fly][meal])
            mealDurs.append(mealDurations[fly][meal])
            flyNum.append(fly+1)

            if meal > 0:
                timeSinceLast.append(mealTimes[fly][meal] - mealTimes[fly][meal-1])

                    
            else:
                timeSinceLast.append("")


            try:
                if meal < len(mealTimes[fly]):
                    timeToNext.append(mealTimes[fly][meal + 1] - mealTimes[fly][meal])



                else:
                    timeToNext.append("")


            except:
                timeToNext.append("")



    final = [flyNum,mealSizes,mealTime,mealDurs,timeSinceLast,timeToNext]
    final = transpose(final)

    doDiv = input("Sort by set interval(y/n): ")
    if doDiv == "y":
        div = int(input("Set sort interval: "))
    else:
        div = 1
    bulkList = []
    for i in range(div):
        subList = []
        for n in range(i,len(mealTimes),div):
            for read in range(len(final)):
                if final[read][0] == n:
                    subList.append(final[read])
        bulkList.append(subList)

    for i in range(len(bulkList)):
        x = bulkList[i]
        toExcelNamed(bulkList[i],"batch_" + str(i) + "_" + feedFileName)
        

def filterFragments(vector,minRep):
    # This function takes a binary list and filters all 1 values that are not part of a series of
    # 1's greater than the specified minRep input

    filterVector = []
    minRep = int(minRep)
    for read in range(len(vector)):
        if vector[read] == 1:
            try:
                if sum(vector[read:read + minRep]) == minRep or filterVector[-1] == 1:
                    filterVector.append(1)
                else:
                    filterVector.append(0)
            except:
                filterVector.append(0)
        else:
            filterVector.append(0)
    return(filterVector)


########################################
###### Commonplace functions ###########
########################################

def rangeCheck(minimum,maximum,array):
    # function for checking if any value in an array is within min and max
    check = 0
    for i in range(len(array)):
        if array[i] >= minimum and array[i] <= maximum:
            check = 1
    return check

def avg (group):
    # returns average of a list after filtering all non ints / floats
    group = [i for i in group if type(i) != str]
    average = (sum(group)) / len(group)
    return(average)

def distance(x1, y1, x2, y2):
    # Function for finding Euclidean distance between 2 sets of x,y coordiantes
    # using pythagorean theorem

    dx = x2 - x1
    dy = y2 - y1
    dsquared = dx**2 + dy**2
    totalDistance = dsquared**0.5
    return totalDistance

def normalizeToMean(matrix):
    #simple function for normalizing arrays in matrix to their own mean
    normList = []
    for i in range(len(matrix)):
        for n in range(len(matrix[i])):        #Clears all '' found in meal size
            if matrix[i][n] == '':
                matrix[i][n] = 0

        normIndiv = []
        for x in range(len(matrix[i])):
            try:
                normIndiv.append(matrix[i][x] / sum(matrix[i]))
            except:
                normIndiv.append(0)

        normList.append(normIndiv)
    return normList

def normalizeToPercent(array):
    normalizedArray = []
    maxX   = max(array)
    minX   = min(array)
    rangeX = maxX - minX
    for i in range(len(array)):
        try:
            normalizedArray.append( ((array[i]-minX) / rangeX)*100)
        except:
            normalizedArray.append("")

    return normalizedArray


def toExcel(matrix):
    # sends file to excel as .csv with each list as a row, list must be 2D
    directory    = os.getcwd()
    outputDataName = input("Name your output file: ")
    outputDataName = directory + "/" + outputDataName + ".csv"

    import csv

    with open(outputDataName,'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerows(matrix)

def toExcelNamed(matrix,name):
    # toExcel where name can be inserted to auto write file without user input
    directory    = os.getcwd()
    outputDataName = name
    outputDataName = directory + "/" + outputDataName + ".csv"

    import csv

    with open(outputDataName,'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerows(matrix)

def transpose(matrix):
    # Flips matrix rows into columns and vice versa. Matrix should contain lists of = length,
    # otherwise short lists will be extended with ""
    listLength = []
    for i in range(len(matrix)):
        listLength.append(len(matrix[i]))
    long = max(listLength)
    for i in range(len(matrix)):
        while len(matrix[i]) < long:
            matrix[i].append("")
    longList = []
    for i in range(len(matrix[0])):
        shortList = []
        for n in range(len(matrix)):
            shortList.append(matrix[n][i])
        longList.append(shortList)
    return longList

def diviAv(matrix):
    # takes columns at a given interval and gets avg across them
    # returns avg vectors of each as a matrix

    interval = int(input("Sort interval: "))

def secChart():
    # simple print statement to guide the user on time selection
    print(" 5 mins  = 300   sec's")
    print(" 10 mins = 600   sec's")
    print(" 30 mins = 1800  sec's")
    print(" 1 hr    = 3600  sec's")
    print(" 3 hr's  = 10800 sec's")
    print(" 4 hr's  = 14400 sec's")
    print(" 6 hr's  = 21600 sec's")

def cutFileName(fileName):
    # function cuts .xxx file type from name and takes only elements up to \ from backend of fileName string
    try:
        fileName = str(fileName)
        i = 1
        while fileName[-i] != ".":
            fileName = fileName[0:-1]
        fileName = fileName[0:-1]
        i = 1
        while fileName[-i] != '\\':
            i = i + 1
        i = i - 1
        cutFileName = fileName[-i:len(fileName)]
    except:
        print("No file type provided")
        cutFileName = input("Name file associations")
    print("")
    print("File associations set to " + cutFileName)
    return cutFileName


import time, sys
##########Status Bar#########
# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 30 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\r[{0}] {1}% {2}".format( "="*block + " "*(barLength-block), round(progress*100,1), status)
    sys.stdout.write(text)
    sys.stdout.flush()

def Max2D(data):
    # function for finding max value in 2D matrix or list of lists
    maximum = 0
    for x in range(len(data)):
        try:
            if max(data[x]) > maximum:        # short code for finding max in array of lists
                maximum = max(data[x])
        except:
            maximum = maximum
    return maximum

def sum2D(matrix):
    outerSum = []
    for i in range(len(matrix)):
        tempSum = sum(matrix[i])
        outerSum.append(tempSum)
    finalSum = sum(outerSum)
    return finalSum

def flatten2D(matrix):
    # This function will take the sum of elements at each position for a series of vectors and make them into 1 sum vector
    flatten = []
    for element in range(len(matrix[0])):
        tempHold = []
        for vector in range(len(matrix)):
            tempHold.append(matrix[vector][element])
        flatten.append(sum(tempHold))
    return flatten

def Min2D(data):
    # function for finding min value in 2D matrix or list of lists
    minimum = data[0][0]
    for x in range(len(data)):
        try:
            if min(data[x]) < minimum:        # short code for finding max in array of lists
                minimum = min(data[x])
        except:
            minimum = minimum
    return minimum

def meanAndDeviation(data):
    # Python algorithm to compute mean and standard deviation for a given list.
    # A faster algorithm exists in Knuth's "The Art of Programming", but this
    # will do.
    # Adapted from:
    # http://www.physics.rutgers.edu/~masud/computing/WPark_recipes_in_python.html
    from math import sqrt
    data = [i for i in data if type(i) != str]
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

def mode(data):

    # Generate a table of sorted (value, frequency) pairs.
    table = _counts(data)
    if len(table) == 1:
        return table[0][0]
    elif table:
        raise StatisticsError(
                'no unique mode; found %d equally common values' % len(table)
                )
    else:
        raise StatisticsError('no mode for empty data')
    
def median(data):
    data = sorted(data)
    if len(data) % 2 == 0:
        n = len(data)//2
        return (data[n]+data[n-1])/2
    else:
        return data[len(data)//2]

def se(data):
    from math import sqrt
    mean, std = meanAndDeviation(data)
    se = std / sqrt(len(data))
    return se

def runGraphs(time, yValues):
######## Not in use ####################
    x = input("Graphs? (yes or no):")
    if x == "yes":
        try:
            print("b")
            import numpy as np
            import pylab as pl
            for x in range(len(yValues)):
                pl.plot(time,yValues[x])
                pl.show()
        except:
            print('Must have numpy and matplotlib installed')



                            # -------------
                            # Main Function
                            # -------------

def runNoah():

    try:
        printBanner()
        commandMenu()
    except Exception as inst:
        print("-------------")
        input(inst)








#################################################################
###############  AUTOCAFE FUNCTIONS BEGINS HERE #################
#################################################################



import os
import copy

   
def getDeltas(inputData,pixPerCM):
    # This function takes a list of lists and returns a new matrix
    # made up of all the delta values for each capillary. These are
    # absolute values between each frame.

    allDeltas = []
    for capillary in inputData:

        deltas = []

        for x in range(1, len(capillary)):
            deltas.append(capillary[x] - capillary[x - 1])
        allDeltas.append(deltas)

    ulConversion       = getUnitConversion(pixPerCM)
    return allDeltas, ulConversion

def noiseStats(capillaryDeltas,fly):
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
        # problems can occur here if program thinks all deltas are meals, fixed with catch where original noise set is used
        try:
            mean, deviation = meanAndDeviation(noiseData)
            
            newNoiseData = []
            
            for i in range(0, len(noiseData)):
                if deviation * MEALPULL_SD > noiseData[i]:
                    newNoiseData.append(noiseData[i])

            currSize  = len(newNoiseData)
            noiseData = newNoiseData

        except:
            print("Alert: there may be an issue with data from capillary " + str(fly+1))
            noiseData = copy.deepcopy(capillaryDeltas)
            mean, deviation = meanAndDeviation(noiseData)
            currSize  = oldSize

    return meanAndDeviation(noiseData)
    
def getMealData(deltaMatrix,ulConversion,ORIGINAL_VOL):
    # Given the delta matrix, return a dictionary containing capillary
    # meals. This will be manipulated by users to determine the final
    # meal matrix.
   
    mealData  = {}
    
    ORIGINAL_VOL = ORIGINAL_VOL * ulConversion
    
    for i in range(0, len(deltaMatrix)):
        capillary   = deltaMatrix[i]
        noiseMean, noiseDeviation = noiseStats(capillary,i)
        meals   = dict()

        # Remove average evaporation/noise from each delta.
        for j in range(0, len(capillary)):
            capillary[j] = (capillary[j] - noiseMean)

        # The region below is to adjust meals for nutrient concentration shift from evaporation
        # Note: Adjustment Factor is currently not in use

        priorMeals = []     
        for j in range(0, len(capillary)):
            if capillary[j]  > (noiseDeviation * FINAL_SD):
                meals[j + 1] = capillary[j]

        mealData[i] = meals

 
    return mealData
   
          

def printData(data):
    # Simple pretty printing of the data. This serves as more of a
    # debugging functionality than anything else. Will be removed
    # in the final version.
    pp = pprint.PrettyPrinter()
    pp.pprint(data)

                            # --------------------
                            # User Input Functions
                            # --------------------



def outputToExcel(mealData,
                  ulConversion,
                  frameOffset,
                  intervalConversion,
                  feedFileName):
    # Used to output the contents of the meals, applying the conversions
    # to the meal data

    print()
    print("-------------- Excel Output --------------");
    print()
    print("NOTE: Existing files will be overwritten...")
    print()


    collatedName = feedFileName
    directory    = os.getcwd()
    collatedName = directory + "/" + collatedName + ".csv"


    preparedData, mealTimes, mealValues, mealDurations = prepareDataMatrix(mealData,
                                                         ulConversion,
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



    except Exception as e:
        print(e)

def prepareDataMatrix(mealData, ulConversion, frameOffset, intervalOffset):
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

    preparedData  = []
    mealTimes     = []
    mealValues    = []
    mealDurations = []

    for i in range(0, len(capillaryIds)):

        mealTimesVector      = []
        mealValuesVector     = []
        mealDurationsVector  = []
        
        capillaryMeals    = mealData[capillaryIds[i]]
        sortedMeals       = []
        
        for meal in capillaryMeals:
            sortedMeals.append(meal)

        sortedMeals.sort()
        preparedMeals = []

        for j in range(0, len(sortedMeals)):
            if j == len(sortedMeals):
                break
            frameNumber  = sortedMeals[j]
            meal         = capillaryMeals[frameNumber]
            mealDur      = 1   # denotes the length of a meal which is always 1 frame before rolling meals
            
            # Roll meals that are in adjacent frames into a single meal.
            combineOffset = 1
            
            while j + 1 < len(sortedMeals):
                if sortedMeals[j] + combineOffset == sortedMeals[ j + 1]:
                    mealDur = mealDur + 1
                    combineOffset = combineOffset + 1
                    meal          = meal + capillaryMeals[ sortedMeals[j+1] ]
                    sortedMeals.pop(j+1)
                else:
                    break

            mealTimesVector.append(frameOffset + (frameNumber - 0.5) * intervalOffset)
            mealValuesVector.append(meal / ulConversion)
            mealDurationsVector.append(mealDur * intervalOffset)

            # frameNumber is offset by -1 to compensate for 1 indexed dict format and -.5 for centering within imageing time window 
            preparedMeals.append(
                {"frame" : "{0:5.5f}".format(frameOffset + (frameNumber - 0.5) * intervalOffset),
                 "meal"  : "{0:5.5f}".format(meal / ulConversion),
                 "duration"  : "{0:5.5f}".format(mealDur * intervalOffset) })
            
        
        while len(preparedMeals) < maxLength:
            preparedMeals.append({"frame": "", "meal": "", "duration": ""})

        mealTimes.append(mealTimesVector)
        mealValues.append(mealValuesVector)
        mealDurations.append(mealDurationsVector)
         
        preparedData.append(preparedMeals) 
        
    return preparedData, mealTimes, mealValues, mealDurations
         
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
                preparedData[j][i]["meal"],
                preparedData[j][i]["duration"]))


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
                preparedData[j][i]["meal"]))
        file.write("\n")

    file.write("\n")

    for i in range(0, length):
        for j in range(0, len(preparedData)):
            file.write("{0:s},".format(
                preparedData[j][i]["duration"]))
        file.write("\n")

    file.write("\n")

           
            
def getUnitConversion(pixPerCM):
    # User input is used to determine the pixels per centimeter in each image.
    # This value, as well as a predetermined cm/uL value are used to provide a
    # unit conversion number. This number is used when outputting data
    # to a file, converting each pixel 'delta' into a meal 'delta'.

    try:

        units_conversion = pixPerCM * CM_PER_UL

        return units_conversion

    except Exception as e:
        print(e)



                            # -------------
                            # Main Function 
                            # -------------
def autoCafe(feedData,readsPerSec,pixPerCM,shortFileName):
    # This is the primary function. The highest level description of the logic
    # belongs here.
    
    try:
        feedFileName                                         = shortFileName+'_feeding'
        frameOffset                                          = zeitStart
        intervalConversion                                   = 1/(SECS_PER_MIN**2 / (feedFrame*readsPerSec)) 
        deltaMatrix, ulConversion                            = getDeltas(feedData,pixPerCM)
        mealData                                             = getMealData(deltaMatrix,ulConversion,ORIGINAL_VOL)                                 
        preparedData, mealTimes, mealValues, mealDurations   = prepareDataMatrix(mealData,ulConversion,frameOffset,intervalConversion)

        write = input('Write raw feeding(AutoCAFE) file to environment?(y/n) ')
        if write == 'y' or write == 'yes'or write == 'YES'or write == 'Yes':
            outputToExcel(mealData,ulConversion,frameOffset,intervalConversion,feedFileName)

        roll = input("Combine feeding bouts within given temporal distance?(y/n): ")

        if roll == 'y' or roll == 'yes' or roll == 'Yes' or roll == 'YES':
            mealValues,mealDurations,mealTimes = rollBouts(mealValues,mealDurations,mealTimes)

    except Exception as inst:
        print("-------------")
        input(inst)

    return mealTimes, mealValues, mealDurations, feedFileName 
                                      
                            # -----------
                            # Entry Point
                            # -----------

runNoah()

