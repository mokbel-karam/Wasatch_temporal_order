import numpy as np

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

    def __init__(self, stdoutfile):
        self.stdoutfile=stdoutfile
        self.WallTimePerStep = []
        self.__WallTimePSolve = []
        self.WallTimePSolveTimestep = []
        self.WallTimePSolveStage = []
        self.timesteps=0
        self.__stgCounter = StageCounter()

    def parse(self, startStep=0,endStep=None):
        with open(self.stdoutfile) as fp:
            line = fp.readline()
            count = 1
            while line:
                currentLine = line.strip()

                self.__parse_timestep(currentLine,startStep,endStep)
                self.__parse_pressure(currentLine,startStep,endStep)

                line = fp.readline()
                count+=1


    def __parse_timestep(self,currentLine, startStep,endStep):
        if self.__exists('Timestep',currentLine):
            firstSplit= currentLine.split("       ")
            time = self.__search_for_word('EMA',firstSplit[-1].split(' '))
            timeVAl = float(time.split('=')[1])
            if (self.timesteps>startStep) and (endStep==None or self.timesteps<=endStep):
                self.WallTimePerStep.append(timeVAl)
                self.__stgCounter.reinitialize()
                self.WallTimePSolveStage.append(self.__WallTimePSolve)
                self.WallTimePSolveTimestep.append(self.__psolve_timestep())
                self.__WallTimePSolve=[]

            self.timesteps+=1

    def __parse_pressure(self,currentLine, startStep,endStep):
        if self.__exists('Solve ',currentLine):
            if (self.timesteps>startStep) and (endStep==None or self.timesteps<=endStep):
                firstSplit= currentLine.split(" ")
                psolveTime = float(firstSplit[8])
                self.__stgCounter.increment()
                self.__WallTimePSolve.append(psolveTime)

    def __psolve_timestep(self):
        return sum(self.__WallTimePSolve)


    def __exists(self,word,string):
        return True if string.find(word) >=0 else False

    def __search_for_word(self,word,list):
        for item in list:
            if self.__exists(word,item):
                return item
        return False

    def total_time(self):
        return sum(self.WallTimePerStep)

    def total_psolve_time(self):
        return sum(self.WallTimePSolveTimestep)

    def total_num_psolve(self):
        return self.__stgCounter.totalCount

    def portion_of_psolve_per_timestep(self):
        return np.average(np.array(self.WallTimePSolveTimestep)/np.array(self.WallTimePerStep))


# #Exmaple:
# #=========
# fileName='log.out'
#
# myparser=Parser(fileName)
# myparser.parse(5)
#
# print(myparser.total_time())
# print(myparser.total_psolve_time())
# print(myparser.total_num_psolve())
# print(myparser.portion_of_psolve_per_timestep())
