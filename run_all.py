#!/usr/bin/env python3

import argparse
import multiprocessing
from prepare_directory import *
import subprocess as sp


parser = argparse.ArgumentParser(description=
                                 'Computes temporal order of accuracy without the need of an anlytical solution. The method '+
                                 'is based on computing numerical solutions at refined timesteps and then computing the '+
                                 'order as p = ln[(f3 - f2)/(f2 - f1)]/ln(0.5).' +
                                 ' The cleanest way to operate this script is to clone it in a new directory. Then '+
                                 'copy all the ups files that you want to test to that directory and execute the script.' )

parser.add_argument('-levels',
                    help='The number of time refinement levels.', type=int, default=5)

parser.add_argument('-nsteps',
                    help='The number of timesteps. Defaults to 10.', type=int, default=10)

parser.add_argument('-suspath',
                    help='The path to sus.',default='.') #required=True

parser.add_argument('-vars', default='asdfadfa',
                    help='Comma seperated list of variables for which the temporal order is to be computed. example: -vars "var1, my var".')

args = parser.parse_args()


dirStruct = DirStruct(args.levels,args.vars,args.suspath,args.nsteps,extension='ups')
dirStruct.prepare_directories()


def Command(folder):
    return "$PWD/{}/run.sh".format(folder)

def worker(command):
    sp.call([command],shell=True)
    return

jobs = []

for num, folder in enumerate(dirStruct.filesDict.keys()):

    process = multiprocessing.Process(target=worker,args=(Command(folder),))
    jobs.append(process)
    process.start()
