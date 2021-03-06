#!/usr/bin/env python

import scipy.io
import argparse
import sys
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os.path
import os

'''
    This file looks at a given mat file with the final metrics over all runs given and will 
    plot this with the standard deviation error
'''
def parse_args(argv):


    #parsing
    parser = argparse.ArgumentParser(prog ="collectionPlots",
                                     description = 'plotting collection data')
    parser.add_argument('input', help = 'file contaning collection data (.mat)')
    parser.add_argument('output', help='output filename .jpeg(graph type will be appended)')
    
    args = parser.parse_args(argv[1:])
    return args.input, args.output

'''
    This arranges the data from the mat and gets the population correlation/phase lags, finds the
    standard deviation and also the average to plot
'''
def arrange_popcor_phaselag(data,start_of_sweep,end_of_sweep,steps):
    std_dev_phase = []
    std_dev_pop = []
    phase = []
    pop = []
    sweep_values = []

    ##Sweeps through the parameters you swept through
    for i in np.arange(start_of_sweep,end_of_sweep,steps):
        temp_phase = []
        temp_corr = []
        for j in data:
           if float(str( j[0][0])) == i:
                temp_phase.append(j[1][0])
                temp_corr.append(j[2][0])
          
           
        ##stores the means and standard deviations of each sweep value        
        sweep_values.append(i)        
        phase.append(np.mean(temp_phase))
        pop.append(np.mean(temp_corr))
        std_dev_phase.append(np.std(temp_phase))
        std_dev_pop.append(np.std(temp_corr))
    
    return std_dev_phase,std_dev_pop,phase,pop,sweep_values 

def main(argv=None):
    if argv is None:
        argv = sys.argv
    (in_fn,out_fn) = parse_args(argv)
    data = scipy.io.loadmat(in_fn)

    ##Get the values for the pop correlation and phase lag
    (std_dev_phase,std_dev_pop,phase,pop,sweep_values) = arrange_popcor_phaselag(data['phase_lag_pop_corr'],0,3.25,.25)

    
    ###Graph the data
    plt.figure(1)
    ax = plt.subplot(111)
    plt.errorbar(sweep_values,phase,std_dev_phase,marker = 'o' ,label ="Phase Shift")
    plt.errorbar(sweep_values,pop,std_dev_pop,c='r',marker= 'o',label="Pop Correlation")
    plt.title('Sweep of Block structure')
    plt.xlabel('idegree')
    plt.ylabel('Phase or Strength Value')
    plt.axis([-.2,3.2,0,1])
    ax.legend()
    plt.savefig(out_fn)

if __name__ == '__main__':
    status = main()
    sys.exit(status)
    
    

        
