#   Noah.py - A script analyze and structure Autocafe software output (created by Keith Murphy)
#			 as well as "Tracker" output(created by Robert Huber)
#
#   Copyright (C) 2017 Keith Murphy, Scarlet Park, & James Quinn
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
global pixPerCM
global readsPerSec
global bodyLenThresh
global feedFrame
global CM_PER_UL
global MEALPULL_SD
global FINAL_SD

bodyLenThresh = 0.5  # bodyLenThresh:This is the fraction of total body length a fly
numEntries = 3  # must move to be accounted for as motion data. adapted from Donelson et al.
cmPerFly = 0.3  # NOTE: Increasing this number decreases sensitivity and vice-versa
feedFrame = 30  # feedFrame is the window size in secs for grabbing the mean position of a dye-band (reduces noise)
# numEntries is number of elements / read / fly
# Typically depending on your version of JavaGrinders
# this is either 3 or 6
# gap is the number of items before 1st x coordinate, this number
# is usually 1 to skip the initial time mark


# ---------
# AutoCAFE Constants
# ---------

SIMPLE_DEVIATION = 2.0  # The naive standard deviation meal model
CM_PER_UL = 1.0075      # Calculated value for cm/uL
HOURS_PER_DAY = 24      # Number of hours in a day
MINUTES_PER_HOUR = 60   # Number of minutes per hour
SECS_PER_MIN = 60       # Number of seconds per minute
DEFAULT_FRAME = 0       # A default frame offset for Zeitgeiber times
DEFAULT_INTERVAL = 1    # A default frame interval for Zeitgeiber times
MEALPULL_SD = 4         # The meal pull sd for recalculating noise sd's
FINAL_SD = 5            # Final SD threshold for pulling meals
ORIGINAL_VOL = 5        # Original Volume of liquid food in capillary

#   -------------------
#		Noah Script
#   -------------------

# Code for taking Drosophila "Tracker" program data and genrating distance
# traveled values for all the individual flies. Also maintains a binning
# function for quick compilation of data as well as a noise removal fuction


import os
import time
import re
from math import atan2

global directory
global flyCount
global flyLength
global zeitStart
global scarletFilter

scarletFilter = True

# from numpy import transpose

pixPerCM = 76
readsPerSec=1


def printBanner():
	# This function is used to print the name and description
	# of this script. Returns the name of the input file to
	# be processed.
	print("			-------------------\n"
		  "				 Noah 15.4\n"
		  "			-------------------\n"
		  "   Noah.py - A script to analyzes data from the ARC\n"
		  "   containing animal and food tracking from \n"
		  "   ARCController.java program for a full suite\n"
		  "   of behavioral analysis\n"
		  "	 \n"
		  "				 \n"
		  "   Copyright (C) 2017 Keith Murphy and Jin Hong Park \n"
		  "\n"
		  " Input files must be tracker output file(.txt) and autocafe output(.csv/.txt)\n"
		  " Requires python 3.3, found in download section of pythons homepage.\n"
		  " Constant for movement detection threshold in regards to fly body length \n"
		  " is " + str(
		bodyLenThresh * 100) + "% and can be changed within the script under the constants section \n\n\n"

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
							   "\n")


def commandMenu():
	# This is the command menu list which allows the user to direct the
	# program to specified function

	while True:

		print("\t  ----- Noah Menu ----- ")
		print()
		print("\t 1.  Select ARC Data File")
		print("\t 2.  Analyze/Synthesize Data")
		print("\t 3.  Bin Activity Data")
		print("\t 4.  Bin Feeding Data")
		print("\t 5.  Bin Sleep Data")
		print("\t 6.  Generate Heat Map Matrix")
		print("\t 7.  Peri-prandial Behavior")
		print("\t 8.  Target Zone Count")
		print("\t 9.  Generate Kymograph")
		print("\t 10. Collective Behavior")
		print("\t 11. Export XY coordinates")
		print("\t 12. Use Virtual beam")
		print("\t 13. Arousal threshold")
		print("\t 14. Individual Sleep Events")
		print("\t 15. Groom Data")
		print("\t 16. Activity and sleep relative to individual meals")
		print("\t 17. Walk Length")
		print("\t 18. Angular Velocity")
		print("\t 19. Change constants")
		print("\t 20. Select AutoCAFE data file")
		print("\t 21. XY coordinates surrounding feeding events")
		print("\t 22. List of meals by fly")

		print("\n\t 0.  Exit Program")
		print("")

		# print("\t 15. Bout Length / Freq array")
		# print("\t 16. Grooming integration")

		try:

			option = int(input("\nEnter Command Number: "))

			if option == 0:
				return

			elif option == 1:
				activity, angularVelocity, readsPerSec, workList, shortFileName, X, Y, zeitStart, stim, feedData, pixPerCM, exptLengthHr, inactivity, sleep, mealTimes, mealValues, mealDurations, boutCountList, mealEndTimes=openData()


			elif option == 2:
				try:  # This is just in case there is no meal data associated with data, if mealTimes reference returns an error it just makes mealtimes and mealvals empty lists
					blank = mealTimes[0]
				except:
					mealTimes = []
					mealValues = []
					mealDurations = []
					blank = [0]
					for x in range(len(sleep)):
						mealTimes.append(blank)
						mealValues.append(blank)
						mealDurations.append(blank)
					print("Alert! No feeding data loaded for synthesis")
				try:
					blank = sleep[0]
				except:
					sleep = []
					activity = []
					workList = []
					blank = [0]
					readsPerSec = 1
					for x in range(len(mealTimes)):
						sleep.append(blank)
						activity.append(blank)
						workList.append(blank)
					print("Alert! No Activity data loaded for synthesis")
				
				useFileName = shortFileName

				synth(sleep, activity, mealTimes, mealValues, mealDurations, readsPerSec, workList, useFileName, exptLengthHr)


			elif option == 3:
				actBin(activity, readsPerSec, shortFileName)

			elif option == 4:
				try:
					mealBins, timeBins, header = feedBins(mealTimes, mealValues, mealDurations, shortFileName)
				except:
					print("Alert! Feeding data may not be loaded.")

			elif option == 5:
				sleepBin(sleep, readsPerSec, shortFileName)

			elif option == 6:

				heatMap(workList, readsPerSec, activity, X, Y, mealValues, mealDurations, mealTimes)

			elif option == 7:
				# can add any feature surrounding feeding events, so long as it is structured the same as sleep / activity
				featureChoice = input("Sleep, activity, or inactivity surrounding feeding events (s/a/i):")
				if featureChoice == "a":
					feature = activity
					featureTitle = "activity"
				elif featureChoice == "i":
					feature = inactivity
					featureTitle = "inactivity"
				elif featureChoice == "s":
					feature = sleep
					featureTitle = "sleep"

				else:
					feature = None
					featureTitle = "None"

				feedLocal(mealValues, mealDurations, mealTimes, feature, featureTitle, readsPerSec, shortFileName)

			elif option == 8:
				hotZone(workList, readsPerSec, numEntries, shortFileName)

			elif option == 9:
				kymograph(workList, readsPerSec, shortFileName, X, Y)

			elif option == 10:
				collective(X, Y, activity, readsPerSec, shortFileName)

			elif option == 11:
				exportX = transpose(X)
				exportY = transpose(Y)
				toExcelNamed(exportX, "X_coordinates" + str(shortFileName))
				toExcelNamed(exportY, "Y_coordinates" + str(shortFileName))

			elif option == 12:
				activity, sleep = virtualBeam(X, Y, readsPerSec)

			elif option == 13:
				try:
					check = mealTimes[0][0]
				except:
					check = 1
				if check != 1:
					arouse = arousal(stim, activity, inactivity, readsPerSec, shortFileName, mealTimes, mealValues)
				else:
					arouse = arousal(stim, activity, inactivity, readsPerSec, shortFileName)


			elif option == 14:
				try:
					sleepFreqLengthArray(sleep, shortFileName)

				except:
					print("can't compute individual sleep events")

			elif option == 15:
				file = getInput()
				groomData = getFileVectors(file)
				groom, sleep, groomErr = groomGen(groomData, activity, inactivity, sleep, readsPerSec)


			elif option == 16:
				mealRelation(mealTimes, mealValues, mealDurations, shortFileName, activity, sleep, readsPerSec)

			elif option == 17:
				walkLength(activity, X, Y)

			elif option == 18:
				angBin(angularVelocity, readsPerSec, shortFileName)

			elif option == 19:
				changeConstants()

			elif option == 20:
				file = getInput()
				readsPerSec = 1 / 60
				mealTimes, mealValues, mealDurations, boutPerMeal, mealEnds = parseMealData(file)

			elif option == 21:
				feedKymo(mealValues, mealDurations, mealTimes, X, Y, readsPerSec, shortFileName)

			elif option == 22:
				combineAutoCAFEMeals(mealTimes, mealValues, mealDurations, shortFileName)


		except Exception as e:
			print(e)

def openData():
	global pixPerCM
	file = getInput()
	activity, angularVelocity, readsPerSec, workList, shortFileName, X, Y, zeitStart, stim, feedData, pixPerCM, exptLengthHr = parseData(file)
	inactivity = getInactDuration(activity)
	sleep = getSleep(activity, readsPerSec)
	mealTimes, mealValues, mealDurations, boutCountList, mealEndTimes = autoCafe(feedData, readsPerSec, pixPerCM, shortFileName)
	#mealTimes, mealValues, mealDurations, boutCountList, mealEndTimes = parseMealData(file)
	#write = input('Write raw feeding(AutoCAFE) file to environment?(y/n) ')
	#	if write == 'y' or write == 'yes'or write == 'YES'or write == 'Yes':
	#		intervalConversion = 1 / (SECS_PER_MIN ** 2 / (feedFrame * readsPerSec))
	#		outputToExcel(mealData,ulConversion,zeitStart,intervalConversion,shortFileName)

	file.close()
	return activity, angularVelocity, readsPerSec, workList, shortFileName, X, Y, zeitStart, stim, feedData, pixPerCM, exptLengthHr, inactivity, sleep, mealTimes, mealValues, mealDurations, boutCountList, mealEndTimes


def changeConstants():
	global pixPerCM
	global bodyLenThresh
	global feedFrame
	global CM_PER_UL
	global MEALPULL_SD
	global FINAL_SD
	global scarletFilter

	while True:
		c = int(input("\n Which constant would you like to change? \n\n"
					  "\t\t\t\t\t\t   current value\n"
					  "\t 1. pixels per centimeter\t\t\t" + str(pixPerCM) + "\n"
																			"\t 2. body length threshold for movement\t\t" + str(
			bodyLenThresh) + "\n"
							 "\t 3. no. of frames to average for feeding\t" + str(feedFrame) + "\n"
																							   "\t 4. centimeters per microliter\t\t\t" + str(
			CM_PER_UL) + "\n"
						 "\t 5. meal pull standard deviation\t\t" + str(MEALPULL_SD) + "\n"
																					   "\t 6. final standard deviation\t\t\t" + str(
			FINAL_SD) + "\n"
						"\t 7. scarlet filter\t\t\t\t" + str(scarletFilter) + "\n\n"
																			  "\t 0. return to main menu\n\n"))
		if c == 1:
			pixPerCM = int(input("Enter new pixPerCM: "))
		elif c == 2:
			bodyLenThresh = float(input("Enter new body length threshold: "))
		elif c == 3:
			feedFrame = int(input("Enter new feedFrame: "))
		elif c == 4:
			CM_PER_UL = float(input("Enter new CM_PER_UL: "))
		elif c == 5:
			MEALPULL_SD = float(input("Enter new MEALPULL_SD: "))
		elif c == 6:
			FINAL_SD = float(input("Enter new FINAL_SD: "))
		elif c == 7:
			if input("Turn Scarlet filter on? (y/n)") == "y":
				scarletFilter = True
			else:
				scarletFilter = False
		elif c == 0:
			break
		else:
			print("input error.")


