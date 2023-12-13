import os.path
import unittest

from eveviewer import io as eve_io
from eveviewer import dataset as eve_dataset


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


class TestEveHDF5Importer(unittest.TestCase):
    path_to_testdata = "/messung/sx700/daten/2023/KW44_23/PTB/00003.h5"

    def setUp(self):
        self.importer = eve_io.EveHDF5Importer()
        self.dataset = eve_dataset.Dataset()

    def test_instantiate_class(self):
        pass

    @unittest.skipUnless(os.path.exists(path_to_testdata), "No test data")
    def test_import_data(self):
        self.importer.source = self.path_to_testdata
        self.importer.import_into(self.dataset)
        self.assertTrue(self.dataset.data.data.any())

    @unittest.skipUnless(os.path.exists(path_to_testdata), "No test data")
    def test_import_data_adds_poscounter_as_device_data(self):
        self.importer.source = self.path_to_testdata
        self.importer.import_into(self.dataset)
        self.assertIn("PosCounter", self.dataset.device_data)
