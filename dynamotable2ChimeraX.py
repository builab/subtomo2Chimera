#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.3
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

import numpy as np
from eulerangles import euler2matrix


def write_cxc_file(output_filename, dftomo, avg_filename, avg_angpix, box_size, level, offset, tomo_angpix):
    """
    Writes a ChimeraX `.cxc` script for the given Dynamo table data. Not similar to the one for Relion star file.
    """
    radius_angst = (np.array(box_size) - 1) / 2 * avg_angpix

    with open(output_filename, 'w') as out:
        # Open all subtomo averages
        out.write('open ')
        for _ in range(len(dftomo)):
            out.write(f' {avg_filename}')
        out.write('\n\n')

        # Set volume level if .mrc is used
        if avg_filename.endswith('.mrc'):
            out.write(f'\nvolume #{offset + 1} step 1 level {level:.6f}\n\n')

        # Write transformation matrices for each subtomogram
        index_offset = dftomo.index[0]
        for i in range(len(dftomo)):
            eulers_dynamo = dftomo.loc[index_offset + i, ['tdrot', 'tilt', 'narot']].tolist()
            rotm = euler2matrix(eulers_dynamo, axes='zxz', intrinsic=False, right_handed_rotation=True).transpose()
            origin = dftomo.loc[index_offset + i, ['x', 'y', 'z']].to_numpy()
            shift_angst = dftomo.loc[index_offset + i, ['dx', 'dy', 'dz']].to_numpy() * tomo_angpix
            origin_angst = origin * tomo_angpix + shift_angst
            t1 = np.matmul(rotm, -radius_angst.transpose())
            adj_origin_angst = origin_angst + t1

            out.write(
                f'view matrix mod #{offset + 1}.{i + offset + 1},'
                f'{rotm[0, 0]:.2f},{rotm[0, 1]:.2f},{rotm[0, 2]:.2f},{adj_origin_angst[0]:.2f},'
                f'{rotm[1, 0]:.2f},{rotm[1, 1]:.2f},{rotm[1, 2]:.2f},{adj_origin_angst[1]:.2f},'
                f'{rotm[2, 0]:.2f},{rotm[2, 1]:.2f},{rotm[2, 2]:.2f},{adj_origin_angst[2]:.2f}\n'
            )

        # Add final orientation command
        out.write('\nview orient\n')

    print(f'Writing out {output_filename}')


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
	
	output_filename = args.o
	TomoName = args.tomoname
	
	level= float(args.level)
	avg_angpix = float(args.avgAngpix)
	box_size = [float(x) for x in args.avgBoxSize.split(",")]
	angpix = float(args.tomoAngpix)
	offset = int(args.offset)	

	# Loading table
	df = dynamotable.read(args.i, args.tomoDoc)
	#print(df)
	dftomo = df[df.tomo_file == TomoName].copy()
	nosubtomo = len(dftomo)
	
	# Offset to load in case many different object. Not use now

	write_cxc_file(output_filename, dftomo, args.avgFilename, avg_angpix, box_size, level, offset, angpix)


	

