import unittest
import datetime

import matplotlib.pyplot as plt
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

    def test_set_preferred_data_sets_axes_quantities(self):
        device_names = ["foo", "bar", "bla", "blub"]
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        for idx, device in enumerate(device_names):
            data = eve_dataset.Data()
            data.data = np.ones(10) + idx
            data.axes[0].quantity = f"{device}_index"
            data.axes[0].unit = "index"
            data.axes[1].quantity = f"{device}"
            data.axes[1].unit = f"{device}_unit"
            self.dataset.device_data[device] = data
        self.dataset.preferred_data = ["bla", "blub"]
        self.assertEqual(self.dataset.data.axes[0].quantity, "bla")
        self.assertEqual(self.dataset.data.axes[0].unit, "bla_unit")
        self.assertEqual(self.dataset.data.axes[1].quantity, "blub")
        self.assertEqual(self.dataset.data.axes[1].unit, "blub_unit")

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

    def test_devices_returns_list_of_device_names(self):
        device_names = ["foo", "bar", "bla", "blub"]
        for idx, device in enumerate(device_names):
            data = eve_dataset.Data()
            data.data = np.ones(10) + idx
            self.dataset.device_data[device] = data
        self.assertListEqual(self.dataset.devices, device_names)

    def test_subscan_returns_data_object(self):
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        self.dataset.subscans["boundaries"] = [[0, 5], [5, 10]]
        self.dataset.subscans["current"] = 0
        self.assertIsInstance(self.dataset.subscan, eve_dataset.Data)

    def test_subscan_returns_current_subscan_of_data(self):
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        self.dataset.subscans["boundaries"] = [[0, 5], [5, 10]]
        self.dataset.subscans["current"] = 0
        slice_ = slice(
            *self.dataset.subscans["boundaries"][
                self.dataset.subscans["current"]
            ]
        )
        data = self.dataset.subscan
        np.testing.assert_allclose(
            data.data,
            self.dataset.data.data[slice_],
        )
        np.testing.assert_allclose(
            data.axes[0].values,
            self.dataset.data.axes[0].values[slice_],
        )

    def test_subscan_does_not_modify_data(self):
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        length = len(self.dataset.data.data)
        self.dataset.subscans["boundaries"] = [[0, 5], [5, 10]]
        self.dataset.subscans["current"] = 0
        _ = self.dataset.subscan
        self.assertEqual(len(self.dataset.data.data), length)

    def test_subscan_with_current_subscan_set_to_minus_one_returns_data(self):
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        self.dataset.subscans["boundaries"] = [[0, 5], [5, 10]]
        self.dataset.subscans["current"] = -1
        data = self.dataset.subscan
        np.testing.assert_allclose(
            data.data,
            self.dataset.data.data,
        )
        np.testing.assert_allclose(
            data.axes[0].values,
            self.dataset.data.axes[0].values,
        )

    def test_plot_plots_data(self):
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        fig, ax = plt.subplots()
        self.dataset.plot(figure=fig)
        np.testing.assert_allclose(
            ax.lines[0].get_ydata(),
            self.dataset.data.data,
        )

    def test_plot_with_subscan_plots_subscan(self):
        self.dataset.data.data = np.zeros(10)
        self.dataset.data.axes[0].values = np.linspace(1, 10, 10)
        self.dataset.subscans["boundaries"] = [[0, 5], [5, 10]]
        self.dataset.subscans["current"] = 0
        data = self.dataset.subscan
        fig, ax = plt.subplots()
        self.dataset.plot(figure=fig)
        np.testing.assert_allclose(
            ax.lines[0].get_ydata(),
            data.data,
        )

    def test_metadata_is_metadata_object(self):
        self.assertIsInstance(
            self.dataset.metadata, eve_dataset.DatasetMetadata
        )


class TestDatasetMetadata(unittest.TestCase):
    def setUp(self):
        self.dataset_metadata = eve_dataset.DatasetMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_measurement_metadata(self):
        self.assertTrue(hasattr(self.dataset_metadata, "measurement"))
        self.assertIsInstance(
            self.dataset_metadata.measurement, eve_dataset.MeasurementMetadata
        )


class TestMeasurementMetadata(unittest.TestCase):
    def setUp(self):
        self.measurement_metadata = eve_dataset.MeasurementMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = ["start", "end"]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.measurement_metadata, attribute))

    def test_start_is_datetime_object(self):
        self.assertIsInstance(
            self.measurement_metadata.start, datetime.datetime
        )

    def test_end_is_datetime_object(self):
        self.assertIsInstance(
            self.measurement_metadata.end, datetime.datetime
        )