def getInput():
	# This function asks the user for an input file. Once it's
	# opened, the data is parsed into a two-dimensional matrix.
	# Data is returned from the function once parsed successfully.
	global directory
	global zeitStart

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
	global readsPerSec

	workList, exptLengthHr = getFileVectors(file)
	print("length of experiment: " + str(exptLengthHr) + " hours")
	timeStamp = workList.pop(0)
	stim = []

	# if empty reads are given by javagrinders delete the column
	workList = [vector for vector in workList if vector[0] != ""]

	if len(workList) % 3 != 0:  # checks for an additional stim line
		print("Data file contains stimulus information...")
		stim = workList.pop(-1)

	flyCount = len(workList) / numEntries
	print("Dataset contains", flyCount, "flies.")
	try:
		pixPerCM == 1
		print("px/cm set to ",pixPerCM)
	except:
		pixPerCM = int(input("Enter pixels / centimeter: "))
	flyLength = pixPerCM * cmPerFly
	try:
		readsPerSec==1
		print("reads/sec set to ",readsPerSec)
	except:
		readsPerSec = float(input("How many readings per second are there in your data: "))
	zeitStart = getZeitStart()
	print("Body length threshold set at ", bodyLenThresh)

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
			while workList[vector][i * -1] == -1:
				i = i + 1
			workList[vector][-1] = workList[vector][i * -1]
		except:
			break

	div = int(len(workList) / 3)
	foodTrack = workList[:div]
	animalTrack = workList[div:]

	print("Cleaning missed animal tracking data...")
	print("")

	# This statement checks for -1's and replaces them with the last good read
	missedAnimal = []
	for fly in range(len(animalTrack)):
		prog = fly / len(animalTrack)
		update_progress(prog)
		miss = 0
		for read in range(1, len(animalTrack[fly])):
			if animalTrack[fly][read] == -1:
				animalTrack[fly][read] = animalTrack[fly][read - 1]
				miss = miss + 1
		if fly % 2 == 0:
			missedAnimal.append((miss / len(animalTrack[fly])) * 100)

	print("")
	print("Data cleaned.")
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

					shift = ((foodTrack[capillary][read + gap] - foodTrack[capillary][read - 1]) / (gap + 1))
					for i in range(0, gap):
						foodTrack[capillary][read + i] = foodTrack[capillary][read - 1] + shift * i
					read = read + gap
				except:
					read = read + gap

			else:
				read = read + 1
		missedFeed.append((miss / len(foodTrack[capillary])) * 100)

	print("")
	print("Data cleaned.")
	print("Processing food tracking data.")

	feedFrameS = int(readsPerSec * feedFrame)  # feed frame converted to seconds
	feedData = []
	for vector in range(len(foodTrack)):
		prog = vector / len(foodTrack)
		update_progress(prog)
		dataVector = []
		for read in range(0, len(foodTrack[vector]), feedFrameS):
			tempList = foodTrack[vector][read:read + feedFrameS]
			try:
				modeT = mode(tempList)  # get mode of population to clear any far outliers

				for i in range(len(tempList)):
					if tempList[i] - abs(modeT) > pixPerCM * 0.3:
						tempList[i] = modeT

			except:
				pass

			dataVector.append(avg(tempList))

		# Custom noise smoothing algorithm using a variation of moving average.
		# Takes advantage of the fact that the meniscus only moves in one direction,
		# and iterates through exponentially decreasing filter widths.
		# Contributed by Jin Hong Park
		if scarletFilter:
			intervalList=[]
			for i in range (4):
				intervalList.append(int(int(feedFrame)/(i+1)))
				intervalList.append(int(int(feedFrame)/(i+1)))

			for interval in intervalList:  # -----1---- Comment out these 5 lines
				fwidth = pow(2, interval)  # -----2---- to remove the noise filter
				for j in range(fwidth, len(dataVector) - fwidth):  # -----3----
					if dataVector[j] < dataVector[j - fwidth] or dataVector[j] > dataVector[j + fwidth]:  # -----4----
						dataVector[j] = (dataVector[j - fwidth] + dataVector[j + fwidth]) / 2  # -----5----
		feedData.append(dataVector)

	shortFileName = cutFileName(file)
	toExcelNamed(transpose(feedData), "cleanedFeedTrack_" + shortFileName)

	print("")
	print("Done processing.")

	X, Y = getCoordinates(
		animalTrack)  # gets x,y coordinates and optionally applies a sorting procedure for identity switching

	print("")
	print("Calculating distal values...")
	print("")
	activity = []
	for fly in range(len(X)):
		prog = fly / len(X)
		update_progress(prog)
		indivDist = []

		for read in range(len(X[fly])):
			x1 = X[fly][read - 1]
			y1 = Y[fly][read - 1]
			x2 = X[fly][read]
			y2 = Y[fly][read]
			try:
				singleDistance = distance(x1, y1, x2,
										  y2)  # Distance function found above calculates simple Euclidean Distance
			except:
				singleDistance = 0
			if singleDistance < (bodyLenThresh * flyLength) / readsPerSec:  # -----1---- Comment out these 5 lines
				if read > 0:  # -----2---- to remove the noise filter
					singleDistance = 0  # -----3----
					X[fly][read] = X[fly][read - 1]  # -----4----
					Y[fly][read] = Y[fly][read - 1]  # -----5----

			indivDist.append(singleDistance / pixPerCM)

		activity.append(indivDist)

	print("")
	print("Distal value calculation complete.")
	print("Calculating angular velocity...")
	print("")

	angularVelocity = []
	for fly in range(len(X)):
		prog = fly / len(X)
		update_progress(prog)
		indAV = []
		for read in range(len(X[fly])):
			try:
				indAV.append(abs(getAngularVelocity(X[fly][read - 1:read + 2], Y[fly][read - 1:read + 2])))
			except:
				indAV.append(0)
		angularVelocity.append(indAV)

	shortFileName = cutFileName(file)

	return (activity, angularVelocity, readsPerSec, workList, shortFileName, X, Y, zeitStart, stim, feedData, pixPerCM,
			exptLengthHr)


def getAngularVelocity(x, y):
	# takes Xi-1 through Xi+1 and same for Y for input
	av = atan2(x[2] - x[1], y[2] - y[1]) - atan2(x[1] - x[0], y[1] - y[0])
	return av


def parseMealData(file):

    # This function splits the lines of the import file named
    # file by tabs. It then generates a list of lists of all the flies
    # meal times and all of their meal sizes which are the outputs

    file.seek(0)
    print("Parsing file contents....")
    mealList    = []
    zTimes      = []
    meals       = []
    durations   = []
    mealEndTimes = []
    indivZTimes = []
    indivMeals  = []
    indivDurs   = []
    indivMealEndTimes = []
    indivBoutCount = []
    boutCountList  = []
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
                    indivBoutCount.append(1)
                    indivMealEndTimes.append(float(mealList[i][f + skip])+float(float((mealList[i][f + skip + 2]))/3600))
                except:
                    pass

            zTimes.append(indivZTimes)
            meals.append(indivMeals)
            durations.append(indivDurs)
            boutCountList.append(indivBoutCount)
            mealEndTimes.append(indivMealEndTimes)

            indivMeals  = []
            indivZTimes = []
            indivDurs   = []
            indivBoutCount = []
            indivMealEndTimes = []
            skip = skip + (itemsPerFly - 1)

        for a in range(len(zTimes)):
            for b in range(len(zTimes[a])):
                zTimes[a][b] = float(zTimes[a][b])
                meals[a][b]  = float(meals[a][b])
                durations[a][b]  = float(durations[a][b])
                boutCountList[a][b] = int(boutCountList[a][b])
                mealEndTimes[a][b] = float(mealEndTimes[a][b])


    except:
        errorMsg = "Error: Check File Structure. Look for gaps in data."
        raise Exception(errorMsg)

    return zTimes, meals,durations, boutCountList,mealEndTimes


def getSleep(activity, readsPerSec):
	# This function takes the distance list and then creates a binary
	# sleep list for each fly. The algorithm considers an animal asleep
	# during any period of immobility > sleepLength which is defined in
	# the constants section above

	sleepLength = int(readsPerSec * 300)
	sleepGroup = []

	print("Compiling Sleep Binary...")
	print("")
	for fly in range(len(activity)):
		prog = fly / len(activity)
		update_progress(prog)
		sleepIndiv = []
		for reading in range(len(activity[fly])):
			if activity[fly][reading] == 0:
				try:
					sumAct = sum(activity[fly][reading:reading + sleepLength])
					if sumAct == 0 or sleepIndiv[-1] == 1:
						sleepIndiv.append(1)
					else:
						sleepIndiv.append(0)
				except:
					sleepIndiv.append(
						0)  # This exception is run when there are no elements in sleepIndiv[-1] or first frame
			else:  # it assumes an animal is awake when there is no prior knowledge of its state and it is inactive
				sleepIndiv.append(0)
		sleepGroup.append(sleepIndiv)
	sleep = sleepGroup
	print("")
	print("")
	print("Sleep Binary Compiled.")
	print("n = ", len(activity))
	return (sleep)


def mealTimesToZS(mealTimes):
	# converts mealTimes to zeitgeber seconds

	mealTimesZS = []
	for i in range(len(mealTimes)):
		indieMeals = []
		for n in range(len(mealTimes[i])):
			indieMeals.append(round((mealTimes[i][n] * 60 * 60), 0))
		mealTimesZS.append(indieMeals)

	return (mealTimesZS)


def feedLocal(mealValues, mealDurations, mealTimes, feature, featureTitle, readsPerSec, shortFileName):
	# This function provides the sleep or activity immediately surrounding
	# feeding events. It includes a filter for meal size and a sorting function
	# where regularly ordered groups (i.e. 1,2,3,1,2,3..) can be sorted
	# current output returns meal volume, meal duration, time of meal,
	# time since last meal, and then the requested time series surrounding
	# a meal

	print("Assumes ZT 0 is start of lights on. ")
	print("Make sure that motion data matches your feeding dataset length")

	zeitStart = getZeitStart()
	timeIndex = framesToSecs(readsPerSec, zeitStart, feature)
	mealTimesZS = mealTimesToZS(mealTimes)

	# time(sec's) from feeding event that sleep binary is appended
	timePush = int(input("Enter absolute time(sec) surrounding feeding events: "))
	step = input("Enter step interval (sec) surrounding feeding events: ")
	try:
		step = int(step)
		if step < 1:
			err
	except:
		step = 1
		print("step default = 1")

	runAbs = input("Compare time points by absolute distance(y/n): ")
	if runAbs == "y" or runAbs == "yes" or runAbs == "Y":
		runAbs = 1

	absList = []
	finalList = []
	for fly in range(len(mealTimesZS)):
		for meal in range(len(mealTimesZS[fly])):
			try:
				current = timeIndex.index(mealTimesZS[fly][meal])
				featureBinary = []
				for n in range(-timePush, timePush, step):
					if not feature == None:
						try:
							featureBinary.append(avg(feature[fly][current + n:current + n + step]))
						except:
							featureBinary.append("")
					else:
						featureBinary.insert(-1, "")

				if runAbs == 1:

					setPre = int(len(featureBinary) / 2) - 1  # +1 because abslist has fly number embedded at position 0
					setPost = int(len(featureBinary) / 2)
					mealComp = []
					for time in range(int(len(featureBinary) / 2)):
						try:
							mealComp.append(featureBinary[setPost + time] - featureBinary[setPre - time])
						except:
							mealComp.append("")

				if meal != 0:
					featureBinary.insert(0, mealTimes[fly][meal] - mealTimes[fly][meal - 1])
				else:
					featureBinary.insert(0, "")
				##					if meal != len(mealTimes[fly])-1:
				##						featureBinary.insert(0,mealTimes[fly][meal+1] - mealTimes[fly][meal])
				##					else:
				##						featureBinary.insert(0,"")
				featureBinary.insert(0, mealTimes[fly][meal])
				featureBinary.insert(0, mealValues[fly][meal])
				featureBinary.insert(0, mealDurations[fly][meal])
				featureBinary.insert(0, fly + 1)
				finalList.append(featureBinary)

				if runAbs == 1:
					##						if meal != len(mealTimes[fly])-1:
					##							featureBinary.insert(0,mealTimes[fly][meal+1] - mealTimes[fly][meal])
					##						else:
					##							featureBinary.insert(0,"")
					if meal != 0:
						mealComp.insert(0, mealTimes[fly][meal] - mealTimes[fly][meal - 1])
					else:
						mealComp.insert(0, "")

					mealComp.insert(0, mealTimes[fly][meal])
					mealComp.insert(0, mealValues[fly][meal])
					mealComp.insert(0, mealDurations[fly][meal])
					mealComp.insert(0, fly)
					absList.append(mealComp)

			except:
				pass

	sort = input("Sort at regular interval(y/n): ")
	if sort == "y":
		sort = int(input("Enter sort interval: "))
		avgList = []
		absAvgList = []
		seList = []
		absSeList = []
		for i in range(sort):
			outputList = []
			absOutputList = []
			x = i
			while x <= len(mealTimesZS):
				try:
					for h in range(len(finalList)):
						if finalList[h][0] == x:
							outputList.append(finalList[h])
							if runAbs == 1:
								absOutputList.append(absList[h])
				except:
					pass
				x = x + sort

			try:
				outputList = transpose(outputList)
				if runAbs == 1:
					absOutputList = transpose(absOutputList)
			except:
				pass

			name = "Group " + str(i + 1)
			absName = name + "_abs"
			toExcelNamed(outputList, name)
			if runAbs == 1:
				toExcelNamed(absOutputList, absName)

			# section for taking averages of all time points for group
			indieAvg = []
			indieSE = []
			for i in range(len(outputList)):
				try:
					indieAvg.append(avg(outputList[i]))
				except:
					indieAvg.append("")
				try:
					indieSE.append(se(outputList[i]))
				except:
					indieSE.append("")

			if runAbs == 1:

				indieAbsAvg = []
				indieAbsSE = []
				for i in range(len(absOutputList)):
					try:
						indieAbsAvg.append(avg(absOutputList[i]))
					except:
						indieAbsAvg.append("")
					try:
						indieAbsSE.append(se(absOutputList[i]))
					except:
						indieAbsSE.append("")

			avgList.append(indieAvg)
			seList.append(indieSE)
			if runAbs == 1:
				absAvgList.append(indieAbsAvg)
				absSeList.append(indieAbsSE)

		finList = avgList + seList
		finList = transpose(finList)
		finList.pop(0)
		finList.pop(0)
		finList.pop(0)
		finList.pop(0)
		finList.pop(0)

		name = "avg,se"
		toExcelNamed(finList, name + "_" + shortFileName)

		if runAbs == 1:
			absFinList = absAvgList + absSeList
			absFinList = transpose(absFinList)
			absFinList.pop(0)
			absFinList.pop(0)
			absFinList.pop(0)
			absFinList.pop(0)
			absFinList.pop(0)

			absName = "abs_avg,se"
			toExcelNamed(absFinList, absName + "_" + shortFileName)


	else:
		finalList = [["fly#", "meal duration(s)", "meal size(ul)", "meal time", "time since last meal(h)",
					  "P(sleep) pre", "P(sleep) post"]] + finalList
		toExcelNamed(finalList,
					 "prandial" + featureTitle + "_" + str(timePush) + "swindow_" + str(step) + "sbin_" + shortFileName)
		absList = transpose(absList)
		toExcelNamed(absList, "prandial" + featureTitle + "_" + str(timePush) + "swindow_" + str(
			step) + "sbin_" + shortFileName + "_abs")


