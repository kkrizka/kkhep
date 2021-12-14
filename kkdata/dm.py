import yaml
import importlib

import pyspark
import pyspark.sql

import kkconfig.local

session = pyspark.sql.SparkSession.builder \
    .master("spark://localhost:7077") \
    .getOrCreate()

class DataManager:
    """
    A database of samples defined in a series of YAML files.

    # YAML Format
    See the `load_samples` docstring for more information on the expected
    format of the YAML file.

    # Sample Loaders
    The defined samples are turned into objects of the loader class. The
    loader class is reponsible for providing an interface for accessing
    the data stored in the sample (ie: create dataframe and add useful
    columns).

    # Data Paths
    The value of the local configuration variable called `datadir` is used for
    relative paths.

    # Generated Dataset ID (`dsid`)
    The data manager generates a unique dataset id (referred to as `dsid`)
    for every sample added. This is to help when sorting samples in
    subsequent objects (ie: dataframes consisting of multiple samples).

    The `dsid` is passed to the loader constructor.
    """
    def __init__(self, path=None):
        """
        Parameters:
         - path (str): Optionally load samples from YAML definition at `path`.
        """

        # Initialize a SQL context for storing data
        self.sql = session

        # Samples
        self.names={} # name -> dsid map
        self.samples={}

        if path is not None:
            self.load_samples(path)

    def load_samples(self,path):
        """
        Parse a YAML files with sample definitions and add them to the data
        manager instance.

        The format of each sample definition is as follows:
        ```yaml
        loader: 'loader.class'
        samples:
          sample1:
            file: 'dir'
            title: 'Example 1'
          sample2:
            file: 'dir/*'
            title: 'Example 2'
        ```

        The `loader` is the class (including package path) used to load
        and represent the sample. The constructor to the loader must have
        two positional arguments: `dsid` and `path`. The `dsid` is the
        generated ID for the sample (integer) and `path` is the full path,
        including `datadir` to the sample data.

        The `samples` is a list of samples. The key is the name of the
        sample referred to by subsequent code. The `file` value is the path
        (relative to local configuration `datadir`) to the sample data. The
        interpretation (ie: allowed wildcards) is up to the loader. Any
        remaining fields are set as members of the sample object.
        """
        datadef = yaml.load(open(path), Loader=yaml.FullLoader)

        #
        # variables
        datadir=kkconfig.local.config['datadir'] # location of all data

        #
        # initialize loader class
        parts=datadef['loader'].split('.')
        module='.'.join(parts[:-1])
        classn=parts[-1]
        m = importlib.import_module(module)
        c = getattr(m, classn)
        loader=c

        #
        # initialize samples
        for name,sample in datadef['samples'].items():
            file=datadir+"/"+sample.pop('file')
            self.add_sample(name, file, loader, **sample)

    def add_sample(self, name, path, loader, **kwargs):
        """
        Add sample to the data manager instance.

        The sample representation is stored as an instance of the loader
        class. The sample object is constructed by passing the sample
        `dsid` and absolute path to the constructor.

        Any optional keyword arguments are set as properties of the sample
        object.

        Parameters:
         - name (str): Name for sample reference
         - path (str): Absolute path to the sample data
         - loader (class): Loader class
         - **kwargs: Optional properties for sample object
        """
        # Next available DSID
        dsid=len(self.names)

        # Create sample
        self.samples[dsid]=loader(dsid,path,sql=self.sql)
        self.names[name]=dsid

        # Extra sample attributes
        for k,v in kwargs.items():
            self.samples[dsid].__setattr__(k, v)

    def __getitem__(self, key):
        """
        Return sample corresponding to `key`. The `key` can be either a
        string with the sample name or the `dsid` integer.
        """
        if type(key)==str:
            key=self.names[key]
        return self.samples[key]
