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
        os.system('ln -fs ' + self.suspath + '/sus sus')
        os.system('ln -fs ' + self.suspath + '/tools/extractors/lineextract lineextract')


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

    def __create_new_files(self,CFL,Re):
        fname = os.path.splitext(self.upsFile)[0] + '-CFL' + str(CFL) +'-Re' + str(Re) + '-tend'+str(self.tend)+ '.ups'
        copyfile(self.upsFile, fname)
        return fname



    def __update_xml(self,fname,dt,mu):
        print ('now updating xml for ', fname)
        basename = os.path.splitext(fname)[0]
        xmldoc = minidom.parse(fname)
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

        f = open(fname, 'w')
        xmldoc.writexml(f)
        f.close()


    def __run_fname(self,fname):
        udaName = os.path.splitext(fname)[0] + '.uda'
        outputName = os.path.splitext(fname)[0] + '.log'
        os.environ["SCI_DEBUG"]="ExecOut:+"
        os_return = os.system('./sus' + ' ' + fname + ' > '+outputName)
        os.system('rm ' + fname)
        os.system('rm -f -r *uda* *dot')
        return True

    def __single_run(self, CFL, Re,U=2):
        dx = 1.0/self.Nx
        mu = str(U*dx/Re)
        dt = str(CFL*dx/U)
        fname = self.__create_new_files(CFL,Re)
        self.__update_xml(fname,dt,mu)

        run = self.__run_fname(fname)

    def run(self,CFL,Re,U=2):
        if type(CFL) == list and type(Re)==list:
            for cfl, re in zip(CFL,Re):
                self.__single_run(cfl,re,U)

        else:
            self.__single_run(CFL,Re,U)
