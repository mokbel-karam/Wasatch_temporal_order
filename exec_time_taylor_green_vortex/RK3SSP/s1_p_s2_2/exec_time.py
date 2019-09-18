import json
import os


class StageCounter:
    def __init__(self):
        self.totalCount=0
        self.count=0
        self.psolvePreStep=None
    def increment(self):
        self.count +=1
        self.totalCount +=1

    def reinitialize(self):
        self.psolvePreStep=self.count if self.psolvePreStep ==None else self.psolvePreStep
        self.count = 0


    def total_number_psolve(self):
        return self.totalCount

    def number_psolve_per_timestep(self):
        return self.psolvePreStep

class Parser:

    def __init__(self ):
        self.totalTime=[]
        self.totalPsolveTime=[]
        self.totalPsolve =[]
        self.totalIterations = []
    def parse(self, stdoutfile, startStep=0,endStep=None):
        stdoutfile=stdoutfile
        WallTimePerStep = []
        WallTimePSolve = []
        WallTimePSolveTimestep = []
        WallTimePSolveStage = []
        iterationsTimestep = []
        iterations = []
        timesteps=0
        stgCounter = StageCounter()
        with open(stdoutfile) as fp:
            line = fp.readline()
            count = 1
            while line:
                currentLine = line.strip()
                bad=False

                if self.__exists('Timestep',currentLine):
                    firstSplit= currentLine.strip().split(' ')
                    time = [i for i in firstSplit if i]
                    print(time)
                    try:
                        timeVAl = float(time[7].split('=')[1])
                    except:
                        bad = True
                    if ((timesteps>startStep) and (endStep==None or timesteps<=endStep))or not bad:
                        WallTimePerStep.append(timeVAl)
                        stgCounter.reinitialize()
                        WallTimePSolveStage.append(WallTimePSolve)
                        WallTimePSolveTimestep.append(sum(WallTimePSolve))
                        WallTimePSolve=[]
                        iterations.append(sum(iterationsTimestep))
                        iterationsTimestep=[]

                    timesteps+=1

                if self.__exists('Solve ',currentLine):
                    if (timesteps>startStep) and (endStep==None or timesteps<=endStep):
                        firstSplit= currentLine.split(" ")
                        psolveTime = float(firstSplit[8])
                        print(firstSplit)
                        try:
                            iteration = float(firstSplit[17])
                        except:
                            iteration = float(firstSplit[14])
                        iterationsTimestep.append(iteration)
                        stgCounter.increment()
                        WallTimePSolve.append(psolveTime)

                line = fp.readline()
                count+=1
            self.totalTime.append(sum(WallTimePerStep))
            self.totalPsolveTime.append(sum(WallTimePSolveTimestep))
            self.totalPsolve.append(stgCounter.totalCount)
            self.totalIterations.append(sum(iterations))

    def __exists(self,word,string):
        return True if string.find(word) >=0 else False

    def __search_for_word(self,word,list):
        for item in list:
            if self.__exists(word,item):
                return item
        return False

    def total_time(self):
        return self.totalTime

    def total_psolve_time(self):
        return self.totalPsolveTime

    def total_num_psolve(self):
        return self.totalPsolve

    def total_num_iterations(self):
        return self.totalIterations


class SummaryParser:
    def __init__(self,stdoutfile):
        self.stdoutfile=stdoutfile
        self.taskCount = 0
        self.data={}
    def parse(self):
        caseData={}
        with open(self.stdoutfile, 'rb') as fp:
            line = fp.readline()
            count = 1
            while line:
                currentLine = line.strip()

                self.__parse_total(currentLine)
                self.__parse_task(currentLine,caseData)

                line = fp.readline()
                count+=1
        return caseData
    def __parse_task(self,currentLine,dict):
        if self.__exists('Task',currentLine):
            if (self.taskCount!=0):
                firstSplit= currentLine.split("|")
                taskName = firstSplit[0].strip()
                print(firstSplit)
                averageTime = float(firstSplit[1].strip())
                maxTime = float(firstSplit[2].strip())
                dict[taskName]=(averageTime,maxTime)

            self.taskCount+=1

    def __parse_total(self,currentLine):
        if self.__exists('Total',currentLine):
            firstSplit=currentLine.split("=")
            val = float(firstSplit[1].strip())
            self.totalTime=val

    def __exists(self,word,string):
        return True if string.find(word) >=0 else False


myparser = Parser()

d = '.'
directories=[os.path.join(d, o) for o in os.listdir(d)
 if os.path.isdir(os.path.join(d,o))]


path = '.'

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.log' in file:
            files.append(os.path.join(r, file))

print(files)

Res = []
for path in files:
    Res.append(float(path.split('-')[2][2:]))
    myparser.parse(path)

timeDict={}
psolvetimeDict={}
totalpsolveDict={}
totaliterationsDict={}
for Re,totaltime,totalpsolvetime,totalpsolve, totaliterations in zip(Res,myparser.totalTime,myparser.totalPsolveTime,myparser.totalPsolve, myparser.totalIterations):
    timeDict[Re] = totaltime
    psolvetimeDict[Re]=totalpsolvetime
    totalpsolveDict[Re] =totalpsolve
    totaliterationsDict[Re]=totaliterations

sortedtimeDict={}
sortedpsolvetimeDict={}
sortedtotalpsolveDict={}
sortedtotaliterationsDict={}
for Re in sorted(Res):
    sortedtimeDict[Re]=timeDict[Re]
    sortedpsolvetimeDict[Re]=psolvetimeDict[Re]
    sortedtotalpsolveDict[Re]=totalpsolveDict[Re]
    sortedtotaliterationsDict[Re]=totaliterationsDict[Re]

sortedDict = {'totalTime':list(sortedtimeDict.values()),'totalPsolveTime':list(sortedpsolvetimeDict.values()),'totalPsolve':list(sortedtotalpsolveDict.values()),'totalIterations':list(sortedtotaliterationsDict.values()),'Res':sorted(Res)}
print(sortedDict)

# dict= {'totalTime':myparser.totalTime,'totalPsolveTime':myparser.totalPsolveTime,'totalPsolve':myparser.totalPsolve,'Res':Res}

with open('./execTimesRK3proj_new.json','w') as file:
    json.dump(sortedDict,file,indent=4)
