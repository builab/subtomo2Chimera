# subtomo2Chimera

## Required:
[starfile](https://pypi.org/project/starfile/) and [eulerangles](https://pypi.org/project/eulerangles/) modules from Alister Burt

```
pip install eulerangles
pip install starfile
```

## Usage:
```
python relionsubtomo2ChimeraX.py --i run_data_empiar10064.star --o load_tomo1.cxc --avgAngpix 10.48 --avgBoxSize "64,64,64" --tomoname CTEM_tomo1
```

*--i* Input star file

*--o* Output ChimeraX Loading Script

*--avgAngpix* Pixel Size of the average file

*--avgBoxSize* Box Size of the average. 3 values seperated by comma and double quoted. Better be a cube. Not tested with non-cube yet.

*--tomoname* Name of tomo for the visualization. You have to do this script for each tomo you want to visualize.

Not required option

*--avgFileName* Name of subtomo average loaded for the visualization. Default is *avg.mrc* but you can put any name in.

*--offset* (default 0) Offset number if you want to load different kinds of subtomogram averages into the same session

*--level* (default 0.0039) Volume level set for the subtomogram average


## How it works:
The script will load the subtomogram average in Chimera and transform it to orientation of each subtomo in the tomogram. You can also load the tomogram in to visualize it together. This script only perform for only one kind of subtomogram average but it is not too difficult to do the same thing with different classes of average using the offset and combine the loading script together.

The subtomogram average name is avg.mrc by default. You need to adjust the level of the average in output Chimera loading script. You can use the exact command above to test the example of ribosome subtomo average from EMPIAR-10064.

The output Chimera loading script uses a lot of memory due to many subtomograms rendering. Therefore, try to make the avg.mrc file as small as possible. It doesn't have to be the same pixel size as the star file data. You can use further binning/tight crop and then input the pixel size & box size of the subtomogram average into the command

Update: 2022/05/03 Now you can customize the subtomo avg name & the offset is now correct.

**NOTE 1:**

For calculation of rotation matrix:
The rotation matrix needs to be transposed due to the view orientation of Chimera (turn x 180).

The shift after the rotation = RotationMatrix*-HalfBoxSize + CoordinateOfSubtomogram


**NOTE 2:**
Script only works with relion 4.0 star file.
The Chimera version of the script also works to a certain degree but it is very clumpsy and not properly aligned to the tomogram.

## How to run:
1. Prepare the input files: Relion star file from Refine3D job (Should be at least 3.1 and up), the binned out subtomogram average avg.mrc (size ~1Mb)

2. Generate the ChimeraX loading script for a specific tomogram using the above command

*python relionsubtomo2ChimeraX.py --i run_data_empiar10064.star --o load_tomo1.cxc --avgAngpix 10.48 --avgBoxSize "64,64,64" --tomoname CTEM_tomo1* 

Full command

*python relionsubtomo2ChimeraX.py --i run_data_empiar10064.star --o load_tomo1.cxc --avgAngpix 10.48 --avgBoxSize "64,64,64" --tomoname CTEM_tomo1 --level 0.0039 --avgFileName avg.mrc --offset 0* 

3. Edit the ChimeraX loading script for proper level of the map and open the output script in Chimera using commandline or interface:

*chimerax load_tomo1.cxc*

4. Loading the tomogram into ChimeraX (Better bin4 or more for faster loading)

5. Set the right pixel size and origin for the tomogram to be properly located relative to the subtomogram average

*volume #TomoModelNumber voxelSize 10.48 originIndex 0,0,0*


**View of the subtomogram average only**

![AvgOnly](https://github.com/builab/subtomo2Chimera/blob/main/image4.png?raw=true)

**View of subtomogram average within the tomogram**

![VolumeDisplay](https://github.com/builab/subtomo2Chimera/blob/main/image2.png?raw=true)

**Plane View**

![PlaneDisplay](https://github.com/builab/subtomo2Chimera/blob/main/image3.png?raw=true)




