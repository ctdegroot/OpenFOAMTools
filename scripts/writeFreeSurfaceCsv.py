#!/usr/bin/python

import argparse

from modules import FreeSurfaceCalculator

""" This script may be used to output the level of a free surface as a function 
    of time to a csv file.
    
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

# Set up command line argument parser
description = 'Output free surface level as a function of time to a csv file.'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-d',
                    '--dir', 
                    help='Directory containing data files', 
                    required=False)
parser.add_argument('-o',
                    '--out',
                    help='Name of output file',
                    required=True)
args = vars(parser.parse_args())

# Get command line arguments
parentDir = args['dir']
if parentDir == None:
    parentDir = '.'
outputFile = args['out']

# Write the csv file
calculator = FreeSurfaceCalculator.FreeSurfaceCalculator(parentDir)
calculator.writeCsvOutput(outputFile)