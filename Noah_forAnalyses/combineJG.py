import os

input_dir = input("Drag the directory containing the javagrinder output files you want combined ")
input_dir = input_dir+"\\"

numFiles = len(os.listdir(input_dir))
fileN = 0
numFlies = 30
numCols = numFlies * 3 + 1
hrs = 24

cut = input("Cut data to 24 hours? (y/n): ")
if ((cut.lower()).find("y")==-1):
	pass
else:
	totLines = hrs * 3600

totFiles = len(os.listdir(input_dir))
totFlies = 30 * totFiles 

foodY = [[] for _ in range(totFlies)]
flyX  = [[] for _ in range(totFlies)]
flyY  = [[] for _ in range(totFlies)]
timestamp = []


for filename in os.listdir(input_dir):

	print(filename)

	if fileN == 0:
		outputName = str(filename.split('_')[0])

	path=input_dir+str(filename)

	with open(path) as rFile:
		
		lineN = 0

		for line in rFile:

			try:

				lineList = line.split('\t')
				lineList[-1] = lineList[-1].split('\n')[0]
				
				if len(lineList) > numCols:
					lineList = lineList[len(lineList)-numCols:]

				if fileN == 0:
					timestamp.append(lineList[0])

				for c in range (0, numFlies):
					flyN = (fileN*numFlies)+c
					foodY[flyN].append(lineList[c+1])
					flyX[flyN].append(lineList[numFlies+(c*2)+1])
					flyY[flyN].append(lineList[numFlies+(c*2)+1+1])

				lineN = lineN + 1

				if totLines:
					if lineN >= totLines:
						break
			
			except:
				pass

		# for line in rFile:

		# 	if lineN < (totLines):

		# 		lineList = line.split('\t')
		# 		lineList[-1] = lineList[-1].split('\n')[0]
				
		# 		if len(lineList) > numCols:
		# 			lineList = lineList[len(lineList)-numCols:]

		# 		if fileN == 0:
		# 			timestamp.append(lineList[0])

		# 		for c in range (0, numFlies):
		# 			flyN = (fileN*numFlies)+c
		# 			foodY[flyN].append(lineList[c+1])
		# 			flyX[flyN].append(lineList[numFlies+(c*2)+1])
		# 			flyY[flyN].append(lineList[numFlies+(c*2)+1+1])

		# 		lineN = lineN + 1
			
		# 	else:
		# 		pass

		# for line in rFile:

		# 	lineList = line.split('\t')
		# 	lineList[-1] = lineList[-1].split('\n')[0]
			
		# 	if len(lineList) > numCols:
		# 		lineList = lineList[len(lineList)-numCols:]

		# 	if fileN == 0:
		# 		timestamp.append(lineList[0])

		# 	for c in range (0, numFlies):
		# 		flyN = (fileN*numFlies)+c
		# 		foodY[flyN].append(lineList[c+1])
		# 		flyX[flyN].append(lineList[numFlies+(c*2)+1])
		# 		flyY[flyN].append(lineList[numFlies+(c*2)+1+1])
		


	fileN = fileN + 1

wFile = open(input_dir+outputName+".txt","w")

#for line in range(totLines):
for line in range(len(foodY[0])):
	tempLine = str(timestamp[line])
	for fly in range(totFlies):
		try:
			tempLine=tempLine+'\t'+str(foodY[fly][line])
		except:
			tempLine=tempLine+'\t'+'-1'
	for fly in range (totFlies):
		try:
			tempLine = tempLine+'\t'+str(flyX[fly][line])+'\t'+str(flyY[fly][line])
		except:
			tempLine = tempLine+'\t'+'-1'+'\t'+'-1'
	wFile.write(tempLine+'\n')

wFile.close()
print("done")