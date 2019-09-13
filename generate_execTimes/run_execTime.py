
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