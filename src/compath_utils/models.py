# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

__all__ = [
    'ComPathPathway',
]


class ComPathPathway(ABC):
    """This is the abstract class that the Pathway model in a ComPath repository should extend"""

    @abstractmethod
    def get_gene_set(self):
        """Returns the genes associated with the pathway (gene set). Note this function restricts to HGNC symbols genes

        :return: Returns a set of protein models that all have names
        """
