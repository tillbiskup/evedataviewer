import unittest

from eveviewer import dataset as eve_dataset
from eveviewer import io as eve_io


class TestDataset(unittest.TestCase):
    def setUp(self):
        self.dataset = eve_dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_import_from_loads_data(self):
        importer_factory = eve_io.ImporterFactory()
        importer = importer_factory.get_importer()
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.data.any())
