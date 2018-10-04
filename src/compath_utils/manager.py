# -*- coding: utf-8 -*-

"""This module contains the abstract manager that all ComPath managers should extend."""

import logging
import os
from collections import Counter
from typing import Iterable, List, Mapping, Optional, Set, Tuple

import click
import itertools as itt

from bio2bel import AbstractManager
from bio2bel.manager.bel_manager import BELManagerMixin
from bio2bel.manager.flask_manager import FlaskMixin
from bio2bel.manager.namespace_manager import BELNamespaceManagerMixin
from .exc import CompathManagerPathwayModelError, CompathManagerProteinModelError
from .models import ComPathPathway
from .utils import write_dict

__all__ = [
    'CompathManager',
]

log = logging.getLogger(__name__)


class CompathManager(AbstractManager, BELNamespaceManagerMixin, BELManagerMixin, FlaskMixin):
    """This is the abstract class that all ComPath managers should extend."""

    #: The standard pathway SQLAlchemy model
    pathway_model: ComPathPathway = None

    #: Put the standard database identifier (ex wikipathways_id or kegg_id)
    pathway_model_identifier_column = None

    #: The standard protein SQLAlchemy model
    protein_model: ComPathPathway = None

    def __init__(self, *args, **kwargs):
        """Doesn't let this class get instantiated if the pathway_model."""
        if self.pathway_model is None:
            raise CompathManagerPathwayModelError('did not set class-level variable pathway_model')

        if not self.namespace_model or self.namespace_model is ...:  # set namespace model if not already set
            self.namespace_model = self.pathway_model

        if not self.flask_admin_models or self.flask_admin_models is ...:  # set flask models if not already set
            self.flask_admin_models = [self.pathway_model, self.protein_model]

        # TODO use hasattr on class for checking this
        # if self.pathway_model_identifier_column is None:
        #     raise CompathManagerPathwayIdentifierError(
        #         'did not set class-level variable pathway_model_standard_identifer')

        if self.protein_model is None:
            raise CompathManagerProteinModelError('did not set class-level variable protein_model')

        super().__init__(*args, **kwargs)

    def is_populated(self) -> bool:
        """Check if the database is already populated."""
        return 0 < self._count_model(self.pathway_model)

    def _query_pathway(self):
        return self.session.query(self.pathway_model)

    def _query_protein(self):
        return self.session.query(self.protein_model)

    def _query_proteins_in_hgnc_list(self, gene_set: Iterable[str]) -> List[protein_model]:
        """Return the proteins in the database within the gene set query.

        :param gene_set: hgnc symbol lists
        :return: list of proteins models
        """
        return self._query_protein().filter(self.protein_model.hgnc_symbol.in_(gene_set)).all()

    def query_protein_by_hgnc(self, hgnc_symbol: str) -> List[protein_model]:
        """Return the proteins in the database matching a hgnc symbol.

        :param hgnc_symbol: hgnc symbol
        """
        return self._query_protein().filter(self.protein_model.hgnc_symbol == hgnc_symbol).all()

    def query_similar_hgnc_symbol(self, hgnc_symbol: str, top: Optional[int] = None) -> Optional[pathway_model]:
        """Filter genes by hgnc symbol.

        :param hgnc_symbol: hgnc_symbol to query
        :param top: return only X entries
        """
        similar_genes = self._query_protein().filter(self.protein_model.hgnc_symbol.contains(hgnc_symbol)).all()

        if top:
            return similar_genes[:top]

        return similar_genes

    def query_similar_pathways(self, pathway_name: str, top: Optional[int] = None) -> List[Tuple[str, str]]:
        """Filter pathways by name.

        :param pathway_name: pathway name to query
        :param top: return only X entries
        """
        similar_pathways = self._query_pathway().filter(self.pathway_model.name.contains(pathway_name)).all()

        similar_pathways = [
            (pathway.resource_id, pathway.name)
            for pathway in similar_pathways
        ]

        if top:
            return similar_pathways[:top]

        return similar_pathways

    def query_gene(self, hgnc_gene_symbol: str) -> List[Tuple[str, str, int]]:
        """Return the pathways associated with a gene.

        :param hgnc_gene_symbol: HGNC gene symbol
        :return:  associated with the gene
        """
        pathway_ids = set(itt.chain.from_iterable(
            gene.get_pathways_ids()
            for gene in self.query_protein_by_hgnc(hgnc_gene_symbol)
        ))

        enrichment_results = []

        for pathway_id in pathway_ids:
            pathway = self.get_pathway_by_id(pathway_id)

            pathway_gene_set = pathway.get_gene_set()  # Pathway gene set

            enrichment_results.append((pathway_id, pathway.name, len(pathway_gene_set)))

        return enrichment_results

    def query_gene_set(self, hgnc_gene_symbols: Iterable[str]) -> Mapping[str, Mapping]:
        """Calculate the pathway counter dictionary.

        :param hgnc_gene_symbols: An iterable of HGNC gene symbols to be queried
        :return: Enriched pathways with mapped pathways/total
        """
        proteins = self._query_proteins_in_hgnc_list(hgnc_gene_symbols)

        pathways_lists = [
            protein.get_pathways_ids()
            for protein in proteins
        ]

        # Flat the pathways lists and applies Counter to get the number matches in every mapped pathway
        pathway_counter = Counter(itt.chain(*pathways_lists))

        enrichment_results = dict()

        for pathway_id, proteins_mapped in pathway_counter.items():
            pathway = self.get_pathway_by_id(pathway_id)

            pathway_gene_set = pathway.get_gene_set()  # Pathway gene set

            enrichment_results[pathway_id] = {
                "pathway_id": pathway_id,
                "pathway_name": pathway.name,
                "mapped_proteins": proteins_mapped,
                "pathway_size": len(pathway_gene_set),
                "pathway_gene_set": pathway_gene_set,
            }

        return enrichment_results

    @classmethod
    def _standard_pathway_identifier_filter(cls, pathway_id: str):
        """Get a SQLAlchemy filter for the standard pathway identifier."""
        return cls.pathway_model_identifier_column == pathway_id

    def get_pathway_by_id(self, pathway_id: str) -> Optional[pathway_model]:
        """Get a pathway by its database-specific identifier. Not to be confused with the standard column called "id".

        :param pathway_id: Pathway identifier
        """
        return self._query_pathway().filter(self._standard_pathway_identifier_filter(pathway_id)).one_or_none()

    def get_pathway_by_name(self, pathway_name: str) -> Optional[pathway_model]:
        """Get a pathway by its database-specific name.

        :param pathway_name: Pathway name
        """
        pathways = self._query_pathway().filter(self.pathway_model.name == pathway_name).all()

        if not pathways:
            return None

        return pathways[0]

    def get_all_pathways(self) -> List[pathway_model]:
        """Get all pathways stored in the database."""
        return self._query_pathway().all()

    def get_all_pathway_names(self) -> List[str]:
        """Get all pathway names stored in the database."""
        return [
            pathway.name
            for pathway in self._query_pathway().all()
        ]

    def get_all_hgnc_symbols(self) -> Set[str]:
        """Return the set of genes present in all Pathways."""
        return {
            gene.hgnc_symbol
            for pathway in self.get_all_pathways()
            for gene in pathway.proteins
            if pathway.proteins
        }

    def get_pathway_size_distribution(self) -> Mapping[str, int]:
        """Return pathway sizes.

        :return: pathway sizes
        """
        pathways = self.get_all_pathways()

        return {
            pathway.name: len(pathway.proteins)
            for pathway in pathways
            if pathway.proteins
        }

    def query_pathway_by_name(self, query: str, limit: Optional[int] = None) -> List[pathway_model]:
        """Return all pathways having the query in their names.

        :param query: query string
        :param limit: limit result query
        """
        q = self._query_pathway().filter(self.pathway_model.name.contains(query))

        if limit:
            q = q.limit(limit)

        return q.all()

    def export_gene_sets(self) -> Mapping[str, Set[str]]:
        """Return the pathway - genesets mapping."""
        return {
            pathway.name: {
                protein.hgnc_symbol
                for protein in pathway.proteins
            }
            for pathway in self._query_pathway().all()
        }

    def get_gene_distribution(self) -> Counter:
        """Return the proteins in the database within the gene set query.

        :return: pathway sizes
        """
        return Counter(
            gene.hgnc_symbol
            for pathway in self.get_all_pathways()
            if pathway.proteins
            for gene in pathway.proteins
        )

    @staticmethod
    def _add_cli_export(main: click.Group) -> click.Group:
        """Add the pathway export function to the CLI."""

        @main.command()
        @click.option('-d', '--directory', default=os.getcwd(), help='Defaults to CWD')
        @click.pass_obj
        def export_gene_sets(manager, directory):
            """Export all pathway - gene info to a excel file."""
            # https://stackoverflow.com/questions/19736080/creating-dataframe-from-a-dictionary-where-entries-have-different-lengths
            gene_sets_dict = manager.export_gene_sets()
            path = os.path.join(directory, f'{manager.module_name}_gene_sets.xlsx')
            write_dict(gene_sets_dict, path)

        return main

    @classmethod
    def get_cli(cls) -> click.Group:
        """Get a :mod:`click` main function to use as a command line interface."""
        main = super().get_cli()
        cls._add_cli_export(main)
        return main
