import unittest

import numpy as np

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

    def test_set_preferred_data_sets_axes_values(self):
        device_names = ["foo", "bar", "bla", "blub"]
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        for idx, device in enumerate(device_names):
            data = eve_dataset.Data()
            data.data = np.ones(10) + idx
            self.dataset.device_data[device] = data
        self.dataset.preferred_data = ["bla", "bar"]
        np.testing.assert_allclose(
            self.dataset.data.axes[0].values,
            self.dataset.device_data["bla"].data,
        )

    def test_set_preferred_data_sets_data(self):
        device_names = ["foo", "bar", "bla", "blub"]
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        for idx, device in enumerate(device_names):
            data = eve_dataset.Data()
            data.data = np.ones(10) + idx
            self.dataset.device_data[device] = data
        self.dataset.preferred_data = ["bla", "blub"]
        np.testing.assert_allclose(
            self.dataset.data.data,
            self.dataset.device_data["blub"].data,
        )

    def test_set_preferred_data_with_unknown_key_raises(self):
        device_names = ["foo", "bar", "bla", "blub"]
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        for idx, device in enumerate(device_names):
            data = eve_dataset.Data()
            data.data = np.ones(10) + idx
            self.dataset.device_data[device] = data
        with self.assertRaises(KeyError):
            self.dataset.preferred_data = ["unknown_device", "bar"]
            self.dataset.preferred_data = ["foo", "unknown_device"]
