import subprocess as sp
import os

class DirStruct:
    count = 0
    __instance=None
    def __init__(self,levels,vars,suthpath,nsteps,extension='ups'):
        if DirStruct.__instance==None:
            self.extension= extension
            self.levels = levels
            self.nsteps = nsteps
            self.vars = vars
            self.suthPath = suthpath
            self.cwd = self.CWD()
            self.__generates_names()
            # for later create a class for structure that allows addition of folders, files ...
            #self.struct={self.CWD().split('/')[-1]:{'absPath':self.CWD(),'relPath':'.','dirs':{},'files':{}}}
            DirStruct.count+=1
            DirStruct.__instance=self
        else:
            return DirStruct.getInstance()

    @staticmethod
    def getInstance():
        if DirStruct.__instance!=None:
            return DirStruct.__instance
        else:
            raise Exception("This class is not instantiated!")

    def CWD(self):
        cwdProcess = sp.run(['pwd'], stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)
        return cwdProcess.stdout

    def command (self,fileName):
        return  "python2.7 compute-temporal-order.py -ups {} -levels {} -nsteps {} -vars {} -suspath {}".format(fileName, self.levels, self.nsteps, self.vars, self.suthPath)

    def __generates_names(self):
        try:
            findFileNamesProcess = sp.run(['find *.'+self.extension], stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True, shell=True)
            self.fileNames = findFileNamesProcess.stdout.split('\n')[:-1]
            self.folders = [filename.split('.')[0] for filename in self.fileNames]
            self.filesDict ={}
        except:
            print('An error occured while generating the files and folders names.')
            print('make sure that this type "{}" of files exists in the current working directory!')
            return False

    def prepare_directories(self):
        for folder,file in zip(self.folders,self.fileNames):
            self.filesDict[folder]=file
        createFoldersCommand = ['mkdir']
        for folder in self.folders:
            createFoldersCommand.append(folder)
        try:
            mkdir = sp.run(createFoldersCommand, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)
            print(self.filesDict)
            for folder in self.filesDict.keys():
                os.system('cp $PWD/compute-temporal-order.py $PWD/{}'.format(folder))
                os.system('cp $PWD/{} $PWD/{}'.format(self.filesDict[folder],folder))

            for folder in self.filesDict.keys():
                # os.system('rm $PWD/{}/run.sh'.format(folder))
                os.system("echo '#!/usr/bin/bash' > $PWD/{}/run.sh".format(folder))
                os.system("echo {} >> $PWD/{}/run.sh".format(self.command(self.filesDict[folder]),folder))
                os.system("chmod +x $PWD/{}/run.sh".format(folder))
        except:
            print("An error occured while generatiing directories and prepating the scripts to run")
            return False

        return True
