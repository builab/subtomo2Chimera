#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 22:56:14 2021

Script to convert star file to visualization script in Chimera/ChimeraX
Need to install eulerangles, starfile (pip install eulerangles, pip install starfile)
Need to adjust level after in the chimera script
Usage: relionsubtomo2ChimeraX.py --i run_data.star --o load_chimera.cmd --avgAngpix 10.48 --avgBoxSize "64,64,64" --tomoname CTEM_tomo1
@author: Huy Bui, McGill University
"""


import numpy as np
import starfile
import argparse

from eulerangles import euler2matrix

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Convert relion4.0 subtomo star to Chimera session')
	parser.add_argument('--i', help='Input star file',required=True)
	parser.add_argument('--o', help='Output Chimera Script',required=True)
	parser.add_argument('--avgAngpix', help='Pixel size of average',required=True)
	parser.add_argument('--avgBoxSize', help='Box size of average',required=True)
	parser.add_argument('--tomoname', help='Tomo Name',required=True)
	parser.add_argument('--avgFilename', help='Avg subtomo filename',required=False, default='avg.mrc')
	parser.add_argument('--offset', help='Offset of volume number',required=False, default=0)

	
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
	
	# Offset to load in case many different object. Not use now
	offset = int(args.offset)	
	out = open(outfile, 'w')
	
	# (N-1)/2 later
	radiusAngst = (np.array(boxSize)-1)/2*avgAngpix
	
	for i in range(len(dftomo)):
		out.write('open {:s}\n'.format(args.avgFilename))
	
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

	

