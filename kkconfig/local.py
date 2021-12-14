"""
Defines a global variable called `config` that is filled with settings
corresponding to the analysis package configuration. 

The `config` variable isinitialized with the contents of `.kkhep.yaml` file if
it exists. It is set to `None` otherwise.
"""

import yaml
import os

config=None
if os.path.exists('.kkhep.yaml'):
    config = yaml.load(open('.kkhep.yaml'), Loader=yaml.FullLoader)

