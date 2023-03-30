""" Contains Database Enum
"""
from enum import Enum


class DataNodeType(Enum):
    """Data Node Type Enum
    """
    PRIMARY = 1
    REPLICA = 2
