#!/usr/bin/python
# -*- coding: utf-8 -*-

# recorbra2
# Python 3.10

"""
A extenal script for basic independent functions
"""


import enum


class eTreatPathType(enum.Enum):
    TREATPATH_FOLDER        = 0,
    TREATPATH_FILE          = 1


def treat_path(path, type):
    path = path.replace("\\", "/")

    if (type == eTreatPathType.TREATPATH_FOLDER):
        path += "/" * (path[-1] != "/")  # Add forward-slash on to the end if it doesn't exist
    
    elif (type == eTreatPathType.TREATPATH_FILE) and (path[-1] == "/"):
        path = path[:-1]  # Remove the last character if it's a forward-slash

    return path