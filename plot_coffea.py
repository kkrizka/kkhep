# %% Autoreload for when running in a notebook
#%load_ext autoreload
#%autoreload 2

# %% Important packages
import yaml

import kkplot

import coffea.hist

import awkward as ak
import numpy as np
import matplotlib.pyplot as plt

import argparse
import pathlib
import sys, os

from math import *

# %% Prepare configuration
if 'ipykernel' in sys.modules: # running in a notebook
    #%load_ext autoreload
    #%autoreload 2
    runcfgpath='trthits.yaml'
    workers=16
    testmode=True
else:
    parser = argparse.ArgumentParser()
    parser.add_argument('runconfig', help='Path to run configuration file')
    parser.add_argument('-j', '--workers', type=int, default=8, help='Number of workers')
    parser.add_argument('-t', '--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()

    runcfgpath=args.runconfig
    workers=args.workers
    testmode=args.test

runconfig={}
with open(runcfgpath) as fh:
    runconfig=yaml.safe_load(fh)

# %% Create a list of input files
fileset=runconfig['input']

# %% Prepare the processor
import importlib

pconfig=runconfig['processor'].copy()

# treename
treename=pconfig.pop('tree')

# processor class
pclass=pconfig.pop('class')
pcpart=pclass.split('.')
pmodul='.'.join(pcpart[:-1])
pmodule=importlib.import_module(pmodul)
pclass=pcpart[-1]

processor=getattr(pmodule,pclass)(**pconfig)

# %%
# from dask.distributed import Client
# client = Client('tcp://localhost:8786')
# executor = coffea.processor.DaskExecutor(client=client)
#executor = coffea.processor.IterativeExecutor()
executor = coffea.processor.FuturesExecutor(workers=workers)

run = coffea.processor.Runner(executor=executor,
                    savemetrics=True
                    )

out, metrics = run(fileset, treename, processor_instance=processor)

print(metrics)

# %% Helpful function for formatting a histogram
def formatter(ax, **kwargs):
    if 'logy' in kwargs:
        ax.set_yscale('log')

    if 'xticksmajor' in kwargs and 'xticksminor' in kwargs:
        kkplot.xticks(kwargs['xticksmajor'],kwargs['xticksminor'],ax=ax)

# %% Plot 1D histograms  
def plot_runs(hist, format=None, outname=None):
    xlabel=hist.axes()[1].label

    fig, ax = plt.subplots()

    histcommon={'histtype':'step','density':True}
    for runNumber in hist.identifiers('runNumber'):
        h=hist[runNumber]
        kkplot.hist(h.axes()[1].edges(), h.values()[(str(runNumber),)], label=runNumber, ax=ax, **histcommon)

    if format is not None:
        formatter(ax, **format)

    ax.set_xlabel(xlabel)

    ax.set_ylabel('a.u.')
    ax.legend(title='Run Number')

    if outname is not None:
        fig.savefig(f'{outname}.png')
    fig.show()

# %% Plot 1D histograms sliced in a variable
def plot_slices(hist, format=None, outname=None):
    xlabel=hist.axes()[2].label
    ylabel=hist.axes()[1].label

    ncols=int(ceil(sqrt(hist.axes()[1].edges().size)))
    fig, ax = plt.subplots(ncols,ncols,figsize=(15,15),sharex=True,sharey=True)
    ax=ax.flatten()

    histcommon={'histtype':'step','density':True}
    for runNumber in hist.identifiers('runNumber'):
        h=hist[runNumber]

        d=h.values()[(str(runNumber),)]
        for sidx in range(d.shape[0]):
            mymin=h.axes()[1].edges()[sidx]
            mymax=h.axes()[1].edges()[sidx+1]

            ax[sidx].set_title(f'{ylabel}=[{mymin:.1f},{mymax:.1f})')

            kkplot.hist(h.axes()[2].edges(), d[sidx], ax=ax[sidx], label=runNumber, **histcommon)


    # Format every subplot
    for myax in ax:
        myax.set_xlabel(xlabel)

        myax.set_ylim(0,0.1)

        if format is not None:
            formatter(myax, **format)

    ax[0].legend(title='Run Number')

    fig.tight_layout()

    if outname!=None:
        fig.savefig(f'{outname}.png')
    fig.show()
    return fig,ax

# %% Run the plotting
for pname,pdef in runconfig.get('plots',{}).items():
    # Get the plotter
    plotter=pdef['plotter']
    pcpart=plotter.split('.')
    pmodule='.'.join(pcpart[:-1])
    pmodule=importlib.import_module(pmodule)
    pfuncto=pcpart[-1]
    plotter=getattr(pmodule,pfuncto)

    # Make the histograms
    for hdef in pdef['histograms']:
        if type(hdef)==str:
            hname=hdef
            form=None
        else:
            hname=hdef['name']
            form=hdef.get('format')
        plotter(hist=out[hname], format=form, outname=f'{hname}')
