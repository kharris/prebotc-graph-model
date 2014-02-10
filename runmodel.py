#!/usr/bin/env python
import os
import sys
import prebotc_BPR as prebotc
#import prebotc_weave as prebotc
import numpy as np
import scipy.integrate
import time
import argparse
import scipy.io
import progressbar

def parse_args(argv):
    # # defaults for original model
    # dt = 1e-3
    # tf = 30
    # defaults for BPR model
    dt = 1.0
    tf = 30.0e3
    # shared defaults
    t0 = 0.0
    abs_error = 1e-6
    rel_error = 1e-4
    parser = argparse.ArgumentParser(prog="runmodel",
                                     description='run the preBotC model')
    parser.add_argument('-t0', type=float, default=t0,
                        help='initial time (default: %(default)s)')
    parser.add_argument('-tf', type=float, default=tf,
                        help='final time (default: %(default)s)')
    parser.add_argument('-dt', type=float, default=dt,
                        help='time step (default: %(default)s)')
    parser.add_argument('param', help='parameter pkl file')
    parser.add_argument('graph', help='graph gml file')
    parser.add_argument('output', help='output (.mat) filename')
    parser.add_argument('--abs_err', '-a', type=float, 
                        help='absolute error (default: %(default)s)',
                        default=abs_error)
    parser.add_argument('--rel_err', '-r', type=float, 
                        help='relative error (default: %(default)s)',
                        default=rel_error)
    parser.add_argument('--save_full', '-F', action='store_true',
                        help='save all state variables (default: just membrane potentials)')
    args = parser.parse_args(argv[1:])
    return args.t0, args.tf, args.dt, args.param, args.graph, \
        args.output, args.abs_err, args.rel_err, args.save_full

def main(argv=None):
    if argv is None:
        argv = sys.argv

    t0, tf, dt, paramFn, graphFn, outFn, abs_error, rel_error, save_full \
        = parse_args(argv)
    # compute the number of steps required
    Nstep = np.ceil(tf/dt)
    print "Loading parameters, graph, and setting up IC's"
    my_params = prebotc.params(paramFn)
    num_vertices, num_edges, vertex_types, edge_list, in_edge_ct, in_edges \
        = prebotc.graph(graphFn)
    y, N = prebotc.ics(num_vertices, num_edges)
    # rhs of ODE with parameters evaluated
    # f is the rhs with parameters evaluated
    f = lambda t, y: prebotc.rhs(t, y, 
                                 vertex_types,
                                 edge_list,
                                 in_edge_ct,
                                 in_edges,
                                 my_params)
    # vector of states to output
    if save_full:
        save_state = np.zeros( (N, Nstep+1) )
    else:
        save_state = np.zeros( (num_vertices, Nstep+1) ) 
    r = scipy.integrate.ode(f)
    r.set_initial_value(y, t0)
    # method 1: BDF
    # r.set_integrator(
    #     'vode', 
    #     method='bdf', 
    #     with_jacobian = False,
    #     order=3,
    #     rtol= rel_error,
    #     atol= abs_error
    #     )
    # method 2: Dormand-Price
    # r.set_integrator(
    #     'dopri5', 
    #     rtol = rel_error,
    #     atol = abs_error
    #     )
    # method 3: VODE
    # r.set_integrator('vode',
    #                  rtol = rel_error,
    #                  atol = abs_error)
    print "Running integration loop...."
    t = time.time()
    bar_updates = 100
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()]
    bar = progressbar.ProgressBar(maxval=bar_updates, widgets=widgets)
    bar.start()
    i = 0
    j = 0
    while r.successful() and r.t < tf:
        r.integrate(r.t + dt)
        y = r.y.copy()
        if save_full:
            save_state[:, i] = y
        else:
            save_state[:, i] = prebotc.voltages(y, num_vertices)
        i += 1
        if ( i % np.floor(Nstep/bar_updates) ) == 0:
            bar.update(j)
            j += 1
    bar.finish()
    save_state = save_state[:, 0:(i-1)]
    elapsed = time.time() - t
    print "Done!\nElapsed: %1.2fs" % elapsed
    # Time saving
    t = time.time()
    print "Saving output...."
    scipy.io.savemat(outFn, 
                     mdict={'Y': save_state,
                            'vTypes': vertex_types,

                            'dt': dt,
                            't0': t0,
                            'tf': tf,
                            'paramFn': os.path.abspath(paramFn),
                            'graphFn': os.path.abspath(graphFn),
                            'absErr': abs_error,
                            'relErr': rel_error
                            },
                     oned_as = 'column')
    elapsed = time.time() - t
    print "Done!\nSave time: %1.2fs" % elapsed

# run the main stuff
if __name__ == '__main__':
    status = main()
    sys.exit(status)
