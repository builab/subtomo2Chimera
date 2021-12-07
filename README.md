# subtomo2Chimera

Required: starfile and eulerangles module from Alister Burt

Usage: relionsubtomo2ChimeraX.py --i run_data_empiar10064.star --o load_chimera.cxc --avgAngpix 10.48 --avgBoxSize "64,64,64" --tomoname CTEM_tomo1

-i Input star file

-o Output ChimeraX Loading Script

-avgAngpix Pixel Size of the average file

-avgBoxSize Box Size of the average.

-tomoname Name of tomo for the visualization


The subtomogram average name is avg.mrc by default. You need to adjust the level of the average in output Chimera loading script.
The output Chimera loading script uses a lot of memory due to many subtomograms. Therefore, try to make the avg.mrc file as small as possible. It doesn't have to be the same pixel size as the star file data.

NOTE: The Chimera version also works but very clumpsy.
