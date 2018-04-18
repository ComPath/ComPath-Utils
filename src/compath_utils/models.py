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

    @property
    @abstractmethod
    def resource_id(self):
        """Returns the database-specific resource identifier (will be a SQLAlchemy Column instance)"""

    @property
    @abstractmethod
    def url(self):
        """Returns the URL to the resource, usually based in the identifer for this pathway

        :rtype: str


        Example for WikiPathways:

        .. code-block:: python

            >>> @property
            >>> def url(self):
            >>>     return 'https://www.wikipathways.org/index.php/Pathway:{}'.format(self.wikipathways_id)
        """
