import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

import numpy as np
from scipy.stats import beta

def subplot_ratio():
    """
    Create a subplot with dimensions useful for making ratio plots.
    """
    fig, ax=plt.subplots(2,1,sharex=True,squeeze=True,gridspec_kw={'height_ratios':(2,1),'hspace':0.1})
    return fig, ax

def yeff(ylim=1.1, ax=plt):
    """
    Setup y axis to represent efficiency
    """
    ax.set_ylim(0,ylim)
    ax.set_ylabel('Efficiency')

    ticks(ax.yaxis, 0.1, 0.02)

def ticks(axis, major, minor, majorfmt='{x:.1f}'):
    """
    Setup major/minor ticks
    """
    axis.set_major_locator(MultipleLocator(major))
    axis.set_major_formatter(majorfmt)
    axis.set_minor_locator(MultipleLocator(minor))

def hist(bins, values, ax=plt, **kwargs):
    """
    Draw a histogram using predefined bins and corresponding values.

    Contents of `kwargs` are passed to the matplotlib histogram function.
    """
    ax.hist(bins[:-1], bins=bins, weights=values, **kwargs)

def efficiency(bins, total, passed, ax=plt, **kwargs):
    """
    Draw an efficiency plot with error bars following the Clopper-Pearson 
    prescription.

    Parameters:
     - bins (list of float): Bins boundaries for the corresponding counts.
     - total (list of float): Total counts in each bin.
     - passed (list of float): Passed counts in each bin.
     - ax (AxesSubplot): plotting canvas
     - kwargs: passed to matplotlib errorbar function
    """
    # x axis
    x=(bins[1:]+bins[:-1])/2
    xerr=(bins[1:]-bins[:-1])/2

    # Mean values
    eff = np.divide(passed, total, out=np.zeros_like(passed), where=total!=0)

    # Uncertainty bars
    yerr = np.zeros((2, eff.shape[0]))

    level = 0.682689492137 # 1 sigma
    alpha = (1. - level) / 2

    # upper
    a = passed + 1
    b = total - passed
    yerr[1,:]=beta.ppf(1-alpha, a, b)
    yerr[1,:]=np.nan_to_num(yerr[1,:], nan=1.)

    # lower
    a = passed
    b = total - passed + 1
    yerr[0,:]=beta.ppf(  alpha, a, b)
    yerr[0,:]=np.nan_to_num(yerr[0,:], nan=0.)

    # normalize
    yerr=np.abs(yerr-eff)

    ax.errorbar(x, eff, xerr=xerr, yerr=yerr, fmt='.', **kwargs)

    return x,eff,xerr,yerr