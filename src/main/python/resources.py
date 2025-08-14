from functools import cache

import json

import os.path as pth

def path(*name: str):
    """
    Returns the absolute path to the Java resource file.

    Assumes the resources are located in the 'resources' directory,
    one level up the cwd.

    :param name: The name of the resource file.
    :return: The absolute path to the resource file.
    """
    return pth.abspath(pth.join(pth.dirname(__file__), '..', 'resources', *name))

@cache
def config():
    """
    Reads the initial conditions from the JSON configuration file.

    :return: A dictionary containing the configuration.
    """
    config_path = path('initial_conditions.json')

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError as e:
        print(f"Error: The file '{config_path}' was not found.")
        raise e
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from '{config_path}'. Check file format.")
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
