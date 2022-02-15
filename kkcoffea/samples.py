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
    def __init__(self, sampledef=None, datadir="."):
        """
        Parameters:
            - sampledef (str): path to sample definition file
            - datadir (str): path where all data files are located
        """
        self.datadir=datadir
        self.samples={}
        if sampledef is not None:
            self.add_sampledef(sampledef)

    def add_sampledef(self, sampledef):
        """
        Add a sample definition to the manager. A sample definition is a YAML
        file that contains sample and multisample definitions. The parsed
        result is appended to `this.samples`.

        The contents of keys other than `samples` are added as `self` members.

        An example of the syntax is.

        ```yaml
        config1: value1
        samples:
            - dsid: 123456
              data:
                - mysample.root
            - name: multisample1:
              samples:
                - dsid: 900000
                  data:
                    - file0.root
                - dsid: 900001
                  data:
                    - file1.root
        ```

        Parameters:
            - sampledef (str): path to sample definition file
        """
        with open(sampledef) as fh:
            data=yaml.safe_load(fh)

        # Store metadata
        for k in data.keys():
            if k=='samples':
                continue # skip, this is special
            setattr(self, k, data[k])

        # Loop over all samples and add them
        for sample in data['samples']:
            if 'samples' not in sample: # this is a single sample
                samplename,sample=self._create_sample(sample)
                self.samples[samplename]=sample
            else: # this is a multisample
                samplename=sample['name']
                subsamples={}
                for subsample in sample['samples']:
                    subsamplename,subsample=self._create_sample(subsample)
                    subsamples[subsamplename]=subsample
                sample=MultiSample(subsamples)
                self.samples[samplename]=sample

    def _create_sample(self, sample):
        """
        Creates a new `Sample` object based on a dictionary sample definition.


        Returns: `samplename`, `sampleobj`
        """

        # Get the name of the sample
        samplename=None
        if 'dsid' in sample:
            samplename=str(sample['dsid'])
        if 'name' in sample:
            samplename=sample['name']

        # Create the sample object
        sampleobj=Sample(data=[self.datadir+'/'+path for path in sample['data']])

        return samplename, sampleobj

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