def feedKymo(mealValues, mealDurations, mealTimes, X, Y, readsPerSec, shortFileName):
	# XY coordinates surrounding feeding events

	zeitStart = getZeitStart()
	timeIndex = framesToSecs(readsPerSec, zeitStart, X)
	mealTimesZS = mealTimesToZS(mealTimes)

	timePush = int(input("Enter absolute time(sec) surrounding feeding events: "))
	step = input("Enter step interval (sec) surrounding feeding events: ")

	try:
		step = int(step)
		if step < 1:
			err
	except:
		step = 1
		print("step default = 1")

	finalList = []
	for fly in range(len(mealTimesZS)):
		for meal in range(len(mealTimesZS[fly])):
			try:
				current = timeIndex.index(mealTimesZS[fly][meal])
				xList = []
				yList = []
				for n in range(-timePush, timePush, step):
					try:
						xList.append(avg(X[fly][current + n:current + n + step]))
						yList.append(avg(Y[fly][current + n:current + n + step]))
					except:
						xList.append("")
						yList.append("")

				xList.insert(0, "X")
				xList.insert(0, mealTimes[fly][meal])
				xList.insert(0, mealValues[fly][meal])
				xList.insert(0, mealDurations[fly][meal])
				xList.insert(0, meal + 1)
				xList.insert(0, fly + 1)
				finalList.append(xList)

				yList.insert(0, "Y")
				yList.insert(0, mealTimes[fly][meal])
				yList.insert(0, mealValues[fly][meal])
				yList.insert(0, mealDurations[fly][meal])
				yList.insert(0, meal + 1)
				yList.insert(0, fly + 1)
				finalList.append(yList)

			except:
				pass

	else:
		header = ["fly#", "meal number", "meal duration(s)", "meal size(ul)", "meal time"]
		for i in range(-timePush, timePush, step):
			header.append(str(i))
		finalList.insert(0, header)
		toExcelNamed(finalList,
					 "XY surrounding meal_" + str(timePush) + "swindow_" + str(step) + "sbin_" + shortFileName)


def getInactDuration(activity):
	# This function scans the activity data matrix and creates a matrix of arrays of time inactive
	# at all time points for each fly. This means if at time point x a fly has been inactive since
	# time point x - 15, the value at x for inactDur will be 15

	print("Generating inactivity data...")
	print("")
	inactDur = []
	for fly in range(len(activity)):
		prog = fly / len(activity)
		update_progress(prog)
		inactDurInd = []
		i = 0
		for read in range(len(activity[fly])):
			if activity[fly][read] == 0:
				i = i + 1
			else:
				i = 0
			inactDurInd.append(i)
		inactDur.append(inactDurInd)
	print("")
	print("Generating inactivity data complete.")

	return (inactDur)


def arousal(stim, activity, inactivity, readsPerSec, shortFileName, mealTimes=0, mealValues=0):
	# requires a column vector tab delimited file of stim's applied matched to
	# tracking file for instance [0 0 0 0 .5 0 0 1 0 0] would mean
	# that at the 5th time point in a tracking file, a stimulus of .5 was applied and
	# at time point 8, a stimulus of 1 was applied. This function then
	# generates a vector for each fly listing the stims they respond
	# to. For instance if a fly responded to the 1 value stim shown above the vector
	# would appear as [0 0 0 0 0 0 0 1 0 0]. Method and parameters
	# based on work of Faville et al. 2015

	iDur = inactivity
	try:
		inactMin = int(
			input("Enter minimum time(seconds) a fly can be inactive to be considered for stimulus response: "))
	except:
		print('Default: minimum time set to 1 second')
		inactMin = 1
	try:
		inactMax = int(
			input("Enter maximum time(seconds) a fly can be inactive to be considered for stimulus response: "))
	except:
		print('Default: no max time set')
		inactMax = 10000000000000

	inactMin = int(inactMin * readsPerSec)
	inactMax = int(inactMax * readsPerSec)
	timeToRespond = int(
		input("Enter seconds within which an animal must move to be considered aroused by a given stimulus: "))
	timeToRespond = int(timeToRespond * readsPerSec)
	maxStim = 3.2  # ceiling stimulus an animal is given
	maxAssignment = 3.8  # stim response an animal is assigned if they don't respond to maxStim

	if len(stim) == 0:  # check if stim file is empty
		print("Requires single column stimulation file...")
		stimFile = getInput()
		stimFile.seek(0)
		stim = []
		for line in stimFile:
			stim.append(float(line))

	arouse = []
	zeitStart = getZeitStart()
	timeIndex = framesToSecs(readsPerSec, zeitStart, activity)  # use timeIndex for meal relative arousal

	# generates a vector for each fly of arousal events indicated by the value of arousal or "" for no arousal
	for fly in range(len(activity)):
		arousalInd = []
		for i in range(len(stim)):
			if stim[i] != 0:
				if iDur[fly][i] >= inactMin and iDur[fly][i] <= inactMax and i > inactMin:
					if sum(activity[fly][i:i + timeToRespond]) > 0 and sum(arousalInd[-timeToRespond:]) == 0:
						arousalInd.append(stim[i])
					elif stim[i] == maxStim and sum(arousalInd[-timeToRespond:]) == 0:
						arousalInd.append(maxAssignment)
					else:
						arousalInd.append(0)
				else:
					arousalInd.append(0)
			else:
				arousalInd.append(0)

		for r in range(len(arousalInd)):  # replace all 0's with "" for averaging purposes in next nection
			if arousalInd[r] == 0:
				arousalInd[r] = ""

		arouse.append(arousalInd)

	label = "arousal"
	meanBinGen(arouse, readsPerSec, shortFileName, label)

	if type(mealTimes) != int:
		# mealTimes converted to z-time seconds
		mealTimesZS = []
		for i in range(len(mealTimes)):
			indieMeals = []
			for n in range(len(mealTimes[i])):
				indieMeals.append(round((mealTimes[i][n] * 60 * 60), 0))
			mealTimesZS.append(indieMeals)

		# time(sec's) from feeding event that arousal is appended
		timePush = int(input("Enter absolute time(sec's) surrounding feeding events: "))
		timePush = int(timePush * readsPerSec)
		step = int(input("Enter step interval(sec's) surrounding feeding events: "))
		finalList = []
		for fly in range(len(mealTimes)):
			for meal in range(len(mealTimes[fly])):
				featureBinary = []
				try:
					current = timeIndex.index(mealTimesZS[fly][meal])
					for n in range(-timePush, timePush, step):
						try:
							featureBinary.append(avg(arouse[fly][current + n:current + n + step]))
						except:
							featureBinary.append("")
				except:
					featureBinary.append("")

				featureBinary.insert(0, mealTimes[fly][meal])
				featureBinary.insert(0, mealValues[fly][meal])
				featureBinary.insert(0, fly)
				finalList.append(featureBinary)

		finalList = transpose(finalList)
		toExcelNamed(finalList, shortFileName + "feeding_arousal")

	##	proximity = int(input("enter proximity in seconds: "))
	##	pre  = []
	##	post = []
	##	bet = []
	##	for fly in range(len(arouse)):
	##		for read in range(len(arouse[fly])):
	##			if arouse[fly][read] != "":
	##				wasSort = 0
	##				stimTime = timeIndex[read]
	##				for meal in range(len(mealTimesZS[fly])):
	##					if mealTimesZS[fly][meal] > stimTime and mealTimesZS[fly][meal] - stimTime < proximity:
	##						temp = []
	##						temp.append(stimTime)
	##						temp.append(mealValues[fly][meal])
	##						temp.append(arouse[fly][read])
	##						pre.append(temp)
	##						wasSort = 1
	##					if mealTimesZS[fly][meal] < stimTime and stimTime - mealTimesZS[fly][meal] < proximity:
	##						temp = []
	##						temp.append(stimTime)
	##						temp.append(mealValues[fly][meal])
	##						temp.append(arouse[fly][read])
	##						post.append(temp)
	##						wasSort = 1
	##				if wasSort == 0:
	##					temp = []
	##					temp.append(stimTime)
	##					temp.append("")
	##					temp.append(arouse[fly][read])
	##					bet.append(temp)
	##
	##	pre = transpose(pre)
	##	post = transpose(post)
	##	bet = transpose(bet)
	##	toExcelNamed(pre,'pre')
	##	toExcelNamed(post,'post')
	##	toExcelNamed(bet,'between')

	return (arouse)


def sleepFreqLength(sleep, readsPerSec):
	# returns avg sleep bout length and # of sleep bouts from a list of sleep binary
	boutLengths = []
	for x in range(1, len(sleep)):
		if sleep[x] == 1 and sleep[x - 1] == 0:
			n = 0
			try:
				while sleep[x + n] == 1:
					n = n + 1
				boutLengths.append(n / readsPerSec)
			except:
				pass

	try:
		freq = int(len(boutLengths))
		boutLength = avg(boutLengths)
	except:
		freq = 0
		boutLength = 0

	return (freq, boutLength)


def sleepFreqLengthArray(sleep, shortFileName):
	# uses a list of lists of sleep and creates a corresponding set where sleepLength has elements that denote
	# the length of a sleep bout initiated at any given point i. Sleep frequency is a binary in which a 1 denotes
	# a time point i at which a sleep bout is initiated
	zeitStart = getZeitStart()

	boutLengths = []
	boutTimes = []
	flyNums = []

	for fly in range(len(sleep)):
		indivLength = []
		indivZT = []
		read=1

		if len(sleep[fly])>0:
			try:
				while read < len(sleep[fly]):
					try:
						if sleep[fly][read-1]==0 and sleep[fly][read]==1:
							boutLen=1
							movingRead=read+1
							while sleep[fly][movingRead]==1:
								boutLen=boutLen+1
								movingRead=movingRead+1
							indivLength.append(boutLen)
							indivZT.append(float(read)/3600+zeitStart)
							read=movingRead+1
						else:
							read=read+1
					except:
						break
				boutLengths.append(indivLength)
				boutTimes.append(indivZT)
			except:
				pass
		else:
			pass

	flyNums=[]
	final=[["fly#","sleep time","sleep length (s)"]]
	for fly in range(len(boutLengths)):
		try:
			for count in range(len(boutLengths[fly])):
				final.append([fly+1,boutTimes[fly][count],boutLengths[fly][count]])
		except:
			pass

	toExcelNamed(final,"sleepEvents_"+shortFileName)


def rollBouts(mealValues, mealDurations, mealTimes, boutCounts, mealEndTimes):
	# Because there is no formal definition for what a meal is,
	# this function allows the user to roll together
	# meals within a user specified temporal distance

	rollDistance = float(input("Enter temporal distance between bouts for compression(s): "))
	rollDistance = rollDistance / 3600

	for fly in range(len(mealTimes)):
		for meal in range(len(mealTimes[fly])):
			try:
				if mealTimes[fly][meal + 1] - mealEndTimes[fly][meal] <= rollDistance:
					imi                          = mealTimes[fly][meal + 1] - mealEndTimes[fly][meal]
					mealValues[fly][meal + 1]    = mealValues[fly][meal] + mealValues[fly][meal + 1]
					# not just sum of all durations, but from the beginning to the end of a meal
					mealDurations[fly][meal + 1] = mealDurations[fly][meal] + imi + mealDurations[fly][meal + 1]
					# just sum of all meal durations
					# mealDurations[fly][meal + 1] = mealDurations[fly][meal] + imi + mealDurations[fly][meal + 1]
					boutCounts[fly][meal + 1]    = boutCounts[fly][meal] + 1
					mealValues[fly][meal]        = " "
					mealDurations[fly][meal]     = " "
					mealTimes[fly][meal]         = " "
					boutCounts[fly][meal]        = " "
					mealEndTimes[fly][meal]      = " "
			except:
				pass

	for fly in range(len(mealTimes)):
		mealTimes[fly]     = [meal for meal in mealTimes[fly] if meal != " "]
		mealValues[fly]    = [meal for meal in mealValues[fly] if meal != " "]
		mealDurations[fly] = [meal for meal in mealDurations[fly] if meal != " "]
		boutCounts[fly]    = [meal for meal in boutCounts[fly] if meal != " "]
		mealEndTimes[fly]  = [meal for meal in mealEndTimes[fly] if meal != " "]

	return (mealValues, mealDurations, mealTimes, boutCounts, mealEndTimes)



################################################
############ General Stats Generator ###########
################################################

