"""
Helpful functions for configuring coffea processors and histograms.
"""

from coffea.hist import Bin, Cat, Hist

def bins(bdefs):
    """
    Create a dictionary of bin defintions.

    A bin definition consists of the following properties:
        - label: axis label
        - nbins: number of bins
        - min: lower bound of the binning
        - max: upper bound of the binning

    Parameters:
    -----------
    bdefs: dictionary of bin definitions
        Keys are the names of the bins.
    """
    mybins={}
    for bname,bdef in bdefs.items():
        mybins[bname]=Bin(bname, bdef['label'], bdef['nbins'], bdef['min'], bdef['max'])
    return mybins

def histograms(hdefs, bins):
    """
    Create a dictionary of histograms using existing bin definitions.

    Add histograms have a category bin called `dataset`.

    A histogram definition is a list of bin names corresponding to existing bin
    defintions in `bins`.
    """
    histograms={}
    for hname,hdef in hdefs.items():
        hbins=[bins[bdef] for bdef in hdef]
        hist=Hist(
            "a.u.",
            Cat("dataset", "Dataset Name"),
            *hbins)
        histograms[hname]=hist
    return histograms
