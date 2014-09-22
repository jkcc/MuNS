'''
Created on 15/08/2014

@author: Jeffrey Chan, 2014
'''

import sys
import getopt
import glob
import csv
import os.path
import string
import subprocess as sp
import numpy as np
from testingUtils import *

def main():
    # process options
    try:
        # option list
        options = "p:t:c:b:n:e:s:"
        # get options
        optList, remainArgs = getopt.gnu_getopt(sys.argv[1:], options)
    except getopt.GetoptError, err:
        print >> sys.stderr, str(err)
        usage(sys.argv[0])
    
     
    sMode = 'list'
    maxIter = 20
    convEpsilon = 0.03
    ioBalance = 0.5
    topNCompared = 10
    simEpsilon = 0.001
    earlySimStopThres = 0.1
    for opt, arg in optList:
        if opt == "-p":
            sMode = arg
        elif opt == '-t':
            maxIter = int(arg)
        elif  opt == '-c':
            convEpsilon = float(arg)
        elif  opt == '-b':
            ioBalance = float(arg)
        elif  opt == '-n':
            topNCompared = int(arg)
        elif  opt == '-e':
            simEpsilon = float(arg)
            assert(simEpsilon <= 1.0 and simEpsilon >= 0.0)            
        elif opt == '-s':
            earlySimStopThres = float(arg)
        else:
            print >> sys.stderr, sys.argv[0] + " -m <mat index wanted> [edge list]"
            sys.exit(2)    
    
    # check number of arguments
    if len(remainArgs) != 4:
        usage(sys.argv[0])
    
    sGraphFile = remainArgs[0]    
    sPartFile = remainArgs[1]
    sResultsOutPrefix = remainArgs[2]
    vertNum = int(remainArgs[3])
    
    
    
#     lLambdaRange = [0.1, 0.3, 0.5, 0.7, 0.9]
    lLambdaRange = [0.9]
#     lBetaRange = [0.5]
#     lLambdaRange = [0.9]
    sInitAlgor = 'degBinaryInit'
#     lsInit = ['degRatioInit']
#     lsAlgor = ['autosim', 'autoSimEarlySim', 'rolesim', 'matchsim', 'simrank', 'prank']
    lsAlgor = ['icebergAutosim']
#     lsAlgor = ['simrank']
#     lsAlgor = ['autosim']
    
    

    for sAlgorname in lsAlgor:       
        print sAlgorname              
        fResultOut = open(sResultsOutPrefix + '_' + sAlgorname + '.out.csv' , 'w')
        csvResultOut = csv.writer(fResultOut, delimiter=',')               
                
        llPartitions = loadPart(sPartFile, sMode)
        
        # store results
        lResults = []

        sTempOutFile = 'temp.out'
        sExec = '~/Programming/workspace/matlabSimrank/rolesim2/cRolesim2/Release/cRoleSim2'
        
        for dampingFactor in lLambdaRange:
            print [sExec, 
                                ' -t ' + str(maxIter), 
                                ' -e ' + str(convEpsilon), 
                                ' -i ' + sInitAlgor,
#                                 ' -b ' + str(ioBalance),
                                ' -d ' + str(dampingFactor),
                                ' -s ' + str(earlySimStopThres),
                                sGraphFile,
                                sAlgorname, 
                                str(vertNum),
                                sTempOutFile
                                ]
            proc = sp.Popen(sExec + 
                                ' -t ' + str(maxIter) + 
                                ' -e ' + str(convEpsilon) + 
                                ' -i ' + sInitAlgor +
#                                 ' -b ' + str(ioBalance) +
                                ' -d ' + str(dampingFactor) +
                                ' -s ' + str(earlySimStopThres) +
                                ' ' + sGraphFile +
                                ' ' + sAlgorname +
                                ' ' + str(vertNum) +
                                ' ' + sTempOutFile
                                ,
                                shell=True, stderr=sp.PIPE, stdout=sp.PIPE)
            sOut, sErr = proc.communicate()
            print sOut
            print sErr
                
            # get the results
            with open('temp.out', 'r') as fTempOutput:
                # read in first two rows
                sLine = fTempOutput.readline();
                lTokens = sLine.split(':')
                runningTime = float(lTokens[1])
                    
                sLine = fTempOutput.readline();
                lTokens = sLine.split(':')
                iterNum = int(lTokens[1])                        
                    
                # read in similarity matrix
                llSim = [];
                csvTempOut = csv.reader(fTempOutput, delimiter=',')
                for lRow in csvTempOut:
                    llSim.append([float(x) for x in lRow])
                                            
                # do accuracy testing
                assert(len(llPartitions) > 0)
                intra = avgIntraSim(llSim, llPartitions)
                inter = avgInterSim(llSim, llPartitions)
                intraInterRatio = intra / inter
                
                lSim = [item for lSublist in llSim for item in lSublist]
                rowLen = len(llSim[0])                
                intraRank, interRank = avgRank(lSim, rowLen, llPartitions, simEpsilon)
                    
                # average precision
#                 precision, recall, fscore = avgRetrievalStats(llSim, llPartitions, topNCompared)
                precisionAtK = avgPrecisionAtK(llSim, llPartitions, topNCompared)
                rPrecision = avgRPrecision(llSim, llPartitions)
                MAP = avgMAP(llSim, llPartitions)
                
                # store results
                lResults.append([sAlgorname, sInitAlgor, ioBalance, dampingFactor, runningTime, iterNum, intra, inter, intraInterRatio, intraRank, interRank, precisionAtK, rPrecision, MAP])
                currRow = [sAlgorname, sInitAlgor, ioBalance, dampingFactor, runningTime, iterNum, intra, inter, intraInterRatio, intraRank, interRank, precisionAtK, rPrecision, MAP]
                csvResultOut.writerow(currRow)
                fResultOut.flush()
                
            
            # delete temp.out
            os.remove('temp.out')
                  
        fResultOut.close()
    
        

######################################################################

def usage(sProgname):
    print >> sys.stderr, sProgname + "[original gml file that is to be aligned] [gml file where we want to align to] [output of aligned gml file]"
    sys.exit(2)


if __name__ == '__main__':
    main()