def synth(sleep, activity, mealTimes, mealValues, mealDurations, readsPerSec, workList, useFileName, exptLengthHr):
	# This function runs a number of different procedures for capturing the basic behavior of a
	# fly. All outputs are initiated early on and listed at the end of function

	###################
	# ----CONSTANTS----#
	###################

	flies = len(sleep)
	reads = len(activity[0])
	print("Assumes ZT 0 is start of lights on. ")
	print("Make sure that this matches your feeding dataset length")
	zeitStart = getZeitStart()
	RI12 = int(43200 * (readsPerSec / 1))  # number of reads in 12 hrs
	RI24 = int(RI12 * 2)
	short, med, longS = sleepDepth(sleep, readsPerSec)

	# below is short code to convert mealTimes from hours into seconds for indexing purposes
	mealTimesZS = []  # mealTimes converted to z-time seconds
	for i in range(len(mealTimes)):
		indieMeals = []
		for n in range(len(mealTimes[i])):
			indieMeals.append(round((mealTimes[i][n] * 60 * 60), 0))
		mealTimesZS.append(indieMeals)

	timeIndex = framesToSecs(readsPerSec, zeitStart, activity)
	# check framesToSecs for details

	flyCount = ["Fly #"]  # Header with Fly # generator
	for x in range(len(sleep)):
		flyCount.append(x + 1)

	# check if # of flies in feeding data matches tracking data
	if len(mealValues) == flies:

		# The section below creates all the lists of paramters we'll look at, each having a title describing the data as the 0th element
		# Many of these measurements will not show up in the output unless indicated in statsList at the end of this function

		Activity = ["Activity - Distance Traveled (cm)"]
		Sleep = ["Sleep(hrs)"]
		Feed = ["Feeding (ul)"]
		FeedPerHr = ["Avg Feeding per Hour (ul/hr)"]
		avgMeal = ["Avg Meal Size "]
		numMeal = ["Meal frequency"]
		avgDuration = ["Meal Duration (s)"]
		totalFeedTime = ["Time Spent Eating (s)"]
		percentSleep = ["% of Time Sleeping"]
		avgSleepLength = ["Length of sleep bouts (sec)"]
		sleepBouts = ["Sleep bout frequency "]
		daySleepLength = ["Day sleep length(sec)"]
		nightSleepLength = ["Night sleep length(sec)"]
		daySleepFreq = ["Day sleep frequency"]
		nightSleepFreq = ["Night sleep frequency"]
		sleepLatency = ["Sleep latency (sec)"]
		mealSleep = ["Post meal Sleep latency"]
		mealOnsetSleep = ["Pre meal time since sleep"]
		lightSleep = ["Light sleep bout frequency"]
		mediumSleep = ["Medium sleep bout frequency"]
		deepSleep = ["Deep sleep bout frequency"]
		shortSleepT = ["Time spent in light sleep"]
		medSleepT = ["Time spent in medium sleep"]
		longSleepT = ["Time spent in deep sleep"]
		dTotFeed = ["Daytime feeding"]
		nTotFeed = ["Nighttime feeding"]
		dAvgMeal = ["Daytime meal size"]
		nAvgMeal = ["Nighttime meal size"]
		dFreq = ["Daytime feeding frequency"]
		nFreq = ["Nighttime feeding frequency"]
		daySleep = ["Daytime sleep"]
		nightSleep = ["Nighttime sleep"]
		dayDeepSleep = ["Daytime deep sleep"]
		nightDeepSleep = ["Nighttime deep sleep"]
		dayActivity = ["Daytime activity"]
		nightActivity = ["Nighttime activity"]
		ratioNightSleep = ["Ratio of night:day sleep"]
		ratioNightAct = ["Ratio of night:day activity"]
		ratioNightDeepSleep = ["Ratio of night:day deep sleep"]
		iMealInts = ["Satiety ratio"]
		daySatiety = ["NightTime satiety"]
		nightSatiety = ["Daytime satiety"]
		efficiencyIndex = ["Efficiency index(activity / % time awake)"]
		strideDistances = ["Distance traveled / stride"]
		strideLengths = ["Time traveling / stride"]
		strideCount = ["Stride count"]
		velocity = ["Velocity (centimeters / unit read time)"]
		oneActPreFeed = ["Activity 1x(x time) pre feeding (cm)"]
		twoActPreFeed = ["Activity 2x(x time) pre feeding (cm)"]
		oneActPostFeed = ["Activity 1x(x time) post feeding (cm)"]
		twoActPostFeed = ["Activity 2x(x time) post feeding (cm)"]
		oneSleepPreFeed = ["Sleep 0-1(x time) pre feeding (sec)"]
		twoSleepPreFeed = ["Sleep 1-2(x time) pre feeding"]
		oneSleepPostFeed = ["Sleep 0-1(x time) post feeding"]
		twoSleepPostFeed = ["Sleep 1-2(x time) post feeding"]
		feedWake = ["Percent of Feeding Events Occuring During Wake State"]
		firstMeal = ["1st meal (ul)"]
		secondMeal = ["2nd meal (ul)"]
		thirdMeal = ["3rd meal (ul)"]
		fourthMeal = ["4th meal (ul)"]
		maxMeal = ["Maximum meal size (ul)"]
		fastingPer = ["Fasting period length (hr)"]
		firstMealTime = ["First meal time"]
		secondMealTime = ["Second meal time"]
		thirdMealTime = ["Third meal time"]
		firstSleep = ["First sleep"]
		non = [""]

		print("Generating statistics...")

		mealTimeStats = []
		intermealIntervals = []

		# i is general iterator for each fly
		for i in range(flies):
			prog = i / flies
			update_progress(prog)

			################################################################
			## Casual Calculations to describe basic features of behavior ##
			################################################################

			try:
				Activity.append((sum(activity[i])))
			except:
				Activity.append("----")

			try:
				Sleep.append((((sum(sleep[i])) / readsPerSec) / 3600))
			except:
				Sleep.append("----")

			try:
				Feed.append(sum(mealValues[i]))
			except:
				Feed.append("----")

			try:
				FeedPerHr.append(sum(mealValues[i]) / exptLengthHr)
			except:
				FeedPerHr.append("----")

			try:
				percentSleep.append(round(((sum(sleep[i])) / reads) * 100, 1))
			except:
				percentSleep.append("----")

			try:
				avgMeal.append(avg(mealValues[i]))
			except:
				avgMeal.append("----")

			try:
				avgDuration.append(avg(mealDurations[i]))
			except:
				avgDuration.append("----")

			try:
				if mealTimes[i][0] > 0:  # Safety net in case feeding list is empty with
					numMeal.append(len(mealValues[i]))  # 0's in which case it would normally count a freq of 1
				else:
					numMeal.append("----")
			except:
				numMeal.append("----")

			try:
				efficiencyIndex.append(((sum(activity[i]))) / (100 - round(((sum(sleep[i])) / reads) * 100, 1)))
			except:
				efficiencyIndex.append("----")

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

			try:
				readS = 0
				while sleep[i][readS] == 0:
					readS = readS + 1
				firstSleep.append(readS)
			except:
				firstSleep.append("")

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
					iMealInts.append(avg(intermealIntList) / avg(mealValues[i]))
				except:
					fastingPer.append("----")
					iMealInts.append("----")
			else:
				fastingPer.append("----")
				iMealInts.append("----")

			######################################################
			#### Sleep Freq / Avg Length / Depth Counts ##########
			######################################################

			# short code for generating a list of sleepbout lengths

			try:
				sleepCount, sleepLength = sleepFreqLength(sleep[i], readsPerSec)
				avgSleepLength.append(sleepLength)
				sleepBouts.append(sleepCount)
			except:

				avgSleepLength.append("----")
				sleepBouts.append("----")

			try:
				shortCount = sum(1 for x in boutLengths if x >= 300 * r and x < 900 * r)
				medCount = sum(1 for x in boutLengths if x >= 900 * r and x < 1800 * r)
				longCount = sum(1 for x in boutLengths if x > 1800 * r)

				shortTime = sum(short[i])
				medTime = sum(med[i])
				longTime = sum(longS[i])

				lightSleep.append(shortCount)
				mediumSleep.append(medCount)
				deepSleep.append(longCount)

				shortSleepT.append(shortTime)
				medSleepT.append(medTime)
				longSleepT.append(longTime)
			except:

				lightSleep.append("----")
				mediumSleep.append("----")
				deepSleep.append("----")

				shortSleepT.append("----")
				medSleepT.append("----")
				longSleepT.append("----")

			#######################################
			#### Night Vs Day Feed calculations ###
			#######################################
			dayMeals = []
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

			#################################################
			#### Night Vs Day Activity Sleep calculations ###
			#################################################

			lightsOnSleep = []
			lightsOffSleep = []
			lightsOnAct = []
			lightsOffAct = []

			for n in range(len(timeIndex)):
				if (timeIndex[n] % 86400) <= 43200:
					lightsOnSleep.append(sleep[i][n])
					lightsOnAct.append(activity[i][n])
				else:
					lightsOffSleep.append(sleep[i][n])
					lightsOffAct.append(activity[i][n])

			daySleep.append(sum(lightsOnSleep))
			nightSleep.append(sum(lightsOffSleep))
			dayActivity.append(sum(lightsOnAct))
			nightActivity.append(sum(lightsOffAct))

			try:
				sleepCount, sleepLength = sleepFreqLength(lightsOnSleep, readsPerSec)
				daySleepLength.append(sleepLength)
				daySleepFreq.append(sleepCount)

			except:
				daySleepLength.append("----")
				daySleepFreq.append("----")

			try:
				sleepCount, sleepLength = sleepFreqLength(lightsOffSleep, readsPerSec)
				nightSleepLength.append(sleepLength)
				nightSleepFreq.append(sleepCount)
			except:
				nightSleepLength.append("----")
				nightSleepFreq.append("----")

			try:
				actPercent = (darkAct / lightAct)
				sleepPercent = (darkSleep / lightsSleep)
			except:

				actPercent = "----"
				sleepPercent = "----"
			try:

				ratioNightSleep.append(sleepPercent)
				ratioNightAct.append(actPercent)

			except:
				ratioNightSleep.append("----")
				ratioNightAct.append("----")

			################################################
			#########  Deep Sleep Night Day Calcs ##########
			################################################
			lightsOnDeepSleep = []
			lightsOffDeepSleep = []

			try:
				for n in range(len(timeIndex)):
					if (timeIndex[n] % 86400) <= 43200:
						lightsOnDeepSleep.append(longS[i][n])
					else:
						lightsOffDeepSleep.append(longS[i][n])

				Loff = sum(lightsOffDeepSleep)
				Lon = sum(lightsOnDeepSleep)
				dayDeepSleep.append(Lon)
				nightDeepSleep.append(Loff)
			except:
				dayDeepSleep.append("----")
				nightDeepSleep.append("----")

			try:
				ratioNightDeepSleep.append(Loff / Lon)
			except:
				ratioNightDeepSleep.append("----")

			#######################################
			#########  Sleep Latency   ############
			#######################################

			# defined as time between lights off and first sleep event following

			if len(sleep[i]) > 1:
				sleepLats = []
				for n in range(len(timeIndex)):
					if timeIndex[n] % 43200 == 0 and (timeIndex[n] / 43200) % 2 == 1:
						try:
							time = n
							x = 0
							while sleep[i][time + x] == 0:
								x = x + 1
							sleepLats.append(x)
						except:
							fail = 0
				try:
					sleepLatency.append(avg(sleepLats))
				except:
					sleepLatency.append("----")

			else:
				sleepLatency.append("----")

			##########################################
			######## Post meal sleep latency #########
			##########################################

			if len(sleep[i]) > 1:
				mealLats = []
				mealPreLats = []
				for meal in range(len(mealTimesZS[i])):
					try:
						current = timeIndex.index(mealTimesZS[i][meal])
						latency = 0
						try:
							while sleep[i][int(current + latency)] == 0:
								latency = latency + 1
							mealLats.append(latency)
						except:
							pass
						latency = 0
						try:
							while sleep[i][int(current - latency)] == 0:
								latency = latency + 1
							mealPreLats.append(latency)
						except:
							pass

					except:
						pass

				try:
					mealSleep.append(avg(mealLats))
					mealOnsetSleep.append(avg(mealPreLats))
				except:
					mealSleep.append("----")
					mealOnsetSleep.append("----")
			else:
				mealSleep.append("----")
				mealOnsetSleep.append("----")

			#####################################################
			######## Average Stride and stride velocity #########
			#####################################################

			# This measures features of motion for single fly
			# Based on "strides" which is functionally defined here as a discrete continuous motion
			# Note: this will only be useful if reads are fast enough to resolve a stride (> 1hz)

			strides = []
			strideTimeLengths = []
			velocities = []
			strideCounter = 0
			disTotal = 0
			strideTime = 0

			for read in range(1, len(activity[i])):

				if activity[i][read] > 0 and activity[i][read - 1] == 0:
					strideCounter = strideCounter + 1

				if activity[i][read] > 0:
					disTotal = disTotal + activity[i][read]
					strideTime = strideTime + 1

				if activity[i][read] == 0 and activity[i][read - 1] > 0:
					strides.append(disTotal)
					strideTimeLengths.append(strideTime)
					try:
						velocities.append(disTotal / strideTime)
					except:
						pass
					disTotal = 0
					strideTime = 0

			try:
				strideDistances.append(avg(strides))
				strideLengths.append(avg(strideTimeLengths))
				velocity.append(avg(velocities))
				strideCount.append(strideCounter)
			except:
				strideDistances.append("----")
				strideLengths.append("----")
				velocity.append("----")
				strideCount.append("----")

		statsList = [flyCount, Activity, Sleep, Feed, FeedPerHr, numMeal, avgMeal, avgDuration,
					 totalFeedTime, sleepBouts, avgSleepLength, sleepLatency, mealOnsetSleep, mealSleep,
					 dTotFeed, nTotFeed, dAvgMeal, nAvgMeal, dFreq, nFreq, daySleep, nightSleep, daySleepLength,
					 nightSleepLength, daySleepFreq,
					 nightSleepFreq, dayActivity, nightActivity, iMealInts, efficiencyIndex, strideDistances,
					 strideLengths, velocity, strideCount, firstMeal,
					 secondMeal, thirdMeal, fourthMeal, maxMeal, fastingPer, firstMealTime, secondMealTime,
					 thirdMealTime, firstSleep]

		print("")
		print("Statistics complete.")
		toExcelNamed(transpose(statsList), "stats_" + useFileName)



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

def actBin(activity, readsPerSec, shortFileName):
	# This function sums all activity into specified bin sizes as to reduce the
	# number of data points in a graph or data set, This could be used
	# for making the seconds readings into minutes, hours, etc.

	secChart()
	zeitStart = getZeitStart()
	binSize = int(input("Enter activity bin size in seconds: "))
	binSize = int(binSize * readsPerSec)

	########################
	#### Bin generators ####
	########################
	print("Generating activity bin's")
	actBins = []
	for fly in range(len(activity)):
		loc = 0  # loc is bin location
		indivBins = []
		while loc < len(activity[fly]):  # can also be while binLoc + step to cut any partial bins out entirely
			activityBin = sum(activity[fly][loc:loc + binSize])
			indivBins.append(activityBin)
			loc = loc + binSize
		actBins.append(indivBins)
	print("Activity bin's sucessfully generated.")

	norm = False
	if "y" in input("Scale data 0 to 1? (y/n): "):
		norm = True
		normBins = normalizeZeroOne(actBins)

	###############
	### Outputs ###
	###############

	header = []
	for x in range(len(actBins[0])):
		header.append(float(zeitStart + ((binSize * x) / 3600)))

	title = []
	title.append("fly# ZT")
	for i in range(len(actBins)):
		title.append(i + 1)

	actBins.insert(0, header)
	for i in range(len(actBins)):
		actBins[i].insert(0, title[i])

	trans = False
	if "y" in input("transpose data?\t(y: timepoints in rows\t""n: flies in rows) "):
		trans = True
		actBins = transpose(actBins)
		actBins[0][0] = "ZT fly#"
	toExcelNamed(actBins, "actBins_" + str(int(binSize / 60)) + "m_" + shortFileName)

	if norm:
		normBins.insert(0, header[1:])
		for i in range(len(normBins)):
			normBins[i].insert(0, title[i])
		if trans:
			normBins = transpose(normBins)
			normBins[0][0] = "ZT fly#"

		toExcelNamed(normBins, "normActBins_" + str(int(binSize / 60)) + "m_" + shortFileName)

	return (actBins, binSize)


