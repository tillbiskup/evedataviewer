import datetime
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


class TestImporter(unittest.TestCase):
    def setUp(self):
        self.importer = eve_io.Importer()
        self.dataset = eve_dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_import_into_sets_dataset_id_to_source(self):
        source = "foo/bar/bla.blub"
        self.importer.source = source
        self.importer.import_into(self.dataset)
        self.assertEqual(self.dataset.id, source)

    def test_import_into_sets_dataset_label_to_filename_without_path(self):
        source = "foo/bar/bla.blub"
        self.importer.source = source
        self.importer.import_into(self.dataset)
        self.assertEqual(self.dataset.label, os.path.split(source)[1])


class TestDummyImporter(unittest.TestCase):
    def setUp(self):
        self.importer = eve_io.DummyImporter()
        self.dataset = eve_dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_import_adds_data_to_dataset(self):
        self.importer.import_into(self.dataset)
        self.assertTrue(self.dataset.data.data.any())

    def test_import_adds_device_data_to_dataset(self):
        self.importer.import_into(self.dataset)
        self.assertTrue(self.dataset.device_data.keys())

    def test_import_into_sets_dataset_id_to_source(self):
        source = "foo/bar/bla.blub"
        self.importer.source = source
        self.importer.import_into(self.dataset)
        self.assertEqual(self.dataset.id, source)

    def test_import_into_sets_dataset_label_to_filename_without_path(self):
        source = "foo/bar/bla.blub"
        self.importer.source = source
        self.importer.import_into(self.dataset)
        self.assertEqual(self.dataset.label, os.path.split(source)[1])

    def test_source_containing_init_creates_subscans(self):
        source = "foo/bar/__init__.py"
        self.importer.source = source
        self.importer.import_into(self.dataset)
        self.assertTrue(self.dataset.subscans["boundaries"])

    def test_dataset_with_subscans_sets_initial_current_subscan(self):
        source = "foo/bar/__init__.py"
        self.importer.source = source
        self.importer.import_into(self.dataset)
        self.assertEqual(-1, self.dataset.subscans["current"])


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

    @unittest.skipUnless(os.path.exists(path_to_testdata), "No test data")
    def test_import_into_sets_dataset_id_to_source(self):
        self.importer.source = self.path_to_testdata
        self.importer.import_into(self.dataset)
        self.assertEqual(self.dataset.id, self.importer.source)

    @unittest.skipUnless(os.path.exists(path_to_testdata), "No test data")
    def test_import_into_sets_dataset_label_to_filename_without_path(self):
        self.importer.source = self.path_to_testdata
        self.importer.import_into(self.dataset)
        self.assertEqual(
            self.dataset.label, os.path.split(self.importer.source)[1]
        )

    @unittest.skipUnless(os.path.exists(path_to_testdata), "No test data")
    def test_import_into_sets_start_date_of_measurement(self):
        self.importer.source = self.path_to_testdata
        self.importer.import_into(self.dataset)
        now = datetime.datetime.now()
        self.assertLess(
            self.dataset.metadata.measurement.start,
            now.replace(minute=now.minute - 1),
        )

    @unittest.skipUnless(os.path.exists(path_to_testdata), "No test data")
    def test_import_into_sets_end_date_of_measurement(self):
        self.importer.source = self.path_to_testdata
        self.importer.import_into(self.dataset)
        now = datetime.datetime.now()
        self.assertLess(
            self.dataset.metadata.measurement.end,
            now.replace(minute=now.minute - 1),
        )

    @unittest.skipUnless(os.path.exists(path_to_testdata), "No test data")
    def test_end_date_of_measurement_is_later_than_start_date(self):
        self.importer.source = self.path_to_testdata
        self.importer.import_into(self.dataset)
        self.assertLess(
            self.dataset.metadata.measurement.start,
            self.dataset.metadata.measurement.end,
        )
