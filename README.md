# WARNING! READ THIS FIRST
This tool is grossly INCOMPLETE.  
It was started Summer 2021 but could not be completed because the author was pulled away to complete abandoned work.  

# lrt2sradsky
A libRadtran wrapper to produce spectral radiance across the sky.  

Predicted spectral radiance across the skydome is useful for many applications including building performance. In general, we want to know the spectral energy coming in from all directions of the sky. This energy changes greatly depending on the position of the sun and the state of the atmosphere (aerosol optical depth, composition, pollution, ash, etc.).  

libRadtran can predict spectral radiance coming directly from the sun (direct beam solar) and indirectly at locations in the sky (indirect diffuse sky) given a properly configured input file for the site and a complete list of sky coordinates. It can also compute spectral radiance sums (irradiance) for the entire sky. However, it doesn't do both at the same time. So to get the direct beam solar and a set of specific coordinates in the sky may take 2 separate runs. libRadtran supports many input parameters (some conflicting) which can be confusing if new to the library. Some are global atmospheric parameters that apply to all sites on Earth while others are site location specific.  

This tool should take as arguments:  
- a datetime of the sky of interest (sun location can be inferred from this time)
- a site location input file (libRadtran parameters specific to the site, including addition atmospheric properities if desired)
- optional arguments for length and resolution of spectrum, solver, etc. if desired

This tool should then:
1. create 2 new downstream input files that will be loaded into libRadtran
    - first one will be used to compute: edir (direct beam solar), edn (downward welling irradiance), eglo (sum of the two)
    - second one will be used to compute: spectral radiance per a list of coordinates across the sky
2. copy the template input file with global parameters to both input files
5. copy the parameters from the site location input file to both input files
7. write the specified datetime to the new files
8. compute or load a list of equidistant coordinates across the sky to the second input file
9. run libRadtran on both newly created input files
10. parse the results and combine them into a final "sky file"  

Example:  
`lrt2sradsky in/ithaca.inp "07/26/2013 13:15 EST"`  
to produce:  
- ithaca.sol.072620131315EST.inp (input file for computing edir and global irradiance)  
- ithaca.sky.072620131315EST.inp (input file for computing edir and global irradiance)  
- ithaca.sol.072620131315EST.out (results from libRadtran)  
- ithaca.sol.072620131315EST.txt (log file from libRadtran) 
- ithaca.sky.072620131315EST.out (results from libRadtran)  
- ithaca.sky.072620131315EST.txt (log file from libRadtran)   
- ithaca.072620131315EST.csv (merged solar and sky spectral radiances per nm of the specified spectrum)

# libRadtran 
### Install
libRadtran is easy to install by following their instructions on their website: http://www.libradtran.org/doku.php?id=download  
If you get any errors during install, it is probably because you are missing some of the required libraries like: make, gcc/gpp, gsl, flex, netcdf, etc.  
Make sure to download and unpack the following absorption and scattering databases as well (necessary for accurate results):  
- Optical properties of water clouds, ice clouds and OPAC aerosols in netcdf format  
- Optical properties for ice cloud parameterization based on single scattering data by P. Yang et al., 2013  
- Data for the REPTRAN absorption parameterization  

Once installed, there are many input (.inp) file examples in the `examples` directory.  
The libRadtran manual can be found here: http://www.libradtran.org/doc/libRadtran.pdf  
Specifics about default solver (`distort`): http://www.libradtran.org/lib/exe/fetch.php?media=disortreport1.1.pdf   

### Usage
**`uvspec`** is the tool that produces the spectral radiances.  
`uvspec` **must** be executed in such a way so that it knows where the libRadtran `data` directory is, which includes the atmospheric databases needed for it to run. Some of this data can be specified by path in the input files themselves, but some of it is accessed from this default `data` directory within the libRadtran install folder by default. If you do not want to change your current working directory, you can execute `uvspec` like this so that it can still load its data:  
`cd ~/libRadtran-2.0.2/bin/ && exec uvspec < in/ithaca.072620131315EST.inp > in/ithaca.072620131315EST.out`  

By default, standard out and err will be saved to a file called `log.txt` or `verbose.txt`. You can redirect this output to whichever file you want like so:  
`(cd ~/libRadtran-2.0.2/bin/ && exec uvspec < in/ithaca.072620131315EST.inp > in/ithaca.072620131315EST.out) >& out/ithaca.072620131315EST.txt`