def sleepBin(sleep, readsPerSec, shortFileName):
	# This function allows user to bin sleep data and functions
	# exactly as the activity binning function does

	secChart()
	zeitStart = getZeitStart()
	binSize = int(input("Enter sleep bin size in seconds: "))
	binSize = int(binSize * readsPerSec)

	########################
	#### Bin generators ####
	########################
	print("Generating sleep bin's")
	sleepBins = []
	for fly in range(len(sleep)):
		loc = 0
		indivBins = []
		while loc < len(sleep[fly]):
			sleepingBin = sum(sleep[fly][loc:loc + binSize])
			indivBins.append(sleepingBin)
			loc = loc + binSize
		sleepBins.append(indivBins)

	norm = False
	if "y" in input("Scale data 0 to 1? (y/n): "):
		norm = True
		normBins = normalizeZeroOne(sleepBins)

	###############
	### Outputs ###
	###############

	header = []
	for x in range(len(sleepBins[0])):
		header.append(float(zeitStart + ((binSize * x) / 3600)))

	title = []
	title.append("fly# ZT")
	for i in range(len(sleepBins)):
		title.append(i + 1)

	sleepBins.insert(0, header)
	for i in range(len(sleepBins)):
		sleepBins[i].insert(0, title[i])

	trans = False
	if "y" in input("transpose data?\t(y: timepoints in rows\t""n: flies in rows) "):
		trans = True
		sleepBins = transpose(sleepBins)
		sleepBins[0][0] = "ZT fly#"
	print("NOTE: Data is expressed as seconds spent in sleep state during period")
	toExcelNamed(sleepBins, "sleepBins_" + str(int(binSize / 60)) + "m_" + shortFileName)

	if norm:
		normBins.insert(0, header[1:])
		for i in range(len(normBins)):
			normBins[i].insert(0, title[i])
		if trans:
			normBins = transpose(normBins)
			normBins[0][0] = "ZT fly#"
		toExcelNamed(normBins, "normSleepBins_" + str(int(binSize / 60)) + "m_" + shortFileName)


def feedBins(mealTimes, mealValues, mealDurations, feedFileName):
	# This function goes through list and appends times and meal sizes
	# within specified range groups to separate lists. For instance if
	# your bin interval is 3 it will make lists of all times 0-3,3-6,6-9 etc
	# as well as the meals that correspond to their index couterpart in the
	# input file

	try:
		binSize = float(input("Enter Bin Size(seconds): "))
		binSize = binSize / 3600

	except:
		print("Invalid Entry")
		return
	try:
		masterMealBins = []
		masterTimeBins = []
		masterSatietyBins = []
		maxZeitTime = Max2D(mealTimes)
		UsersBinStart = getZeitStart()

		print("Binning Data....")
		for fly in range(len(mealTimes)):
			timeBins = []
			mealBins = []
			satietyBins = []
			binStart = float(UsersBinStart)

			while binStart < maxZeitTime:
				timeBin = []
				mealBin = []
				satBin = []  # time to next meal/ meal size
				for meal in range(len(mealTimes[fly])):
					if binStart < mealTimes[fly][
						meal] <= binStart + binSize:  # Check if time is above moving start and below moving start + binsize
						timeBin.append(mealTimes[fly][meal])
						mealBin.append(mealValues[fly][meal])

						try:
							satBin.append((mealTimes[fly][meal + 1] - mealTimes[fly][meal]) / mealValues[fly][meal])
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

		norm = False
		if "y" in input("Scale data 0 to 1? (y/n): "):
			norm = True

		header = ["fly# ZT"]
		for i in range(len(masterMealBins[0])):
			header.append(float(UsersBinStart) + i * binSize)

		mealBins = masterMealBins  # 3D matrix layered   meals -> bins -> fly
		timeBins = masterTimeBins
		satietyBins = masterSatietyBins

		masterMealSum = []
		masterMealFreq = []
		masterMealSize = []
		masterSatiety = []
		masters = [masterMealSum, masterMealFreq, masterMealSize, masterSatiety]

		for fly in range(len(mealBins)):
			flyMealSum = []
			flyMealFreq = []
			flyMealSize = []
			flySatiety = []

			for bins in range(len(mealBins[fly])):
				binSum = float(sum(mealBins[fly][bins]))
				flyMealSum.append(binSum)
				zeros = float(
					mealBins[fly][bins].count(0))  # can't use len for frequency because empty lists contain [0]
				freq = int(len(mealBins[fly][bins])) - zeros
				flyMealFreq.append(freq)  # so counting 0's and subtracting from len instead
				if freq > 0:
					flyMealSize.append(binSum / freq)
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

		if norm:
			normBins = normalizeZeroOne(masterMealSum)
			masters.append(normBins)

		for lst in masters:
			for i in range(0, len(lst)):
				lst[i].insert(0, i + 1)
			lst.insert(0, header)

		if not "y" in input("transpose data?\t(y: timepoints in rows\t""n: flies in rows)\n"):
			for lst in masters:
				lst = transpose(lst)
				lst[0][0] = "ZT fly#"

		toExcelNamed(masterMealSum, "feedBins_" + str(int(binSize * 60)) + "m_" + feedFileName)

		if input("Add bins for frequency (y/n): ") == "y":
			toExcelNamed(masterMealFreq, "freqBins_" + str(int(binSize * 60)) + "m_" + feedFileName)
		if input("Add bins for meal size (y/n): ") == "y":
			toExcelNamed(masterMealSize, "sizeBins_" + str(int(binSize * 60)) + "m_" + feedFileName)
		if input("Add bins for satiety (y/n): ") == "y":
			toExcelNamed(masterSatiety, "satBins_" + str(int(binSize * 60)) + "m_" + feedFileName)
		if norm:
			toExcelNamed(normBins, "normFeedBins_" + str(int(binSize * 60)) + "m_" + feedFileName)

		print("Feeding bins generated.")


	except Exception as e:
		print(e)
	return mealBins, timeBins, header


def angBin(angularVelocity, readsPerSec, shortFileName):
	# This function sums all activity into specified bin sizes as to reduce the
	# number of data points in a graph or data set, This could be used
	# for making the seconds readings into minutes, hours, etc.

	secChart()
	zeitStart = getZeitStart()
	binSize = int(input("Enter orientation bin size in seconds: "))
	binSize = int(binSize * readsPerSec)

	########################
	#### Bin generators ####
	########################
	print("Generating delta orientation bin's")
	angBins = []
	for fly in range(len(angularVelocity)):
		loc = 0  # loc is bin location
		indivBins = []
		while loc < len(angularVelocity[fly]):  # can also be while binLoc + step to cut any partial bins out entirely
			angBin = sum(angularVelocity[fly][loc:loc + binSize])
			indivBins.append(angBin)
			loc = loc + binSize
		angBins.append(indivBins)
	print("Activity bin's sucessfully generated.")

	###############
	### Outputs ###
	###############

	header = []
	for x in range(len(angBins[0])):
		header.append(float(zeitStart + ((binSize * x) / 3600)))
	title = ["Z Time"]
	for i in range(len(angBins)):
		title.append(i + 1)
	##	norm = input("Normalize Bins to Mean?(y/n): ")
	##	if norm == "y" or norm == "yes" or norm == "YES" or norm == "Yes":
	##		actBins = normalizeToMean(actBins)
	angBins = transpose(angBins)
	for i in range(1, len(angBins)):
		angBins[i - 1].insert(0, header[i])

	angBins.insert(0, title)
	finalAng = []
	addWord = ["Total Orientation Delta Bins (seconds)", ""]
	finalAng.append(addWord)
	for i in range(len(angBins)):
		finalAng.append(angBins[i])

	toExcelNamed(finalAng, "angBins_" + str(int(binSize / 60)) + "_mins" + shortFileName)

	return (angBins, binSize)


def meanBinGen(thingToBin, readsPerSec, shortFileName, label):
	# This function averages values of any type into specified bin sizes as to reduce the
	# number of data points in a graph or data set, This could be used
	# for making the seconds readings into minutes, hours, etc. Takes a list of lists
	# organized as [fly][attribute]

	secChart()
	zeitStart = getZeitStart()
	binSize = int(input("Enter bin size in seconds: "))
	binSize = int(binSize * readsPerSec)

	########################
	#### Bin generators ####
	########################
	print("Generating bin's")
	thingBins = []
	for fly in range(len(thingToBin)):
		loc = 0  # loc is bin location
		indivBins = []
		while loc < len(thingToBin[fly]):  # can also be while binLoc + step to cut any partial bins out entirely
			try:
				thingBin = avg(thingToBin[fly][loc:loc + binSize])
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
		header.append(float(zeitStart + ((binSize * x) / 3600)))
	title = ["Z Time"]
	for i in range(len(thingBins)):
		title.append(i + 1)
	thingBins = transpose(thingBins)
	for i in range(len(thingBins)):
		thingBins[i].insert(0, header[i])

	thingBins.insert(0, title)
	finalBins = []
	addWord = ["Total Count Bins (seconds)", ""]
	finalBins.append(addWord)
	for i in range(len(thingBins)):
		finalBins.append(thingBins[i])

	toExcelNamed(finalBins, label + str(int(binSize / 60)) + "_mins" + shortFileName)


def sleepDepth(sleep, readsPerSec):
	# This algorithm cycles through the sleep binary and keeps a count of
	# seconds sleeping. When the count is within the light , med , or deep sleep
	# range it will append a 1 to that given list (light,med,deep), Note: sleep depths not currently in use

	light = []
	med = []
	deep = []

	for fly in range(len(sleep)):
		sL = []
		sM = []
		sD = []
		count = 0
		for read in range(len(sleep[fly])):
			# Sleep Second Counter
			if sleep[fly][read] == 1:
				count = count + 1
			else:
				count = 0

			# Test for which sleep category count falls under
			if count > 0 and count < (600 * readsPerSec):
				sL.append(1)
				sM.append(0)
				sD.append(0)
			elif count >= (600 * readsPerSec) and count < (1500 * readsPerSec):
				sL.append(0)
				sM.append(1)
				sD.append(0)
			elif count >= (1500 * readsPerSec):
				sL.append(0)
				sM.append(0)
				sD.append(1)
			else:
				sL.append(0)
				sM.append(0)
				sD.append(0)
		light.append(sL)
		med.append(sM)
		deep.append(sD)

	return light, med, deep


def walkLength(activity, X, Y):
	# This function captures the length of individual discrete walking events

	walkList = []
	startX = []
	stopX = []
	startY = []
	stopY = []

	for fly in range(len(activity)):
		# walkListInd = []
		walkLen = 0

		minX = min(X[fly])
		minY = min(Y[fly])

		for read in range(len(activity[fly])):
			if activity[fly][read] > 0:
				walkLen = walkLen + activity[fly][read]
			try:
				if activity[fly][read] > 0 and activity[fly][read - 1] == 0:
					startX.append(X[fly][read] - minX)
					startY.append(Y[fly][read] - minY)
			except:
				pass
			if activity[fly][read] == 0 and walkLen > 0:
				walkList.append(walkLen)
				if walkLen > 3.7 and walkLen < 4.1:
					stopX.append(X[fly][read] - minX)
					stopY.append(Y[fly][read] - minY)
				walkLen = 0

	# walkList.append(walkListInd)
	# xyToHeat(startX,startY)
	xyToHeat(stopX, stopY)


def getZeitStart():
	# gets start zeitgeber time from user
	global zeitStart
	try:
		zeitStart == 1
	except:
		try:
			#zeitDay = float(input("Day of the experiment? ")) - 1
			zeitStart = float(input("Enter start Zeitgeiber hour (wait for minutes!): "))
			zeitMin = float(input("Minute of the hour: "))
			zeitStart=zeitStart+(zeitMin/60)
			#zeitStart = zeitDay * 24 + zeitStart + (zeitMin / 60)

		except:
			zeitStart = 0
			print("Default ZT start time = 0")
	return zeitStart


############################################
#########Location based functions###########
############################################

def getCoordinates(animalTrack):
	# get coordinates using workList (raw Tracker Data) assumes that numEntries, gap is global
	X = []  # x coordiante list
	Y = []  # y coordinate list
	print('Getting coordinates...')
	print("")
	flyCount = int(len(animalTrack) / 2)
	for fly in range(flyCount):
		X.append(animalTrack[int(fly * 2)])
		Y.append(animalTrack[int(fly * 2 + 1)])
		prog = fly / flyCount
		update_progress(prog)

	return X, Y


