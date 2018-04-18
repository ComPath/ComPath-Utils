import unittest

from compath_utils import CompathManager, CompathManagerPathwayModelError


class TestManager(unittest.TestCase):

    def test_abstract_methods(self):
        class Manager(CompathManager):
            module_name = 'test'

            @property
            def base(self):
                return

        with self.assertRaises(TypeError):
            Manager()

    def test_pathway_model_error(self):
        class Manager(CompathManager):
            module_name = 'test'

            @property
            def base(self):
                return

            def get_pathway_by_id(self, pathway_id):
                pass

            def get_pathway_names_to_ids(self):
                pass

            def populate(self, *args, **kwargs):
                pass

            def query_gene_set(self, gene_set):
                pass

        with self.assertRaises(CompathManagerPathwayModelError):
            Manager()
