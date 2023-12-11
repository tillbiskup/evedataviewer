import unittest

from eveviewer import io as eve_io


class TestImporterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = eve_io.ImporterFactory()

    def test_instantiate_class(self):
        pass

    def test_get_importer_returns_importer(self):
        importer = self.factory.get_importer()
        self.assertIsInstance(importer, eve_io.Importer)

    def test_get_importer_with_h5_extension_gets_eveh5importer(self):
        importer = self.factory.get_importer(source="foo.h5")
        self.assertIsInstance(importer, eve_io.EveHDF5Importer)