def collective(X, Y, activity, readsPerSec, shortFileName):
	# Funtion for performing basic analysis on multiTracking data in which animals can interact and have collective properties
	# uses global variables such as numEntries, gap, pixPerCM, and flyLength

	zeitStart = getZeitStart()
	timeIndex = framesToSecs(readsPerSec, zeitStart, activity)

	print('Scanning for identity switch...')
	maxDistPoss = 2  # denotes maximum fly lengths a fly can travel/read, flyLenghts is a global variable
	for fly in range(len(activity)):
		for read in range(len(activity)):
			if activity[fly][read] > (flyLength / pixPerCM) * maxDistPoss:
				activity[fly][read] = 0
	print('Cleaned identity switch occurrences.')
	sleep = getSleep(activity, readsPerSec)

	minVelocity = 0.5 / readsPerSec  # this represents 5mm / sec in cm's / sec from Dankert et.al chase definition  original .1
	minSep = 0.3 * pixPerCM  # minimum separation between flies for chase 3mm converted to pixels
	maxSep = 1 * pixPerCM  # max separation 15mm converted to pixels
	minDuration = int(1 * readsPerSec)  # min duration of 1 second
	startleInact = int(
		1 * readsPerSec)  # min duration which flyB must be inactive before being touched by flyA to be considered for startle
	touchDistance = flyLength * 1.1  # min distance between centers to be considered touchinging
	startleDelay = int(round(0.3 * readsPerSec, 1))  # min duration to onset of motion following a touching event
	# Note activity is already in cm's while X and Y is in pixels

	chase = []
	cluster = []
	touch = []
	touching = []
	startle = []
	startled = []
	wakeup = []
	woken = []

	yes = 1  # see if we can replace .append(yes)
	for flyA in range(len(X)):
		chaseMat = []
		clusterMat = []
		touchMat = []
		touchingMat = []
		startleMat = []
		startledMat = []
		wakeupMat = []
		wokenMat = []

		for flyB in range(len(X)):
			chaseVector = []
			clusterVector = []
			touchVector = []
			touchingVector = []
			startleVector = []
			startledVector = []
			wakeupVector = []
			wokenVector = []

			if flyA != flyB:  # stops program from checking behaviors against itself

				for read in range(len(activity[flyB])):
					dis = distance(X[flyA][read], Y[flyA][read], X[flyB][read], Y[flyB][read])
					clusterVector.append(dis)

					if minSep < dis < maxSep:
						if activity[flyA][read] * readsPerSec > minVelocity and activity[flyB][
							read] * readsPerSec > minVelocity:
							chaseVector.append(1)
						else:
							chaseVector.append(0)
					else:
						chaseVector.append(0)

					# touching detector  Note: an animal can remain touching for extended period

					if dis <= touchDistance:
						touchingVector.append(1)  ### this is a problem

					else:  # still Stops
						touchingVector.append(0)

					# startle and wakeup detector  (A startles B)
					try:
						if touchingVector[-1] == 1 and touchingVector[
							-2] == 0:  # checks if this was the moment of touch initiation rather than some period in the middle of an extended touching
							touchVector.append(1)
							if sum(activity[flyB][read - startleInact:read]) == 0 and sum(
									activity[flyB][read:read + startleDelay]) > 0:
								startleVector.append(1)
								# since all wakeup's are inherently startles we can check if pre-startle inactivity is sleep
								if sleep[flyB][read - 1] == 1:
									wakeupVector.append(1)
								else:
									wakeupVector.append(0)
							else:
								startleVector.append(0)
								wakeupVector.append(0)
							# simply flips the interaction above to measure startled and woken
							if sum(activity[flyA][read - startleInact:read]) == 0 and sum(
									activity[flyA][read:read + startleDelay]) > 0:
								startledVector.append(1)
								# since all wakeup's are inherently startles we can check if pre-startle inactivity is sleep
								if sleep[flyB][read - 1] == 1:
									wokenVector.append(1)
								else:
									wokenVector.append(0)
							else:
								startledVector.append(0)
								wokenVector.append(0)
						else:
							touchVector.append(0)
							startleVector.append(0)
							startledVector.append(0)
							wakeupVector.append(0)
							wokenVector.append(0)
					except:
						touchVector.append(0)
						startleVector.append(0)
						startledVector.append(0)
						wakeupVector.append(0)
						wokenVector.append(0)

				chaseVector = filterFragments(chaseVector,
											  minDuration)  # This takes only chase events which last greater than min chase duration
				clusterMat.append(clusterVector)
				chaseMat.append(chaseVector)
				touchMat.append(touchVector)
				touchingMat.append(touchingVector)
				startleMat.append(startleVector)
				startledMat.append(startledVector)
				wakeupMat.append(wakeupVector)
				wokenMat.append(wokenVector)

		cluster.append(clusterMat)
		chase.append(chaseMat)
		touch.append(touchMat)
		touching.append(touchingMat)
		startle.append(startleMat)
		startled.append(startledMat)
		wakeup.append(wakeupMat)
		woken.append(wokenMat)

	##### temporary touch Test #######
	touchingOut = []
	startledOut = []
	chaseOut = []
	iTouch = []
	for fly in range(len(touching)):
		touchingOut.append(flatten2D(touching[fly]))
		iTouch.append(flatten2D(touch[fly]))
		startledOut.append(flatten2D(startled[fly]))
		chaseOut.append(flatten2D(chase[fly]))
	touchingOut = transpose(touchingOut)
	# startledOut = transpose(startledOut)
	chaseOut = transpose(chaseOut)
	# toExcelNamed(touchingOut,"touchingOut")
	# toExcelNamed(startledOut,"startledOut")
	# toExcelNamed(chaseOut,"chaseOut")

	totalCluster = ["Distance from A to B (pixels)"]
	totalChase = ["Time spent in chase"]
	totalTouch = ["Touch events A to B"]
	totalTouching = ["Time A is touching B"]
	totalStartle = ["A Startles B"]
	totalStartled = ["A is startled by B"]
	totalWakeup = ["A Wakes up B"]
	totalWoken = ["A is woken by B"]
	totalSleep = ["Sleep (sec)"]
	totalActivity = ["Activity (cm)"]
	flyNum = ["Fly #"]

	for fly in range(len(cluster)):
		totalCluster.append((sum2D(cluster[fly]) / (len(cluster[fly]) * len(cluster[fly][0]))))
		totalTouch.append(sum2D(touch[fly]))
		totalTouching.append(sum2D(touching[fly]))
		totalChase.append(sum2D(chase[fly]))
		totalStartle.append(sum2D(startle[fly]))
		totalStartled.append(sum2D(startled[fly]))  # error
		totalWakeup.append(sum2D(wakeup[fly]))
		totalWoken.append(sum2D(woken[fly]))
		totalSleep.append(sum(sleep[fly]) / readsPerSec)
		totalActivity.append(sum(activity[fly]))
		flyNum.append(fly)

	finalOut = [flyNum, totalCluster, totalTouch, totalTouching, totalChase, totalStartle, totalStartled, totalWakeup,
				totalWoken, totalSleep, totalActivity]
	toExcelNamed(finalOut, "collective.Behavior_" + shortFileName)

	surrList = []
	##### get activity surrounding touch events
	for fly in range(len(iTouch)):
		for read in range(len(startledOut[fly])):
			if startledOut[fly][read] > 0:
				try:
					temp = activity[fly][read - 2500:read + 2500]
					surrList.append(temp)
				except:
					pass
	surrList = transpose(surrList)
	toExcel(surrList)


def heatMap(workList, readsPerSec, activity, X, Y, mealValues=0, mealDurations=0, mealTimes=0):
	print("Generating Heat Map...")
	flyCount = len(activity)
	xCo = X  # x coordiante list
	yCo = Y  # y coordinate list

	xMax = Max2D(xCo)
	yMax = Max2D(yCo)
	xMin = Min2D(xCo)
	yMin = Min2D(yCo)

	xLen = int(xMax - xMin)
	missed = 0
	splitQ = input("Break Heat Maps into temporal sections? (y/n): ")

	if splitQ == "yes" or splitQ == "y":
		cum = input("Make sections cumulative? (y/n): ")
		split = float(input("What size time sections would you like (in mins): "))

		maps = []  # initialize map
		for i in range(int(yMax - yMin)):  # create blank map
			maps.append([0] * xLen)

		sendOutMaps = input("Write heat maps to working directory(y/n): ")

		if split > 0:
			split = int(split * (readsPerSec * 60))
			for i in range(round(len(xCo[0]) / split)):
				if cum == "n":
					maps = []
					for k in range(int(yMax - yMin)):
						maps.append([0] * xLen)
				for fly in range(len(xCo)):
					for read in range(i * split, i * split + split):
						try:
							x = int(xCo[fly][read] - xMin - 1)
							y = int(yCo[fly][read] - yMin - 1)
							maps[y][x] = maps[y][x] + 1
						except:
							missed = missed + 1

				if sendOutMaps == "y":
					directory = os.getcwd()
					outputDataName = "section" + str(i)
					outputDataName = directory + "/" + outputDataName + ".csv"

					import csv

					with open(outputDataName, 'w', newline='') as f:
						writer = csv.writer(f)
						writer.writerows(maps)

	else:

		maps = []
		for i in range(int(yMax - yMin)):
			maps.append([0] * xLen)
		for fly in range(len(xCo)):
			for read in range(len(xCo[fly])):
				try:
					x = int(xCo[fly][read] - xMin - 1)
					y = int(yCo[fly][read] - yMin - 1)
					maps[y][x] = maps[y][x] + 1
				except:
					missed = missed + 1

		print("Heat Map Generated")
		toExcel(maps)

	runSpatSplit = input("Run spatial splitter (yes/no): ")
	if runSpatSplit == "yes" or runSpatSplit == "y":

		splitNum = int(input("Enter number of vertical quadrants: "))
		yHeight = yMax - yMin
		quadHeight = int(yHeight / splitNum)
		Quads = []

		header = []
		header.append("")
		for i in range(len(yCo)):
			header.append(str("Fly " + str(i + 1)))
		Quads.append(header)
		try:
			if splitQ == "yes" or splitQ == "y":

				for i in range(round(len(yCo[0]) / split)):  # rounds time series count to nearest whole time piece
					title = [str("Time Group " + str(i)),
							 ""]  # for instance: a 23 hr experiment split into 12 hr sections will give 2 12hr time pieces instead of 1
					Quads.append(title)
					for x in range(splitNum):
						highMark = yMin + (x * quadHeight)
						lowMark = yMin + (x * quadHeight) + quadHeight
						times = []
						times.append(str("Quad " + str(x + 1)))
						for fly in range(len(yCo)):
							timeSpent = 0
							for read in range(i * split, i * split + split):
								try:
									if yCo[fly][read] >= highMark and yCo[fly][read] < lowMark:
										timeSpent = timeSpent + 1
								except:
									pass
							times.append(timeSpent)
						Quads.append(times)
				toExcel(Quads)



			else:

				for x in range(splitNum):
					highMark = yMin + (x * quadHeight)
					lowMark = yMin + (x * quadHeight) + quadHeight
					times = []
					times.append(str("Quad " + str(x + 1)))
					for fly in range(len(yCo)):
						timeSpent = 0
						for read in range(len(yCo[fly])):
							if yCo[fly][read] >= highMark and yCo[fly][read] < lowMark:
								timeSpent = timeSpent + 1
						times.append(timeSpent)
					Quads.append(times)
				toExcel(Quads)
		except:
			print("Error...")
			print("Check input values.")

	ndMap = input("Run day/night heatmap(y/n): ")
	if ndMap == "y":
		zeitStart = getZeitStart()
		timeIndex = framesToSecs(readsPerSec, zeitStart, activity)
		nightMap = []
		dayMap = []
		for i in range(int(yMax - yMin)):  # create blank map
			nightMap.append([0] * xLen)
			dayMap.append([0] * xLen)

		for fly in range(len(xCo)):
			for read in range(len(xCo[fly])):
				x = int(xCo[fly][read] - xMin - 1)
				y = int(yCo[fly][read] - yMin - 1)
				if (timeIndex[read] % 86400) <= 43200:
					dayMap[y][x] = dayMap[y][x] + 1
				else:
					nightMap[y][x] = nightMap[y][x] + 1

		toExcelNamed(dayMap, "dayMap")
		toExcelNamed(nightMap, "nightMap")

	surroundFeeding = input("Run heat map surrounding feeding events(y/n): ")
	if surroundFeeding == "y":
		startHour = float(input("Enter start Zeitgeiber hour (wait for minutes!): "))
		startMin = float(input("Minute of the Hour: "))
		zeitStart = getZeitStart()
		surMap = []
		start = int(input("relative starting time(s): "))
		end = int(input("relative end time(s): "))

		for i in range(int(yMax - yMin)):  # create blank map
			surMap.append([0] * xLen)

		# mealTimes converted to z-time seconds
		mealTimesZS = []
		for i in range(len(mealTimes)):
			indieMeals = []
			for n in range(len(mealTimes[i])):
				indieMeals.append(round((mealTimes[i][n] * 60 * 60), 0))
			mealTimesZS.append(indieMeals)

		# creates z-time seconds indexing list for activity and sleep
		step = 1 / readsPerSec
		current = 0
		timeIndex = []
		for x in range(len(activity[0])):
			timeIndex.append(round(current + zeitStart, 0))
			current = current + step

		vertList = []
		xTrace = []
		yTrace = []
		for fly in range(len(mealTimesZS)):
			for meal in range(len(mealTimesZS[fly])):
				subVert = []
				subXTrace = []
				subYTrace = []
				try:
					current = timeIndex.index(mealTimesZS[fly][meal])
					for n in range(start, end, 1):
						try:
							x = int(xCo[fly][current + n] - xMin - 1)
							y = int(yCo[fly][current + n] - yMin - 1)
							surMap[y][x] = surMap[y][x] + 1
							subVert.append(y)
							subXTrace.append(x)
							subYTrace.append(y * -1)
						except:
							pass
					vertList.append(subVert)
					xTrace.append(subXTrace)
					yTrace.append(subYTrace)
				except:
					pass

		xTrace = transpose(xTrace)
		yTrace = transpose(yTrace)
		toExcelNamed(xTrace, "x_trace")
		toExcelNamed(yTrace, "y_trace")
		print('Writing surround map...')
		toExcel(surMap)
		print('Writing vertical kymograph...')
		toExcel(vertList)

	return maps


def xyToHeat(x, y):
	# simplified function for taking a vector for x and y and creating a heat map out of them
	maps = []
	xMax = max(x)
	xMin = min(x)
	yMax = max(y)
	yMin = min(y)
	xLen = int(xMax - xMin)

	for i in range(int(yMax - yMin)):
		maps.append([0] * xLen)

	for i in range(len(x)):
		try:
			yPos = int(y[i])
			xPos = int(x[i])
			maps[yPos][xPos] = maps[yPos][xPos] + 1
		except:
			print('error')
			pass
	print("Heat Map Generated")
	toExcel(maps)


