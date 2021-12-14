import yaml

"""
Collection of classes to handle sample definitions.
"""

class Sample:
    """
    A single sample.
    """
    def __init__(self, data):
        self.data=data

class MultiSample:
    """
    A `MultiSample` is a set of Samples corresponding to a single process. For
    example, a pT sliced dataset.
    """
    def __init__(self, subsamples):
        self.samples=subsamples

class SampleManager:
    """
    Collection of `Sample` and `MultiSample` objects.
    """
    def __init__(self, sampledef=None):
        """
        Parameters:
            - sampledef (str): path to sample definition file
        """
        self.samples={}
        if sampledef is not None:
            self.add_sampledef(sampledef)

    def add_sampledef(self, sampledef):
        """
        Add a sample definition to the manager. A sample definition is a YAML
        file that contains sample and multisample definitions. The parsed
        result is appended to `this.samples`.
        
        An example of the syntax is.

        ```yaml
        samplename:
            data:
                - mysample.root
        multisamplename:
            sample0:
                data:
                    - file0.root
            sample1:
                data:
                    - file1.root
        ```

        Parameters:
            - sampledef (str): path to sample definition file
        """
        with open(sampledef) as fh:
            data=yaml.safe_load(fh)
        for samplename,sampledata in data.items():
            samplename=str(samplename)
            if 'data' in sampledata:
                sample=Sample(data=sampledata['data'])
                self.samples[samplename]=sample
            else: # this is a multisample
                subsamples={}
                for subname,subdata in sampledata.items():
                    subname=str(subname)
                    subsamples[subname]=Sample(**subdata)
                sample=MultiSample(subsamples)
                self.samples[samplename]=sample

    def fileset(self):
        """
        Returns a fileset definition that can be fed to a coffea processor.

        The `MultiSample` samples are unrolled for processing. See
        `SampleManager.group` for merging processed samples.
        """
        fileset={}
        for samplename,sample in self.samples.items():
            if type(sample) is Sample:
                fileset[samplename]=sample.data
            elif type(sample) is MultiSample:
                for subname,subsample in sample.samples.items():
                    fileset[subname]=subsample.data
        return fileset

    def group(self):
        """
        Returns a group definition for a coffea `Hist` object that merges the
        defined `MultiSample`'s.
        """
        group={}
        for samplename,sample in self.samples.items():
            if type(sample) is MultiSample:
                group[samplename]=[subsamplename for subsamplename in sample.samples]
        return group