#!/usr/bin/env python3

import argparse
import multiprocessing
from prepare_directory import *
from upsObject import *
import pickle
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
                    help='The relative path to sus.',default='.')

parser.add_argument('-vars', default='x-mom',
                    help='Comma seperated list of variables for which the temporal order is to be computed. example: -vars "var1, my var".')

parser.add_argument('-title', required=True,
                    help='title of the output object file')

args = parser.parse_args()


dirStruct = DirStruct(args.levels,args.vars,args.suspath,args.nsteps,extension='ups')
dirStruct.prepare_directories()


def worker(folder):
    os.system('cd {} ; setsid ./run.sh  2>&1 log.out ; cd ..'.format(folder))
    return

jobs = []

for num, folder in enumerate(dirStruct.filesDict.keys()):
    p = multiprocessing.Process(target=worker, args=(folder,))
    jobs.append(p)
    p.start()

for job in jobs:
    job.join()

filenames = [folder+".txt" for folder in dirStruct.filesDict.keys()]
with open('./{}.obj'.format(args.title),'wb') as file:
    pickle.dump(UPSGroup(filenames),file)

sep = ' '
command = sep.join(filenames)
os.system("rm {}".format(command))