def getBriefAwakenings(activity, readsPerSec, shortFileName, mealTimes=0, mealValues=0):
	sleepLength = int(readsPerSec * 300)
	awakeningLength = int(readsPerSec * 60)
	briefAwake = []
	for fly in range(len(activity)):
		briefFly = []
		for read in range(len(activity[fly])):
			try:
				if sum(activity[fly][read:read + awakeningLength]) > 0 \
						and sum(activity[fly][read - sleepLength:read]) == 0 \
						and sum(activity[fly][read + awakeningLength:read + sleepLength + awakeningLength]) == 0 \
						and sum(briefFly[read - awakeningLength:]) == 0:
					briefFly.append(1)
				else:
					briefFly.append(0)
			except:
				briefFly.append(0)
		briefAwake.append(briefFly)

	zeitStart = getZeitStart()
	timeIndex = framesToSecs(readsPerSec, zeitStart, activity)  # use timeIndex for meal relative arousal
	label = "briefAwake"
	meanBinGen(briefAwake, readsPerSec, shortFileName, label)

	if type(mealTimes) != int:
		# mealTimes converted to z-time seconds
		mealTimesZS = []
		for i in range(len(mealTimes)):
			indieMeals = []
			for n in range(len(mealTimes[i])):
				indieMeals.append(round((mealTimes[i][n] * 60 * 60), 0))
			mealTimesZS.append(indieMeals)

		# time(sec's) from feeding event that arousal is appended
		timePush = int(input("Enter absolute time(sec's) surrounding feeding events: "))
		timePush = int(timePush * readsPerSec)
		step = int(input("Enter step interval(sec's) surrounding feeding events: "))
		finalList = []
		for fly in range(len(mealTimes)):
			for meal in range(len(mealTimes[fly])):
				featureBinary = []
				try:
					current = timeIndex.index(mealTimesZS[fly][meal])
					for n in range(-timePush, timePush, step):
						try:
							featureBinary.append(avg(briefAwake[fly][current + n:current + n + step]))
						except:
							featureBinary.append("")
				except:
					featureBinary.append("")

				featureBinary.insert(0, mealTimes[fly][meal])
				featureBinary.insert(0, mealValues[fly][meal])
				featureBinary.insert(0, fly)
				finalList.append(featureBinary)

		finalList = transpose(finalList)
		toExcelNamed(finalList, shortFileName + "feeding_breifAwake")

	return briefAwake


def virtualBeam(X, Y, readsPerSec):
	# creates virtual beam in the mid y coordinate of ARC tracking
	# and counts crosses over it

	# vh = input(Are chabers veritical or horizonatal? (v/h):

	xory = input("Split x or y axis (x/y): ")
	if xory == "x":
		ax = X
	else:
		ax = Y

	beam = []
	for fly in range(len(ax)):
		beamInd = ((max(ax[fly]) - min(ax[fly])) * .5) + min(ax[fly])
		beam.append(beamInd)

	beamCross = []
	nearBeam = []
	for fly in range(len(ax)):
		beamCrossIndividual = []
		nearBeamIndividual = []
		for read in range(len(ax[fly])):
			cross = 0
			try:
				if ax[fly][read] < beam[fly] and ax[fly][read + 1] >= beam[fly]:
					cross = 1
				elif ax[fly][read] > beam[fly] and ax[fly][read + 1] <= beam[fly]:
					cross = 1
				else:
					cross = 0
			except:
				cross = 0

			beamCrossIndividual.append(cross)
		beamCross.append(beamCrossIndividual)

	beamSleep = getSleep(beamCross, readsPerSec)

	print('Warning!: activity and sleep data is now set to virtual beam analysis.')
	return beamCross, beamSleep


def kymograph(workList, readsPerSec, shortFileName, X, Y):
	print("Kymograph generator")
	print("Note: generates normalized vertical coordinate kymographs.")
	print("where 0 is the lowest point in the chamber and 1 is")
	print("the highest.")
	flyCount = int(len(workList) / numEntries)  # gives number of flies

	xMax = Max2D(X)
	yMax = Max2D(Y)
	xMin = Min2D(X)
	yMin = Min2D(Y)

	# normalizes x and y's to a 0 to 1 scale so experiments with different coordinates are comparable
	xory = input("Along which axis should the kymograph be generated(x/y): ")
	if xory == "x":
		ax = X
	else:
		ax = Y

	for fly in range(len(ax)):
		Min = min(ax[fly])
		Max = max(ax[fly])
		for i in range(len(ax[fly])):
			pos = ax[fly][i]
			try:
				ax[fly][i] = 1 - ((pos - Min) / (Max - Min))
			except:
				ax[fly][i] = 0

	secChart()
	zeitStart = getZeitStart()
	binSize = int(input("Enter kymograph bin size in seconds: "))
	binSize = int(binSize * readsPerSec)

	########################
	#### Bin generators ####
	########################
	print("Generating kymograph bin's")
	kymBins = []
	for fly in range(len(ax)):
		loc = 0  # loc is bin location
		indivBins = []
		while loc < len(ax[fly]):  # can also be while binLoc + step to cut any partial bins out entirely
			axBin = avg(ax[fly][loc:loc + binSize])
			indivBins.append(axBin)
			loc = loc + binSize
		kymBins.append(indivBins)
	print("Kymograph bin's sucessfully generated.")

	###############
	### Outputs ###
	###############

	header = []
	for x in range(len(kymBins[0])):
		header.append(float(zeitStart + ((binSize * x) / 3600)))
	title = ["Z Time"]
	for i in range(len(kymBins)):
		title.append(i + 1)

	kymBins = transpose(kymBins)
	for i in range(len(kymBins)):
		kymBins[i].insert(0, header[i])

	kymBins.insert(0, title)
	finalKym = []
	addWord = ["Positional Bins (seconds)", ""]
	finalKym.append(addWord)
	for i in range(len(kymBins)):
		finalKym.append(kymBins[i])

	toExcelNamed(finalKym, "kymographBins_" + str(int(binSize / 60)) + "_mins" + shortFileName)


def hotZone(workList, readsPerSec, numEntries, shortFileName):
	try:
		flyCount = len(workList) / numEntries
		xCo = []  # x coordiante list
		yCo = []  # y coordinate list

		for fly in range(flyCount):
			xCo.append(workList[gap + fly * numEntries])
			yCo.append(workList[gap + fly * numEntries + 1])

		# coordinates of hot zones
		xMins = [165, 307, 438, 576]
		xMaxs = [195, 342, 473, 611]
		yMins = [32, 32, 32, 32]
		yMaxs = [82, 87, 87, 87]
		attempts = []

		for fly in range(len(xCo)):
			flyAttempts = []
			for read in range(len(xCo[fly])):
				if xMins[fly] < xCo[fly][read] < xMaxs[fly] and yMins[fly] < yCo[fly][read] < yMaxs[
					fly]:  # checks if fly is inside 'hot zone'
					try:
						if xCo[fly][read + 1] < xMins[fly] or xCo[fly][read + 1] > xMaxs[fly] or yCo[fly][read + 1] < \
								yMins[fly] or yCo[fly][read + 1] > yMaxs[
							fly]:  # checks if fly left 'hot zone' the read after being inside
							flyAttempts.append(1)
						else:
							flyAttempts.append(0)
					except:
						flyAttempts.append(0)
				else:
					flyAttempts.append(0)

			attempts.append(flyAttempts)
		totalAttempts = []
		for fly in range(len(attempts)):
			temp = [sum(attempts[fly])]
			totalAttempts.append(temp)
		toExcelNamed(totalAttempts, "attempts_" + shortFileName)

		#### Bin generator ####
		secChart()
		binSize = int(input("Enter bin size in seconds: "))
		binSize = int(binSize * readsPerSec)
		attemptBins = []
		for fly in range(len(attempts)):
			loc = 0
			indivBins = []
			while loc < len(attempts[fly]):
				aBin = sum(attempts[fly][loc:loc + binSize - 1])
				indivBins.append(aBin)
				loc = loc + binSize
			attemptBins.append(indivBins)

		###############
		### Outputs ###
		###############

		header = []
		for x in range(len(attemptBins[0])):
			header.append(float(zeitStart + ((binSize * x) / 3600)))
		title = ["Z Time"]
		for i in range(len(attemptBins)):
			title.append(i + 1)
		##		norm = input("Normalize Bins to Mean?(y/n): ")
		##		if norm == "y" or norm == "yes" or norm == "YES" or norm == "Yes":
		##			attemptBins = normalizeToMean(attemptBins)
		attemptBins = transpose(attemptBins)
		for i in range(len(attemptBins)):
			attemptBins[i].insert(0, header[i])

		attemptBins.insert(0, title)
		finalAttempts = []
		addWord = ["Total Attempt Bins", ""]
		finalAttempts.append(addWord)
		for i in range(len(attemptBins)):
			finalAttempts.append(attemptBins[i])

		toExcelNamed(finalAttempts, "attemptBins_" + str(int(binSize / 60)) + "_mins" + shortFileName)

	except:
		print("Check numEntries in Constants section")


##########################################
###### Motion Characterization ###########
##########################################

def strideCharacterize(activity, timeIndex, mealTimesZS, mealValues):
	finalList = []
	for fly in range(len(mealTimesZS)):
		for meal in range(len(mealTimesZS[fly])):
			vels = []
			try:
				current = timeIndex.index(mealTimesZS[fly][meal])

				strides = []
				strideTimeLengths = []
				velocities = []
				strideCounter = 0
				disTotal = 0
				strideTime = 0

				for read in range(current, current + 900):
					if activity[fly][read] > 0 and activity[fly][read - 1] == 0:
						strideCounter = strideCounter + 1

					if activity[fly][read] > 0:
						disTotal = disTotal + activity[fly][read]
						strideTime = strideTime + 1

					if activity[fly][read] == 0 and activity[fly][read - 1] > 0:
						strides.append(disTotal)
						strideTimeLengths.append(strideTime)
						try:
							velocities.append(disTotal / strideTime)
						except:
							pass
						disTotal = 0
						strideTime = 0

				try:
					vels.append(fly)
					vels.append(mealValues[fly][meal])
					vels.append(avg(velocities))
				except:
					vels.append("----")

				finalList.append(vels)
			except:
				pass

	finalList = transpose(finalList)
	print("strideCharacterize run...")
	toExcel(finalList)

	return finalList


def groomGen(groomData, activity, inactivity, sleep, readsPerSec):
	# This function takes a "groomFile" and creates a 2D list containing grooming binaries
	# for each fly. A groom file is organized as [[fly # vector],[groom start readings],[groom end readings]]
	# This function starts by making an empty 0 binary for the number of flies in the experiment
	# which is observed by the length of the sleep list fed into the system. It then goes read by
	# read and fills in 1 values for the given ranges for a given fly indicated by groomData[0]

	flyCount = int(len(activity))
	readCount = int(len(activity[0]))
	groom = [[0] * readCount for i in range(flyCount)]  # generate a blank flyCount x readCount list
	origSleep = sleep

	for read in range(len(groomData[0])):
		for i in range(int(groomData[1][read]), int(groomData[2][read] + 1)):
			try:
				groom[int(groomData[0][read] - 1)][i - 1] = 1
			except:
				pass

	# here we recalculate sleep to include grooming, where sleep is defined as a periods absent
	# of grooming and motion for at least 5 minutes
	sleep = []
	sleepLength = int(readsPerSec * 300)
	for fly in range(len(activity)):
		sleepIndiv = []
		for reading in range(len(activity[fly])):
			if activity[fly][reading] == 0 and groom[fly][reading] == 0:
				try:
					sumAct = sum(activity[fly][reading:reading + sleepLength])
					sumGroom = sum(groom[fly][reading:reading + sleepLength])
					if sumAct == 0 and sumGroom == 0 or sleepIndiv[-1] == 1:
						sleepIndiv.append(1)
					else:
						sleepIndiv.append(0)
				except:
					sleepIndiv.append(
						0)  # This exception is run when there are no elements in sleepIndiv[-1] or first frame
			else:  # it assumes an animal is awake when there is no prior knowledge of its state and it is inactive
				sleepIndiv.append(0)
		sleep.append(sleepIndiv)

	a = transpose(activity)
	s = transpose(sleep)
	g = transpose(groom)
	toExcelNamed(a, 'act')
	toExcelNamed(s, 'sleep')
	toExcelNamed(g, 'groom')

	groomErr = []
	for fly in range(len(origSleep)):
		ind = []
		for read in range(len(origSleep[fly])):
			if origSleep[fly][read] == 1:
				if groom[fly][read] == 1:
					ind.append(1)
				else:
					ind.append(0)
			else:
				ind.append("")
		groomErr.append(ind)

	return (groom, sleep, groomErr)


def sleepVisual(visData):
	flyCount = int(input("Enter number of animals in data: "))
	readCount = int(input("Enter total number of seconds of data: "))
	matrix = [[0] * readCount for i in range(flyCount)]  # generate a blank flyCount x readCount list

	for read in range(len(visData[0])):
		for i in range(int(visData[1][read]), int(visData[2][read] + 1)):
			try:
				matrix[int(visData[0][read] - 1)][i - 1] = 1
			except:
				pass

	out = transpose(matrix)
	toExcelNamed(out, "output_matrix")
	return (matrix)

