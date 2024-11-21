#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.3
Created on Sat Dec  4 22:56:14 2021
Modification of relionsubtomo2ChimeraX.py for Dynamo table
Batch processing of multiple tomograms.

Usage:
python subtomo2Chimera/dynamotable2ChimeraX.py \
--tomoDoc tomograms.doc \
--i CU428_TS013_1/aligned.tbl \
--o test_013.cxc \
--avgAngpix 8.48 \
--tomoAngpix 8.48 \
--avgBoxSize "128,128,15" \
--avgFilename avg.mrc \
--level 0.0039
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
import dynamotable
from dynamotable2ChimeraX import write_cxc_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch convert Dynamo table to ChimeraX session')
    parser.add_argument('--i', help='Input table file', required=True)
    parser.add_argument('--tomoDoc', help='Input tomo doc file', required=True)
    parser.add_argument('--o', help='Output ChimeraX Script prefix', required=True)
    parser.add_argument('--avgAngpix', help='Pixel size of average used for display', required=True)
    parser.add_argument('--tomoAngpix', help='Pixel size of tomogram in table', required=True)
    parser.add_argument('--avgBoxSize', help='Box size of average', required=True)
    parser.add_argument('--avgFilename', help='Average subtomo filename (mrc or stl format)', required=False, default='avg.mrc')
    parser.add_argument('--level', help='Level of subtomo average', required=False, default=0.0039)
    parser.add_argument('--offset', help='Offset of volume number', required=False, default=0)

    args = parser.parse_args()

    # Parameters
    outfile_prefix = args.o.replace(".cxc", "")
    level = float(args.level)
    avg_angpix = float(args.avgAngpix)
    box_size = [float(x) for x in args.avgBoxSize.split(",")]
    angpix = float(args.tomoAngpix)
    offset = int(args.offset)

    # Load Dynamo table
    df = dynamotable.read(args.i, args.tomoDoc)

    # Get unique tomograms
    tomo_list = df.tomo_file.unique().tolist()

    for tomo_name in tomo_list:
        # Filter data for the current tomogram
        dftomo = df[df.tomo_file == tomo_name].copy()

        # Create output file for this tomogram
        output_file = f"{outfile_prefix}_{tomo_name}.cxc"

        # Write the ChimeraX script using the external function
        write_cxc_file(
            output_filename=output_file,
            dftomo=dftomo,
            avg_filename=args.avgFilename,
            avg_angpix=avg_angpix,
            box_size=box_size,
            level=level,
            offset=offset,
            tomo_angpix=angpix
        )

