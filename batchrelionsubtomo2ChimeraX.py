#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.3
Batch version of relionsubtomo2ChimeraX.py that generates scripts for all tomograms in the star file.

Usage: batchrelionsubtomo2ChimeraX.py --i run_data.star --o load_chimera.cxc --avgAngpix 10.48 --avgBoxSize "64,64,64"
@author: Huy Bui, McGill University
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import starfile
import argparse
from relionsubtomo2ChimeraX import write_cxc_file  # Importing the function

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch generate ChimeraX scripts for all tomograms in the star file.')
    parser.add_argument('--i', help='Input star file', required=True)
    parser.add_argument('--o', help='Output prefix of ChimeraX Script', required=True)
    parser.add_argument('--avgAngpix', help='Pixel size of average', required=True)
    parser.add_argument('--avgBoxSize', help='Box size of average', required=True)
    parser.add_argument('--avgFilename', help='Avg subtomo filename', required=False, default='avg.mrc')
    parser.add_argument('--level', help='Level of subtomo avg', required=False, default=0.0039)
    parser.add_argument('--offset', help='Offset of volume number', required=False, default=0)
    parser.add_argument('--relion31', help='Star file from Relion 3.1 (1 or 0)', required=False, default=0)
    parser.add_argument('--coordAngpix', type=float, help='Pixel size of subtomogram coordinate', default=-1, required=False)

    args = parser.parse_args()
    output_prefix = args.o.replace(".cxc", "")
    avg_angpix = float(args.avgAngpix)
    box_size = [float(x) for x in args.avgBoxSize.split(",")]
    level = float(args.level)
    offset = int(args.offset)
    relion31 = int(args.relion31)

    # Load Relion star file
    stardict = starfile.read(args.i)
    df_optics = stardict['optics']
    df_particles = stardict['particles']

    tomo_list = df_particles.rlnTomoName.unique().tolist() if relion31 == 0 else df_particles.rlnMicrographName.unique().tolist()

    for tomo_name in tomo_list:
        if relion31 == 0:
            angpix = df_optics.loc[0, 'rlnTomoTiltSeriesPixelSize']
            dftomo = df_particles[df_particles.rlnTomoName == tomo_name].copy()
        else:
            angpix = df_optics.loc[0, 'rlnImagePixelSize']
            dftomo = df_particles[df_particles.rlnMicrographName == tomo_name].copy()
            
        # Overwrite pixel size if provided
        if args.coordAngpix > 0:
            angpix = args.coordAngpix

        print (f"Use coordinate pixel size of {angpix:.2f} Angstrom")

        dftomo.reset_index(drop=True, inplace=True)
        output_filename = f"{output_prefix}_{tomo_name}.cxc"
        write_cxc_file(output_filename, dftomo, args.avgFilename, avg_angpix, box_size, level, offset, angpix)
