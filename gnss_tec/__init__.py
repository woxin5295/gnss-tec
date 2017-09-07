# coding=utf-8
"""TEC === Tools to calculate total electron content value in the ionosphere
using data derived from global navigation satellite systems."""
import warnings

from .gnss import BAND_PRIORITY
from .rinex import ObsFileV2
from .rinex import ObsFileV3

# Shortcut
from .glo import collect_freq_nums

# General information
__version__ = '1.0.1'
__author__ = __maintainer__ = 'Ilya Zhivetiev'
__email__ = 'i.zhivetiev@gnss-lab.org'


def rnx(file, **kwargs):
    """Return a reader object which will iterate over observation records in
    the given file. Each iteration will return Tec object. The file can be any
    object which supports iterator protocol.

    Parameters
    ----------
    file : file-like object
    band_priority : dict
    glo_freq_nums : dict

    Returns
    -------
    reader : iterator
        Yields Tec object for each satellite of the epoch.
    """
    band_priority = kwargs.pop('band_priority', BAND_PRIORITY)
    glo_freq_nums = kwargs.pop('glo_freq_nums', {})

    if kwargs:
        for k in kwargs:
            msg = 'Unknown parameter: {}'.format(kwargs[k])
            raise ValueError(msg)

    try:
        row = next(file)
        rinex_version = float(row[:9])
        rinex_type = row[20]
        # rinex_sat_system = row[40]
    except StopIteration:
        msg = "rnx: Empty input file"
        warnings.warn(msg)
        raise StopIteration
    except ValueError:
        msg = "rnx: Unknown file type"
        raise ValueError(msg)

    if rinex_type.upper() != 'O':
        raise Exception('rnx: Not an observation file')

    rinex_reader = {
        (2.0, 2.1, 2.11, 2.12): ObsFileV2,
        (3.0, 3.01, 3.02, 3.03): ObsFileV3
    }

    reader = None
    for ver in rinex_reader:
        if rinex_version in ver:
            reader = rinex_reader[ver]

    if reader is None:
        msg = 'Unknown RINEX version: {}'.format(rinex_version)
        raise Exception(msg)

    return reader(
        file,
        version=rinex_version,
        band_priority=band_priority,
        glo_freq_nums=glo_freq_nums,
    )
