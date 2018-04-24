# -*- coding: utf-8 -*-

"""Tests errors thrown for improperly implemented ComPath managers."""

import unittest

from compath_utils import CompathManager, CompathManagerPathwayModelError, CompathManagerProteinModelError
from sqlalchemy.ext.declarative import declarative_base

from bio2bel.testing import TemporaryConnectionMethodMixin

Base = declarative_base()


class ManagerMissingFunctions(CompathManager):
    """Test ComPath manager for abstract class."""

    module_name = 'test'

    @property
    def _base(self):
        return Base


class ManagerMissingPathway(ManagerMissingFunctions):
    """Test ComPath manager for abstract class."""

    def get_pathway_by_id(self, pathway_id):
        pass

    def get_pathway_names_to_ids(self):
        pass

    def populate(self, *args, **kwargs):
        pass

    def query_gene_set(self, gene_set):
        pass


class ManagerMissingProtein(ManagerMissingPathway):
    pathway_model = object()


class ManagerOkay(ManagerMissingProtein):
    protein_model = object()


class TestManagerFailures(unittest.TestCase):
    """Tests bad implementations of the manager"""

    def test_abstract_methods(self):
        with self.assertRaises(TypeError):
            ManagerMissingFunctions()

    def test_pathway_model_error(self):
        with self.assertRaises(CompathManagerPathwayModelError):
            ManagerMissingPathway()

    def test_protein_model_error(self):
        with self.assertRaises(CompathManagerProteinModelError):
            ManagerMissingProtein()


class TestManager(TemporaryConnectionMethodMixin):
    def test_instantiation(self):
        ManagerOkay(connection=self.connection)
