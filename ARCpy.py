
#   Copyright (C) 2017 Keith Murphy
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

######## imports #########
import os              
import time
import sys
import threading
import cv2
from os.path import join
import csv

#################
### constants ###
#################

numAnim       = 30   # number of animal and food track windows set

foodTrackX    = 130     # x starting coordinate
foodTrackY    = 9       # y starting coordinate
foodWidth     = 1110     # width of food area
foodHeight    = 280     # heaight of food area

animalTrackX    = 70
animalTrackY    = 364
animalWidth     = 1220
animalHeight    = 329

movingListLength = 60          # length of moving list to work with for identifying meals in realtime
movementThreshold = 0.018       # threshold motion of dye band for triggering stimuli  (lower to increase detection sensitivity and vice versa) 

foodBoxWidth  = int(foodWidth/numAnim)
animalBoxWidth  = int(animalWidth/numAnim)

def main():

    cam = cv2.VideoCapture(0)
    cam.set(3, 1280);
    cam.set(4, 720);

    directory         = os.getcwd()
    outputDataName    = input("Name your output file: ")
    outputDataName    = directory + "/" + outputDataName + ".txt"
    data_file = open(outputDataName, 'a')

    static_x = [0]*numAnim
    static_y = [0]*numAnim  # placeholder for last x and y when animal is not located
    
    sec = getSec()

    ret_val, orig_img = cam.read()
    bg_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY)
    fgbg = cv2.createBackgroundSubtractorMOG2(history = 1000)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

    moveList = movingList(movingListLength, numAnim)
    
    cv2.namedWindow('parameters')
    cv2.createTrackbar('Anim_thresh','parameters',129,255,nothing)
    cv2.createTrackbar('Anim_size','parameters',57,100,nothing)
    cv2.createTrackbar('Dye_thresh','parameters',147,255,nothing)
    cv2.createTrackbar('Dye_size','parameters',50,100,nothing)

    while True:   # will run program until esc is pressed

        newSec = getSec() 
        ret_val, orig_img = cam.read()
        gray_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY) # grab and convert to grayscale

        # This mask creation is only used for animal tracking (adaptive background)
        fgmask = fgbg.apply(gray_img)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        fgmask = cv2.bitwise_not(fgmask)
        fg_img = threshold_img(fgmask,200,255,5)
        cv2.imshow('frame',fg_img)
        
        # get capillary regions and coordinates from pixel size data and animal count provided
        foodStack = []
        for i in range(numAnim):
            foodix = foodTrackX + (i*foodBoxWidth)
            foodStack.append(grabRegion(gray_img,foodTrackY,foodTrackY+foodHeight,foodix,foodBoxWidth))
            cv2.rectangle(gray_img,(foodix,foodTrackY),(foodix+foodBoxWidth,foodTrackY+foodHeight), [0,0,0], 1)                                                   

        foodXFrame = []  #lists for coords to output to data
        foodYFrame = []
        animalXFrame = []
        animalYFrame = []
        
        for i in range(numAnim):
            minFoodThresh = cv2.getTrackbarPos('Dye_thresh','parameters')
            thresh_img = threshold_img(foodStack[i],minFoodThresh,255,3)
            cv2.imshow(str(i)+' foodThresh',thresh_img)
            minDyeSize = cv2.getTrackbarPos('Dye_size','parameters')
            x,y = detectBlobs(thresh_img,minDyeSize)

            if x != -1: 
                x = foodTrackX + (foodBoxWidth*(i)) + x
                y = foodTrackY + y
                cv2.circle(gray_img,(x,y),10, [0,0,0],2)
                static_x[i] = x
                static_y[i] = y

            if x == -1: # shows last known position recorded in static_x and y
                x = static_x[i]
                y = static_y[i] 
                cv2.circle(gray_img,(static_x[i],static_y[i]),10, [0,0,0],2)

            #cv2.rectangle(gray_img,(foodix,foodTrackY),(foodix+foodBoxWidth,foodTrackY+foodHeight), [255,255,0], 3)
            foodXFrame.append(x)
            foodYFrame.append(y)

        # get animal regions and coordinates
        animalStack = []
        #gray_img = 255- (gray_img + bg_img)
        for i in range(numAnim):
            animalix = animalTrackX + i*animalBoxWidth
            animalStack.append(grabRegion(fg_img,animalTrackY,animalTrackY+animalHeight,animalix,animalBoxWidth))
            cv2.rectangle(gray_img,(animalix,animalTrackY),(animalix+animalBoxWidth,animalTrackY+animalHeight), [0,0,0], 1)
        
        for i in range(numAnim):
            minAnimalThresh = cv2.getTrackbarPos('Anim_thresh','parameters')
            thresh_img = threshold_img(animalStack[i],minAnimalThresh,255,5)
            #cv2.imshow(str(i)+' animalThresh',thresh_img)
            minAnimalSize = cv2.getTrackbarPos('Anim_size','parameters')
            x,y = detectBlobs(thresh_img,minAnimalSize)
            if x != -1:
                x = animalTrackX + (animalBoxWidth*(i)) + x
                y = animalTrackY + y
                cv2.circle(gray_img,(x,y),10, [0,0,0],2)
                static_x[i] = x
                static_y[i] = y
                
            if x == -1: # shows last known position recorded in static_x and y
                x = static_x[i]
                y = static_y[i] 
                cv2.circle(gray_img,(static_x[i],static_y[i]),10, [0,0,0],2)
                
            animalXFrame.append(x)
            animalYFrame.append(y)

        cv2.imshow('ARC',gray_img)
        
        if sec != newSec:  # This is basically a 1 second counter to tell the system when to write frame data to your file
 
            animalXYFrame = interleaveXY(animalXFrame,animalYFrame)
            outVector = [sec]+foodYFrame+animalXYFrame
            #print(outVector)
            sec = newSec
            dataToFile = toFileThread(data_file,outVector)
            dataToFile.start()
                     
        if cv2.waitKey(1) == 27: 
            break  # esc to quit

    cv2.destroyAllWindows()


