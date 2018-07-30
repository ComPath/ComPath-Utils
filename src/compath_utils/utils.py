# -*- coding: utf-8 -*-

"""Utilities for ComPath Utilities (yo dawg)."""

import logging
import os

from pandas import DataFrame, Series

logger = logging.getLogger(__name__)


def dict_to_df(data):
    """Convert a dictionary to a DataFrame.

    :type data: dict
    :rtype: pandas.DataFrame
    """
    return DataFrame({
        key: Series(list(values))
        for key, values in data.items()
    })


def write_dict(data, directory, module_name):
    """Write a dictionary to a file as an Excel document."""
    gene_sets_df = dict_to_df(data)

    path = os.path.join(directory, '{}_gene_sets.xlsx'.format(module_name))

    logger.info("Gene sets exported to %s", path)

    gene_sets_df.to_excel(path, index=False)
