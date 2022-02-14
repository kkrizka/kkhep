"""
Functions for managing local configurations for a project.
"""

import yaml
import os

def load_settings(cfgpath, env):
    """
    Loads the contents of the `cfgpath` YAML file and updates the contents of
    `env` with the values.

    If `cfgpath` does not exists, then the function silently returns. This is
    when no override of the settings is desired.
    """
    if not os.path.exists(cfgpath):
        return # no local configuration found
    cfg = yaml.safe_load(open(cfgpath))

    env.update(cfg)

