import coffea.processor
import coffea.hist

import numpy as np
import awkward as ak

def dataset_normalization(xsecdb, dsid):
    """Calculates the dataset normaliation for DSID using values from `xsecdb`
    as cross-section * filter efficiency. If DSID is not in `xsecdb`, then
    return 1.
    """
    if dsid in xsecdb.index:
        return xsecdb.loc[dsid]['crossSection'] * xsecdb.loc[dsid]['genFiltEff']
    else:
        return 1.0

class HistProcessor(coffea.processor.ProcessorABC):
    """ Generic processor for making histograms.

    Manages `self.accumulator` dict with histograms. The actions taken are:
     - automated grouping of samples
     - normalization

    ## Grouping
    All histograms in `self.accumulator` are grouped using
    `coffea.hist.Hist.group` as part of the post-processing stage using the 
    group definition in `self.group`. This step is done after normalizing each
    sample independently.

    ## Normalization
    All histograms in `self.accumulator` are normalized in the post-processing
    stage to a cross-section defined in `self.xsecdb` using
    `dataset_normalization`. The denominator is is the sum of weights of all
    events (first element in `mcEventWeights` branch.)
    """
    def __init__(self, weight_column=None, xsecdb=None, group=None):
        """
        Parameters
          - weight_column (str): name of the column to use as event weight
          - xsecdb (pandas.DataFrame): cross-section database
          - group (dict): group definition for histograms
        """
        self.weight_column = weight_column
        self.xsecdb=xsecdb
        self.group=group
        self.accumulator = coffea.processor.dict_accumulator({
            'cutflow': coffea.processor.defaultdict_accumulator(float)
        })

    def weights(self, events, widx=0):
        """
        Return a list of weights for the supplied events.

        The weights are determined using the following procedure:
         1. `events[self.weight_column]` if the weight column is scalar
         2. `events[self.weight_column][:,widx]` if the weight column is a list
         3. `None` otherwise
        """
        # No defined weight column
        if self.weight_column is None:
            return None

        # Scalar weight column
        weight_column=events[self.weight_column]
        if type(weight_column.type.type) is ak._ext.PrimitiveType:
            return weight_column

        # List weight column (ie: alternate weights)
        if type(weight_column.type.type) is ak._ext.ListType:
            return weight_column[:,widx]

        return None

    def process(self, events):
        """
        Create accumulator identity and add to the `cutflow` sum.
        """
        output = self.accumulator.identity()
        dataset = events.metadata['dataset']

        if self.weight_column is not None:
            output['cutflow'][dataset] += np.sum(self.weights(events))
        else:
            output['cutflow'][dataset] += len(events)

        return output

    def postprocess(self, accumulator):
        """
        Normalization and grouping.
        """
        norm=None
        if self.xsecdb is not None:
            norm=dict(map(lambda i: (i[0], dataset_normalization(self.xsecdb, int(i[0]))/i[1]), accumulator['cutflow'].items()))

        dataset=coffea.hist.Cat("dataset", "Dataset")
        for key in accumulator:
            if type(accumulator[key]) is coffea.hist.Hist:
                if norm is not None:
                    accumulator[key].scale(norm, axis='dataset')
                if self.group is not None:
                    accumulator[key]+=accumulator[key].group('dataset',dataset,self.group)
        return accumulator
