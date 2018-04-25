# -*- coding: utf-8 -*-

import logging
import os

import click
from pandas import DataFrame, Series

log = logging.getLogger(__name__)


def add_cli_export(main):
    """Adds the pathwat export function to the CLI"""

    @main.command()
    @click.option('-d', '--directory', default=os.getcwd(), help='Defaults to CWD')
    @click.pass_obj
    def export(manager, directory):
        """Export all pathway - gene info to a excel file"""

        log.info("Querying the database")

        # https://stackoverflow.com/questions/19736080/creating-dataframe-from-a-dictionary-where-entries-have-different-lengths
        genesets = DataFrame(
            dict([
                (k, Series(list(v)))
                for k, v in manager.export_genesets().items()
            ])
        )

        path = os.path.join(directory, '{}_gene_sets.xlsx'.format(manager.module_name))

        log.info("Geneset exported to '{}".format(path))

        genesets.to_excel(path, index=False)