def mealRelation(mealTimes, mealValues, mealDurations, feedFileName, activity, sleep, readsPerSec):
	flyNum = []
	mealSizes = []
	mealTime = []
	mealDurs = []
	timeSinceLast = []
	timeToNext = []
	actSinceLast = []
	sleepSinceLast = []
	actToNext = []
	sleepToNext = []
	numBouts = []
	mealEnds = []

	zeitStart = getZeitStart()

	timeIndex = framesToSecs(readsPerSec, zeitStart, activity)

	# mealTimes converted to z-time seconds
	mealTimesZS = []
	for i in range(len(mealTimes)):
		indieMeals = []
		for n in range(len(mealTimes[i])):
			indieMeals.append(round((mealTimes[i][n] * 60 * 60), 0))
		mealTimesZS.append(indieMeals)

	for fly in range(len(mealTimes)):
		for meal in range(len(mealTimes[fly])):
			mealSizes.append(mealValues[fly][meal])
			mealTime.append(mealTimes[fly][meal])
			mealDurs.append(mealDurations[fly][meal])
			numBouts.append(boutCounts[fly][meal])
			mealEnds.append(mealEndTimes[fly][meal])
			flyNum.append(fly)

			if meal > 0:
				timeSinceLast.append(mealTimes[fly][meal] - mealEndTimes[fly][meal - 1])
				try:
					current = timeIndex.index(mealTimesZS[fly][meal])
					last = timeIndex.index(mealTimesZS[fly][meal - 1])
					actSinceLast.append(sum(activity[fly][last:current]))
					sleepSinceLast.append((sum(sleep[fly][last:current]) / readsPerSec) / 3600)
				except:
					actSinceLast.append("")
					sleepSinceLast.append("")

			else:
				timeSinceLast.append("")
				actSinceLast.append("")
				sleepSinceLast.append("")

			try:
				if meal < len(mealTimes[fly]):
					timeToNext.append(mealTimes[fly][meal + 1] - mealEndTimes[fly][meal])
					current = timeIndex.index(mealTimesZS[fly][meal])
					nex = timeIndex.index(mealTimesZS[fly][meal + 1])
					actToNext.append(sum(activity[fly][current:nex]))
					sleepToNext.append((sum(sleep[fly][current:nex]) / readsPerSec) / 3600)

				else:
					timeToNext.append("")
					actToNext.append("")
					sleepToNext.append("")

			except:
				timeToNext.append("")
				actToNext.append("")
				sleepToNext.append("")

	for x in range(len(flyNum)):
		flyNum[x] += 1

	final = [flyNum, mealSizes, mealTime, mealDurs, timeSinceLast, timeToNext, actSinceLast, actToNext, sleepSinceLast,
			 sleepToNext]
	final = transpose(final)


	toExcelNamed([["fly#", "meal size (ul)", "meal time", "meal duration (sec)", "time since last meal (hr)",
				   "time to next meal (hr)", "activity since last meal (cm)", "activity until next meal (cm)",
				   "sleep since last meal (hr)", "sleep until next meal (hr)"]] + final,
				 "mealRelation_" + feedFileName)


def filterFragments(vector, minRep):
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
	return (filterVector)


def framesToSecs(readsPerSec, zeitStart, activity):
	# This is to generate a list of times in seconds that correspond to the activity and sleep lists
	# Once we have both meals, acivity and sleep related to seconds we can make comparisons by indexing
	# If read interval is greater than 1 second there may be missing intervals to match from feeding -> acitivty and sleep
	# In this case the program will begin shifting the second index up by 1 until it finds
	# data in the activity that is indexable. For instance if the meal is at 301 seconds and activity reads only exist at
	# 300, 305, 310 ... then the error will shift the index by 1 until there is an indexing match. This is only used in the section
	# below relating meal times to activity and sleep

	zeitStartSec = round(((zeitStart) * 60 * 60), 0)  # converts zeitgeber starting time from hours to seconds
	timeIndex = []
	step = 1 / readsPerSec
	current = 0
	if not activity == None:
		for x in range(len(activity[0])):
			timeIndex.append(round(current + zeitStartSec, 0))
			current = current + step
	return timeIndex


########################################
###### Commonplace functions ###########
########################################

def rangeCheck(minimum, maximum, array):
	# function for checking if any value in an array is within min and max
	check = 0
	for i in range(len(array)):
		if array[i] >= minimum and array[i] <= maximum:
			check = 1
	return check


def avg(group):
	# returns average of a list after filtering all non ints / floats
	group = [i for i in group if type(i) != str]
	average = (sum(group)) / len(group)
	return (average)


def distance(x1, y1, x2, y2):
	# Function for finding Euclidean distance between 2 sets of x,y coordiantes
	# using pythagorean theorem

	dx = x2 - x1
	dy = y2 - y1
	dsquared = dx ** 2 + dy ** 2
	totalDistance = dsquared ** 0.5
	return totalDistance


def normalizeToMean(matrix):
	# simple function for normalizing arrays in matrix to their own mean
	normList = []
	for i in range(len(matrix)):
		for n in range(len(matrix[i])):  # Clears all '' found in meal size
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
	maxX = max(array)
	minX = min(array)
	rangeX = maxX - minX
	for i in range(len(array)):
		try:
			normalizedArray.append(((array[i] - minX) / rangeX) * 100)
		except:
			normalizedArray.append("")

	return normalizedArray


def normalizeZeroOne(matrix):
	from scipy import stats
	normList = []
	for i in range(len(matrix)):
		normList.append(list(stats.zscore(matrix[i])))
	return normList


def toExcel(matrix):
	# sends file to excel as .csv with each list as a row, list must be 2D
	directory = os.getcwd()
	outputDataName = input("Name your output file: ")
	outputDataName = directory + "/" + outputDataName + ".csv"

	import csv

	with open(outputDataName, 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerows(matrix)


def toExcelNamed(matrix, name):
	# toExcel where name can be inserted to auto write file without user input
	directory = os.getcwd()
	outputDataName = name
	outputDataName = directory + "/" + outputDataName + ".csv"

	import csv

	with open(outputDataName, 'w', newline='') as f:
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
	print(" 1 hr	= 3600  sec's")
	print(" 3 hr's  = 10800 sec's")
	print(" 4 hr's  = 14400 sec's")
	print(" 6 hr's  = 21600 sec's")


def cutFileName(fileName):
	# function cuts .xxx file type from name and takes only elements up to \ from backend of fileName string
	try:
		fileName = str(fileName)
		fileName = fileName.split(".")[-2]
		fileName = re.findall(r'\w+', fileName)[-1]
		if "\\" in fileName:
			cutFileName = fileName.split("\\")[-1]
		else:
			cutFileName = fileName
	except:
		print("No file type provided")
		cutFileName = input("Name file associations: ")
	print("\nFile associations set to " + cutFileName)
	return cutFileName


import time, sys


##########Status Bar#########
# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
	barLength = 30  # Modify this to change the length of the progress bar
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
	block = int(round(barLength * progress))
	text = "\r[{0}] {1}% {2}".format("=" * block + " " * (barLength - block), round(progress * 100, 1), status)
	sys.stdout.write(text)
	sys.stdout.flush()


def Max2D(data):
	# function for finding max value in 2D matrix or list of lists
	maximum = 0
	for x in range(len(data)):
		try:
			if max(data[x]) > maximum:  # short code for finding max in array of lists
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
			if min(data[x]) < minimum:  # short code for finding max in array of lists
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
	mean = 0
	std = 0

	for number in data:
		mean = mean + number
	mean = mean / float(length)

	for number in data:
		std = std + (number - mean) ** 2
	std = sqrt(std / float(length - 1))

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
		n = len(data) // 2
		return (data[n] + data[n - 1]) / 2
	else:
		return data[len(data) // 2]


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
				pl.plot(time, yValues[x])
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


def getDeltas(inputData, pixPerCM):
	# This function takes a list of lists and returns a new matrix
	# made up of all the delta values for each capillary. These are
	# absolute values between each frame.

	allDeltas = []
	for capillary in inputData:

		deltas = []

		for x in range(1, len(capillary)):
			deltas.append(capillary[x] - capillary[x - 1])
		allDeltas.append(deltas)

	ulConversion = getUnitConversion(pixPerCM)
	return allDeltas, ulConversion


def noiseStats(capillaryDeltas, fly):
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

	oldSize = -1
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

			currSize = len(newNoiseData)
			noiseData = newNoiseData

		except:
			print("Alert: there may be an issue with data from capillary " + str(fly))
			noiseData = copy.deepcopy(capillaryDeltas)
			mean, deviation = meanAndDeviation(noiseData)
			currSize = oldSize

	return meanAndDeviation(noiseData)


def getMealData(deltaMatrix, ulConversion, ORIGINAL_VOL):
	# Given the delta matrix, return a dictionary containing capillary
	# meals. This will be manipulated by users to determine the final
	# meal matrix.

	mealData = {}

	ORIGINAL_VOL = ORIGINAL_VOL * ulConversion

	for i in range(0, len(deltaMatrix)):
		capillary = deltaMatrix[i]
		noiseMean, noiseDeviation = noiseStats(capillary, i)
		meals = dict()

		# Remove average evaporation/noise from each delta.
		for j in range(0, len(capillary)):
			capillary[j] = (capillary[j] - noiseMean)

		# The region below is to adjust meals for nutrient concentration shift from evaporation
		# Note: Adjustment Factor is currently not in use

		priorMeals = []
		for j in range(0, len(capillary)):
			if capillary[j] > (noiseDeviation * FINAL_SD):
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


def outputToExcel(preparedData, feedFileName):
	# Used to output the contents of the meals, applying the conversions
	# to the meal data

	print()
	print("-------------- Excel Output --------------");
	print()
	print("NOTE: Existing files will be overwritten...")
	print()

	collatedName = feedFileName
	directory = os.getcwd()
	collatedName = directory + "/" + collatedName + ".csv"

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

		if maxLength < len(mealData[capillary]):
			maxLength = len(mealData[capillary])

	capillaryIds.sort()

	preparedData  = []
	mealTimes     = []
	mealValues    = []
	mealDurations = []
	mealEndTimes  = []
	boutCounts    = []

	for i in range(0, len(capillaryIds)):

		mealTimesVector     = []
		mealValuesVector    = []
		mealDurationsVector = []
		mealEndsVector      = []
		boutCountsVector    = []

		capillaryMeals = mealData[capillaryIds[i]]
		sortedMeals = []

		for meal in capillaryMeals:
			sortedMeals.append(meal)

		sortedMeals.sort()
		preparedMeals = []

		for j in range(0, len(sortedMeals)):
			if j == len(sortedMeals):
				break
			frameNumber = sortedMeals[j]
			meal = capillaryMeals[frameNumber]
			mealDur = 1  # denotes the length of a meal which is always 1 frame before rolling meals

			# Roll meals that are in adjacent frames into a single meal.
			combineOffset = 1

			while j + 1 < len(sortedMeals):
				if sortedMeals[j] + combineOffset == sortedMeals[j + 1]:
					mealDur = mealDur + 1
					combineOffset = combineOffset + 1
					meal = meal + capillaryMeals[sortedMeals[j + 1]]
					sortedMeals.pop(j + 1)
				else:
					break
			
			mealT = (frameOffset + (frameNumber - 0.5) * intervalOffset)
			mealD = (mealDur * intervalOffset * 3600)
			mealTimesVector.append(mealT)
			mealValuesVector.append(meal / ulConversion)
			mealDurationsVector.append(mealD)
			mealEndsVector.append(mealT+(mealD/3600))
			boutCountsVector.append(1)

			# frameNumber is offset by -1 to compensate for 1 indexed dict format and -.5 for centering within imageing time window
			preparedMeals.append(
				{"frame"   : "{0:5.5f}".format(frameOffset + (frameNumber - 0.5) * intervalOffset),
				 "meal"    : "{0:5.5f}".format(meal / ulConversion),
				 "duration": "{0:5.5f}".format(mealDur * intervalOffset * 3600)})

		while len(preparedMeals) < maxLength:
			preparedMeals.append({"frame": "", "meal": "", "duration": ""})

		mealTimes.append(mealTimesVector)
		mealValues.append(mealValuesVector)
		mealDurations.append(mealDurationsVector)
		mealEndTimes.append(mealEndsVector)
		boutCounts.append(boutCountsVector)

		preparedData.append(preparedMeals)

	return preparedData, mealTimes, mealValues, mealDurations, mealEndTimes, boutCounts


def addCollatedData(file, preparedData):
	# Output the contents of the 'preparedData' in a 'Collated' format to
	# 'file'. The 'collated' contents place each frame next to the meal size
	# that occurred there.

	for i in range(0, len(preparedData)):
		file.write("Capillary {0:d},,, ".format(i + 1))  # .format(i+1) labels capillaries starting at 0+1
		# to get rid of 0 index
	file.write("\n")  # moves filewriter 1 line down

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

def autoCafe(feedData, readsPerSec, pixPerCM, shortFileName):

	try:
		feedFileName = shortFileName + '_feeding'
		frameOffset = zeitStart
		intervalConversion = 1 / (SECS_PER_MIN ** 2 / (feedFrame * readsPerSec))
		deltaMatrix, ulConversion = getDeltas(feedData, pixPerCM)
		mealData = getMealData(deltaMatrix, ulConversion, ORIGINAL_VOL)
		preparedData, mealTimes, mealValues, mealDurations, mealEndTimes, boutCounts = prepareDataMatrix(mealData, ulConversion, frameOffset, intervalConversion)

		write = input('Write raw feeding(AutoCAFE) file to environment?(y/n) ')
		if write == 'y' or write == 'yes'or write == 'YES'or write == 'Yes':
			outputToExcel(preparedData,feedFileName)

		roll = input("Combine feeding bouts within given temporal distance?(y/n): ")

		if roll == 'y' or roll == 'yes' or roll == 'Yes' or roll == 'YES':
			mealValues, mealDurations, mealTimes, boutCounts, mealEndTimes = rollBouts(mealValues, mealDurations, mealTimes, boutCounts, mealEndTimes)


	except Exception as inst:
		print("-------------")
		input(inst)

	return mealTimes, mealValues, mealDurations, boutCounts, mealEndTimes



def combineAutoCAFEMeals(mealTimes, mealValues, mealDurations, shortFileName):
	lines = [["fly", "meal size(ul)", "meal duration(s)", "meal time (ZT)"]]
	for fly in range(len(mealTimes)):
		for meal in range(len(mealTimes[fly])):
			lines.append([fly + 1, mealValues[fly][meal], mealDurations[fly][meal], mealTimes[fly][meal]])
	toExcelNamed(lines, "indiv_meals_" + shortFileName)


# -----------
# Entry Point
# -----------

runNoah()
