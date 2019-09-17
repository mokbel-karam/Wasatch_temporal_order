# -*- coding: utf-8 -*-
import os
from xml.dom import minidom
from shutil import copyfile
import numpy as np

class Stability:

    def __init__(self,path):
        self.path = path

        with open(path) as file:
            data = np.genfromtxt(file,delimiter=',')
            self.__Reh = list(data[:, 0])
            self.__CFL = list(data[:, 1])
            self.__error=list(data[:, 2])

    def get_Reh(self):
        return self.__Reh

    def get_CFL(self):
        return self.__CFL

    def get_error(self):
        return self.__error



class UPSLuncher:
    def __init__(self,upsFile,tend,timeInteg,suthPath):
        self.upsFile = upsFile
        self.tend = tend
        self.timeInteg = timeInteg
        self.suspath=suthPath

        self.xmldoc = minidom.parse(self.upsFile)
        self.__process_suthpath()
        self.__set_number_of_patches()
        self.__find_resolution()

    def __process_suthpath(self):
        self.suspath = os.path.normpath(self.suspath)
        self.suspath = os.path.abspath(self.suspath)
        print (self.suspath)

    def __create_sus_link(self,folder):
        os.system('ln -fs ' + self.suspath + '/sus '+folder+'/sus')
        os.system('ln -fs ' + self.suspath + '/tools/extractors/lineextract '+ folder+'/lineextract')


# find total number of procs and resolution
    def __set_number_of_patches(self):

        for node in self.xmldoc.getElementsByTagName('patches'):
            P = (str(node.firstChild.data).strip()).split(',')
            P0=int(P[0].split('[')[1])
            P1=int(P[1])
            P2=int(P[2].split(']')[0])
            # node.firstChild.replaceWholeText('[1,1,1]')
        total_proc = P0*P1*P2

    def __find_resolution(self):
        for node in self.xmldoc.getElementsByTagName('resolution'):
            P = (str(node.firstChild.data).strip()).split(',')
            self.Nx=int(P[0].split('[')[1])
            self.Ny=int(P[1])
            self.Nz=int(P[2].split(']')[0])

    def __create_fname(self,CFL,Re):
        fname = os.path.splitext(self.upsFile)[0] + '-CFL' + str(CFL) +'-Re' + str(Re) + '-tend'+str(self.tend)
        return fname
    def __create_logfile_name(self,fname):
        return fname +'.log'

    def __create_uda_name(self,fname):
        return fname +'.uda'
    def __create_newfile_name(self,fname):
         return './' +fname +'/'+ fname +'.ups'

    def __create_new_files(self,fname):
        newfile = self.__create_newfile_name(fname)
        copyfile(self.upsFile, newfile)
        return newfile

    def __creat_file_to_run(self,fname):
        return fname +'.ups'



    def __update_xml(self,fname,dt,mu):
        file = self.__create_newfile_name(fname)
        print ('now updating xml for ', file)
        basename = fname
        xmldoc = minidom.parse(file)
        for node in xmldoc.getElementsByTagName('TimeIntegrator'):
            node.firstChild.replaceWholeText(self.timeInteg)

        for node in xmldoc.getElementsByTagName('filebase'):
            node.firstChild.replaceWholeText(basename + '.uda')

        for node in xmldoc.getElementsByTagName('delt_min'):
            dtmin = dt
            node.firstChild.replaceWholeText(dtmin)

        for node in xmldoc.getElementsByTagName('delt_max'):
            node.firstChild.replaceWholeText(dt)

        for node in xmldoc.getElementsByTagName('maxTime'):
            node.firstChild.replaceWholeText(self.tend)

        for node in xmldoc.getElementsByTagName('BasicExpression'):
            val = node.getElementsByTagName('Constant')[0]
            val.firstChild.replaceWholeText(mu)

        f = open(file, 'w')
        xmldoc.writexml(f)
        f.close()


    def __run_fname(self,fname):
        file = self.__creat_file_to_run(fname)
        udaName = self.__create_uda_name(fname)
        outputName =  self.__create_logfile_name(fname)
        os.environ["SCI_DEBUG"]="ExecOut:+"
        os_return = os.system('cd '+ fname +';'+'./sus' + ' ' + file + ' > '+outputName)
        # os.system('rm ' + newfile)
        os.system('cd '+fname+';'+'rm -f -r *uda* *dot')
        os.system('cd ..')
        return True

    def __single_run(self, CFL, Re,U=2):
        dx = 1.0/self.Nx
        mu = str(U*dx/Re)
        dt = str(CFL*dx/U)
        fname = self.__create_fname(CFL,Re)
        os.system('mkdir '+fname)
        self.__create_sus_link(fname)
        newfile = self.__create_new_files(fname)
        self.__update_xml(fname,dt,mu)
        run = self.__run_fname(fname)

    def run(self,CFL,Re,U=2):
        if type(CFL) == list and type(Re)==list:
            for cfl, re in zip(CFL,Re):
                self.__single_run(cfl,re,U)

        else:
            self.__single_run(CFL,Re,U)


import argparse
from generate_execTimes.RunningAtStability import *

parser = argparse.ArgumentParser(description=
                                 'Computes stability boundary '+
                                 ' The cleanest way to operate this script is to make a copy of it in a new directory. Then '+
                                 'copy the ups file to that directory and execute the script.' )

parser.add_argument('-ups',
                    help='The input file to run.',required=True)

parser.add_argument('-suspath',
                    help='The path to sus.',required=False)

parser.add_argument('-stability',
                    help='The path of the file that contain stability boundary.',type=str,required=True)

parser.add_argument('-tend',
                    help='end time of the simulation.',type=float, required=True)

parser.add_argument('-integ',
                    help='Time integrator (FE, RK2SSP, or RK3SSP).', required=True)

args = parser.parse_args()

results = Stability(args.stability)

myLuncher = UPSLuncher(args.ups,args.tend,args.integ,args.suspath)

myLuncher.run(results.get_CFL(),results.get_Reh())