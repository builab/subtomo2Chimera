#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 22:56:14 2021
Modification of relionsubtomo2ChimeraX.py for Dynamo table
Usage: python subtomo2Chimera/dynamotable2ChimeraX.py --tomoDoc tomograms.doc --i CU428_TS013_1/aligned.tbl --o test_013_old.cxc --avgAngpix 8.48 --tomoAngpix 8.48 --avgBoxSize "128,128,15" --tomoname CU428_TS013_rec.mrc
@author: Huy Bui, McGill University
"""

import numpy as np
import starfile
import argparse
import dynamotable

from eulerangles import euler2matrix

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Convert Dynamo table to ChimeraX session')
	parser.add_argument('--i', help='Input table file',required=True)
	parser.add_argument('--tomoDoc', help='Input tomo doc file',required=True)
	parser.add_argument('--o', help='Output ChimeraX Script',required=True)
	parser.add_argument('--avgAngpix', help='Pixel size of average used for display',required=True)
	parser.add_argument('--tomoAngpix', help='Pixel size of tomo in table',required=True)
	parser.add_argument('--avgBoxSize', help='Box size of average',required=True)
	parser.add_argument('--tomoname', help='Tomo Name',required=True)
	parser.add_argument('--avgFilename', help='Avg subtomo filename (mrc or stl format)',required=False, default='avg.mrc')
	parser.add_argument('--level', help='Level of subtomo avg',required=False, default=0.0039)
	parser.add_argument('--offset', help='Offset of volume number',required=False, default=0)


	args = parser.parse_args()
	
	outfile = args.o
	TomoName = args.tomoname
	
	level= float(args.level)
	avgAngpix = float(args.avgAngpix)
	boxSize = [float(x) for x in args.avgBoxSize.split(",")]
	angpix = float(args.tomoAngpix)

	# Loading table
	df = dynamotable.read(args.i, args.tomoDoc)
	#print(df)
	dftomo = df[df.tomo_file == TomoName].copy()
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
		eulers_dynamo = dftomo.loc[index_offset+i, ['tdrot', 'tilt', 'narot']].tolist()
		rotm = euler2matrix(eulers_dynamo, axes='zxz', intrinsic=False, right_handed_rotation=True)

		# Transpose the matrix due to z view in Chimera
		rotm = rotm.transpose()
		origin = dftomo.loc[index_offset+i, ['x', 'y', 'z']].to_numpy()
		shiftAngst = dftomo.loc[index_offset+i, ['dx', 'dy', 'dz']].to_numpy()*angpix
		originAngst = origin*angpix + shiftAngst
		t1 = np.matmul(rotm, -radiusAngst.transpose())
		adjOriginAngst = originAngst + t1
		out.write('view matrix mod #{:d},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n'.format(i + offset + 1, rotm[0,0], rotm[0,1], rotm[0,2], adjOriginAngst[0], rotm[1,0], rotm[1,1], rotm[1,2], adjOriginAngst[1], rotm[2,0], rotm[2,1], rotm[2,2], adjOriginAngst[2]))
		
	out.write('\nview orient\n')
	
	out.close()

	

