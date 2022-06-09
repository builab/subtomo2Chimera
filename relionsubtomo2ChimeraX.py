#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.1
Created on Sat Dec  4 22:56:14 2021

Script to convert Relion 4.0 star file to visualization script in Chimera/ChimeraX
Need to install eulerangles, starfile (pip install eulerangles, pip install starfile)
Need to adjust level after in the chimera script
2022/05/05 Add stl compatible script
2022/06/09 Reset dataframe index to take care of star file not sorted by rlnTomoName or rlnMicrographName
Usage: relionsubtomo2ChimeraX.py --i run_data.star --o load_chimera.cmd --avgAngpix 10.48 --avgBoxSize "64,64,64" --tomoname CTEM_tomo1
@author: Huy Bui, McGill University
"""


import numpy as np
import starfile
import argparse

from eulerangles import euler2matrix

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Convert Relion 4.0 subtomo star to ChimeraX session')
	parser.add_argument('--i', help='Input star file',required=True)
	parser.add_argument('--o', help='Output Chimera Script',required=True)
	parser.add_argument('--avgAngpix', help='Pixel size of average',required=True)
	parser.add_argument('--avgBoxSize', help='Box size of average',required=True)
	parser.add_argument('--tomoname', help='Tomo Name',required=True)
	parser.add_argument('--avgFilename', help='Avg subtomo filename',required=False, default='avg.mrc')
	parser.add_argument('--level', help='Level of subtomo avg',required=False, default=0.0039)
	parser.add_argument('--offset', help='Offset of volume number',required=False, default=0)
	parser.add_argument('--relion31', help='Star file from Relion 3.1 (1 or 0)',required=False, default=0)
	
	args = parser.parse_args()
	
	outfile = args.o
	TomoName = args.tomoname
	
	level= float(args.level)
	avgAngpix = float(args.avgAngpix)
	boxSize = [float(x) for x in args.avgBoxSize.split(",")]

	# Loading Relion 4.0 star file
	stardict = starfile.read(args.i)
	
	df_optics = stardict['optics']	
	
	df = stardict['particles']
	# Relion 4.0 or 3.1
	if args.relion31 == 0:
		angpix = df_optics.loc[0, 'rlnTomoTiltSeriesPixelSize']	
		dftomo = df[df.rlnTomoName == TomoName].copy()
	else:
		angpix = df_optics.loc[0, 'rlnImagePixelSize']
		dftomo = df[df.rlnMicrographName == TomoName].copy()
	
	# added by v0.1
	dftomo.reset_index(drop=True, inplace=True)
	       
	nosubtomo = len(dftomo)
	
	# Offset to load in case many different object. Not use now
	offset = int(args.offset)	
	out = open(outfile, 'w')
	
	# (N-1)/2 later
	radiusAngst = (np.array(boxSize)-1)/2*avgAngpix
	
	for i in range(len(dftomo)):
		out.write('open {:s}\n'.format(args.avgFilename))
	
	if args.avgFilename.endswith('.mrc'):
		out.write('\nvolume #{:d}-{:d} step 1 level {:f}\n\n'.format(offset + 1, offset + len(dftomo), level))
		
	index_offset = dftomo.index[0]	
	for i in range(len(dftomo)):
		eulers_relion = dftomo.loc[index_offset+i, ['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].tolist()
		rotm = euler2matrix(eulers_relion, axes='zyz', intrinsic=True, right_handed_rotation=True)

		# Tranpose the matrix due to z view in Chimera
		rotm = rotm.transpose()
		origin = dftomo.loc[index_offset+i, ['rlnCoordinateX', 'rlnCoordinateY', 'rlnCoordinateZ']].to_numpy()
		shiftAngst = dftomo.loc[index_offset+i, ['rlnOriginXAngst', 'rlnOriginYAngst', 'rlnOriginZAngst']].to_numpy()
		originAngst = origin*angpix - shiftAngst
		t1 = np.matmul(rotm, -radiusAngst.transpose())
		adjOriginAngst = originAngst + t1
		out.write('view matrix mod #{:d},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n'.format(i + offset + 1, rotm[0,0], rotm[0,1], rotm[0,2], adjOriginAngst[0], rotm[1,0], rotm[1,1], rotm[1,2], adjOriginAngst[1], rotm[2,0], rotm[2,1], rotm[2,2], adjOriginAngst[2]))
		
	out.write('\nview orient\n')
	
	out.close()

	

