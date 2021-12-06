#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 22:56:14 2021

Script to convert star file to visualization script in Chimera/ChimeraX
Need to install eulerangles, starfile (pip install eulerangles, pip install starfile)
Need to adjust level after in the chimera script
Note work very well yet in aligning with tomogram
Usage: relionsubtomo2Chimera.py --i run_data.star --o load_chimera.cmd --avgAngpix 10.48 --avgBoxSize "64,64,64" --tomoname CTEM_tomo1
@author: kbui2
"""


import pandas as pd
import numpy as np
import starfile
import argparse, os

from eulerangles import euler2euler


if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Convert relion4.0 subtomo star to Chimera session')
	parser.add_argument('--i', help='Input star file',required=True)
	parser.add_argument('--o', help='Output Chimera Script',required=True)
	parser.add_argument('--avgAngpix', help='Pixel size of average',required=True)
	parser.add_argument('--avgBoxSize', help='Box size of average',required=True)
	parser.add_argument('--tomoname', help='Tomo Name',required=True)
	
	args = parser.parse_args()
	
	outfile = args.o
	TomoName = args.tomoname
	
	level= 0.0039
	avgAngpix = float(args.avgAngpix)
	boxSize = [float(x) for x in args.avgBoxSize.split(",")]

	stardict = starfile.read(args.i)
	
	df_optics = stardict['optics']	
	angpix = df_optics.loc[0, 'rlnTomoTiltSeriesPixelSize']	
	
	df = stardict['particles']
	dftomo = df[df.rlnTomoName == TomoName].copy()
	nosubtomo = len(dftomo)
	
	# Offset to load in case many different object
	offset = 0
	
	out = open(outfile, 'w')
	
	radiusAngst = np.array(boxSize)*avgAngpix/2
	
	for i in range(len(dftomo)):
		out.write('open avg.mrc\n')
		out.write('volume #{:d} step 1 level {:f}\n'.format(i, level))
		
	out.write('\nturn x 180 1; wait;\n\n')

		
	for i in range(len(dftomo)):
		eulers_relion = dftomo.loc[i, ['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].tolist()
		out.write('roll z {:.2f} 1 models #{:d}; wait;\n'.format(eulers_relion[0], i))
		out.write('roll y {:.2f} 1 models #{:d}; wait;\n'.format(eulers_relion[1], i))
		out.write('roll z {:.2f} 1 models #{:d}; wait;\n\n'.format(eulers_relion[2], i))
		
	out.write('\nturn x 180 1; wait;\n')
	
		
	for i in range(len(dftomo)):
		origin = dftomo.loc[i, ['rlnCoordinateX', 'rlnCoordinateY', 'rlnCoordinateZ']].to_numpy()
		shiftAngst = dftomo.loc[i, ['rlnOriginXAngst', 'rlnOriginYAngst', 'rlnOriginZAngst']].to_numpy()
		originAngst = origin*angpix - shiftAngst - radiusAngst	
		out.write('move x {:.2f} 1 models #{:d}; wait;\n'.format(originAngst[0], i))
		out.write('move y {:.2f} 1 models #{:d}; wait;\n'.format(originAngst[1], i))
		out.write('move z {:.2f} 1 models #{:d}; wait;\n'.format(originAngst[2], i))

		
	out.write('center #0')
	out.close()

	

