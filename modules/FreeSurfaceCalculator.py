import glob
import numpy as np
import os

class FreeSurfaceCalculator(object):
    """Class to calculate the level of a free surface as a function of time.
    
    This assumes that sampled data is organized such that there is one folder
    per timestep, containing a single .xy file.  The .xy file should contain
    two columns, the first of which contains a coordinate value representative 
    of the "height" of the free surface and the second contains values of the
    volume fraction at those locations.  The free surface height is calculated
    by interpolating from the .xy data the location where the volume fraction 
    is equal to 0.5.
    
    Sample code that could be used in an OpenFOAM controlDict file to generate
    the data files is:
    
    functions
    (
        elevation
        {
            type                sets;
            functionObjectLibs  ("libsampling.so");
            outputControl       timeStep;
            interpolationScheme cellPointFace;
            setFormat           raw;
            fields
            (
                alpha1
            );
            sets
            (
                lineX1
                {
                    type uniform;
                    axis distance;
                    start (6.0 0 0.0005);
                    end (6.0 0.5 0.0005);
                    nPoints 500;
                }
            );
        }
    )
    
    Current limitations of this code, that could be addressed in the future are:
    
      - There must only be one .xy file in each directory. This could be 
        extended to allow the free surface height to be calculated at multiple 
        locations.
      - If there are multiple free surface locations (i.e. more than one 
        location where the volume fraction equals 0.5) only the first to be 
        encountered will be logged. This could be extended to look for multiple
        free surfaces which would be relevant in cases where there is 
        entrapment of one phase inside of the other. 
    """
    
    def __init__(self, parentDir='.'):
        """Class initialization.
        
        Input parameters:
          parentDir : top level directory containing subdirectories for each 
                      timestep; defaults to current directory.
        """
        self._parentDir = parentDir
        self._data = []
        
    def _calculate(self):
        """Calculates the free surface height for each timestep."""
        
        # Get all of the directories containing data; results are filtered to 
        # only starting with a number to avoid getting potential hidden files/
        # directories or other extraneous results
        dirs = glob.glob(os.path.join(self._parentDir, '[0-9]*'))
        
        # Loop through all of the directories; assume only one file is in each
        for dir in dirs:
            
            files = os.listdir(dir)
            
            # There should only be one .xy file, but this is necessary in case
            # there are hidden files
            fileName = None
            for file in files:
                if file.endswith('.xy') and not file.startswith('.'):
                    fileName = file
                    break
            
            # Load the xy data and assign to variables
            data = np.loadtxt(os.path.join(dir, fileName))
            y = data[:,0]
            alpha = data[:,1]
            
            # Find the free surface location
            for i in range(alpha.size):
                if alpha[i] > 0.5 and alpha[i+1] < 0.5:
                    break
            
            time = os.path.basename(dir)
            ys = np.interp(0.5, [alpha[i], alpha[i+1]], [y[i], y[i+1]])
            
            # Save the data
            self._data.append([time, ys])
        
    def writeCsvOutput(self, outputCsvFile):
        """Writes the free surface location as a function of time to csv file.
        
        Input parameters:
          outputCsvFile : file name where output will be written; if extension
                          .csv is not present it will be added.
        """
        self._calculate()
        
        if not outputCsvFile[-4:] == '.csv':
            outputCsvFile += '.csv'    
        output = open(outputCsvFile, 'w')
        
        for row in self._data:
            output.write('{}, {}\n'.format(*row))

            