#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.3 - Refactored
Created on Sat Dec  4 22:56:14 2021

Script to convert Relion 4.0 star file to visualization script in Chimera/ChimeraX.
Updated with reusable `write_cxc_file` function for modularity.
Usage: relionsubtomo2ChimeraX.py --i run_data.star --o load_chimera.cmd --avgAngpix 10.48 --avgBoxSize "64,64,64" --tomoname CTEM_tomo1
@author: Huy Bui, McGill University
"""

import numpy as np
import starfile
import argparse
from eulerangles import euler2matrix



def write_cxc_file(output_filename, dftomo, avg_filename, avg_angpix, box_size, level, offset, angpix):
    """
    Writes a ChimeraX `.cxc` script for the given tomogram data.
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
        for i, row in dftomo.iterrows():
            eulers_relion = row[['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].to_list()
            rotm = euler2matrix(eulers_relion, axes='zyz', intrinsic=True, right_handed_rotation=True).transpose()
            origin = row[['rlnCoordinateX', 'rlnCoordinateY', 'rlnCoordinateZ']].to_numpy()
            shift_angst = row[['rlnOriginXAngst', 'rlnOriginYAngst', 'rlnOriginZAngst']].to_numpy()
            origin_angst = origin * angpix - shift_angst
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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Relion 4.0 subtomo star to ChimeraX session')
    parser.add_argument('--i', help='Input star file', required=True)
    parser.add_argument('--o', help='Output ChimeraX Script', required=True)
    parser.add_argument('--avgAngpix', help='Pixel size of average', required=True)
    parser.add_argument('--avgBoxSize', help='Box size of average', required=True)
    parser.add_argument('--tomoname', help='Tomo Name', required=True)
    parser.add_argument('--avgFilename', help='Avg subtomo filename', required=False, default='avg.mrc')
    parser.add_argument('--level', help='Level of subtomo avg', required=False, default=0.0039)
    parser.add_argument('--offset', help='Offset of volume number', required=False, default=0)
    parser.add_argument('--relion31', help='Star file from Relion 3.1 (1 or 0)', required=False, default=0)

    args = parser.parse_args()
    output_filename = args.o
    avg_filename = args.avgFilename
    avg_angpix = float(args.avgAngpix)
    box_size = [float(x) for x in args.avgBoxSize.split(",")]
    level = float(args.level)
    offset = int(args.offset)
    tomo_name = args.tomoname
    relion31 = int(args.relion31)

    # Load Relion star file
    stardict = starfile.read(args.i)
    df_optics = stardict['optics']
    df_particles = stardict['particles']

    # Select tomogram data based on Relion version
    if relion31 == 0:
        angpix = df_optics.loc[0, 'rlnTomoTiltSeriesPixelSize']
        dftomo = df_particles[df_particles.rlnTomoName == tomo_name].copy()
    else:
        angpix = df_optics.loc[0, 'rlnImagePixelSize']
        dftomo = df_particles[df_particles.rlnMicrographName == tomo_name].copy()

    # Reset index to ensure proper indexing
    dftomo.reset_index(drop=True, inplace=True)

    # Write the ChimeraX script
    write_cxc_file(output_filename, dftomo, avg_filename, avg_angpix, box_size, level, offset, angpix)
