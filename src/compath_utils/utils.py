# -*- coding: utf-8 -*-

import logging
import os

from pandas import DataFrame, Series

log = logging.getLogger(__name__)


def dict_to_df(d):
    return DataFrame(
        dict([
            (k, Series(list(v)))
            for k, v in d.items()
        ])
    )


def write_dict(d, directory, module_name):
    gene_sets_df = dict_to_df(d)

    path = os.path.join(directory, '{}_gene_sets.xlsx'.format(module_name))

    log.info("Gene sets exported to '{}".format(path))

    gene_sets_df.to_excel(path, index=False)