# class and function definitions

def interleaveXY(animalXFrame,animalYFrame):
    xyFrame = []
    for i in range(len(animalXFrame)):
        xyFrame.append(animalXFrame[i])
        xyFrame.append(animalYFrame[i])
    return xyFrame


def nothing(x):
    pass


def makeMovingList(movingListLength,numAnim):
    movAvgPiece= [-1]*numAnim
    yTemp = []
    for i in range(movingListLength):
        yTemp.append(movAvgPiece)
    return yTemp


class toFileThread(threading.Thread):
    def __init__(self, file, vector):
        threading.Thread.__init__(self)
        self.vector = vector
        self.file = file
    def run(self):
        newString = listToTabStrings(self.vector)
        self.file.writelines(newString)


class movingList():
    def __init__(self, listLength, numAnimals):
        self.listLength = listLength
        self.numAnimals = numAnimals
        self.vectorSet = []

        movAvgPiece= [-1]*numAnimals
        for i in range(movingListLength):
            self.vectorSet.append(movAvgPiece)    

    def getLength(self):
        return self.listLength

    def getNumAnimals(self):
        return self.numAnimals

    def addVector(self,vector):
        self.vectorSet.pop(0)
        self.vectorSet.append(vector)

    def getMoveList(self):
        return self.vectorSet
                  
    def isMoving(self,movingAvgLength,thresh):
        if movingAvgLength > self.listLength:
            print('error: moving calculation length is longer than list itself')
            return
        aVectorSet = transpose(self.vectorSet)
        dVectorSet = []
        for vector in range(len(aVectorSet)):
            dVectorSet.append(listToDelta(filterMissReads(aVectorSet[vector])))

        moveBool = []
        for vector in range(len(dVectorSet)):
            try:
##                if vector == 2:
##                    print(avg(dVectorSet[vector][-movingAvgLength:-1]))
                if avg(dVectorSet[vector][-movingAvgLength:-1]) > thresh:
                    moveBool.append(True)
                else:
                    moveBool.append(False)
            except:
                moveBool.append(False)
        return moveBool

                  
def listToDelta(tempList):
    delta = []
    for i in range(1,len(tempList)):
        delta.append(tempList[i]-tempList[i-1])
    return delta


def listToTabStrings(vector):
    newString = ""
    for i in range(len(vector)):
        newString = newString + str(vector[i])+'\t'
    newString = newString +'\n'    
    return newString



def movingCheck(movAvgGroupi,yFramei):

    movAvgGroupi = filterMissReads(movAvgGroupi)
    mean,std = meanAndDeviation(movAvgGroupi)
    try:
        if yFramei > mean + std*5:
            return True
        else:
            return False
    except:
        return False


def filterMissReads(vector):
    vector = [i for i in vector if i != -1]
    return vector


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


def avg (group):
    # returns average of a list after filtering all non ints / floats
    group = [i for i in group if type(i) != str]
    average = (sum(group)) / len(group)
    return(average)  


def getSec():
    t = time.gmtime()
    sec = t.tm_sec + (t.tm_min * 60) + (t.tm_hour * 3600)
    return  sec


def detectBlobs(thresh_img,minSize):
    params = cv2.SimpleBlobDetector_Params()
 
    # Filter by Area.
    params.filterByArea = True
    params.minArea = minSize
    params.maxArea = 1000
 
    # Filter by Circularity
    params.filterByCircularity = False
    params.minCircularity = 0.1
 
    # Filter by Convexity
    params.filterByConvexity = False
    params.minConvexity = 0.1
 
    # Filter by Inertia
    params.filterByInertia = False
    params.minInertiaRatio = 0.05
    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(thresh_img)

    try:
        x = int(keypoints[0].pt[0])
        y = int(keypoints[0].pt[1])
    except:
        x = -1
        y = -1
##    try:
##        print(keypoints[0].size) # returns diameter of object
##    except:
##        pass
        
    return x,y

def threshold_img(img,minThresh,maxThresh,blur):
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img)
    img = cv2.medianBlur(img,blur)
    ret,th3 = cv2.threshold(img,minThresh,maxThresh,cv2.THRESH_BINARY)
    return th3


def grabRegion(img,y,height,x,width):
    img_region = img[y:y+height,x:x+width]
    return img_region

     
def meanAndDeviation(data):
    # Python algorithm to compute mean and standard deviation for a given list.
    # A faster algorithm exists in Knuth's "The Art of Programming", but this
    # will do.
    # Adapted from:
    # http://www.physics.rutgers.edu/~masud/computing/WPark_recipes_in_python.html
    from math import sqrt
    try:
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
    except:
        mean = ""
        std = ""
    return mean, std


main()
