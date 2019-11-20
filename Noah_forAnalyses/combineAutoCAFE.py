import os

input_dir = input("Drag the directory containing the autoCAFE files you want combined ")
input_dir = input_dir+"\\"

firstRow=[]

for filename in os.listdir(input_dir):
	if (filename.find("feeding")==-1):
		pass
	else:
		path=input_dir+str(filename)

		with open(path) as rFile:

			if (len(firstRow)==0):
				firstRow=rFile.readline().split(',')[:-1]
				numCols=len(firstRow)
				numFlies=int(numCols/3)
				meals=[[] for _ in range(numFlies)]
				mealTimes=[[] for _ in range(numFlies)]
				mealDurs=[[] for _ in range(numFlies)]
			else:
				rFile.readline()

			for line in rFile:
				line=list(line.split(','))[:-1]
				for i in range (0,numFlies):
					if (line[i*3]==''):
						pass
					else:
						mealTimes[i].append(line[i*3])
						meals[i].append(line[i*3+1])
						mealDurs[i].append(line[i*3+2])

maxLength=0
for fly in range (numFlies):
	listLength=len(meals[fly])
	if (listLength>maxLength):
		maxLength=listLength

wFile=open(input_dir+"combinedCAFE.csv","w")
wFile.write(','.join(firstRow)+',\n')

for line in range(maxLength):
	tempLine=""
	for fly in range(numFlies):
		if (line>=len(meals[fly])):
			tempLine=tempLine+",,,"
		else:
			tempLine=tempLine+str(mealTimes[fly][line])+","
			tempLine=tempLine+str(meals[fly][line])+","
			tempLine=tempLine+str(mealDurs[fly][line])+","
	tempLine=tempLine+'\n'
	wFile.write(tempLine)

wFile.close()
print("done")