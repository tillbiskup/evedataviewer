import unittest

from PySide6 import QtCore, QtWidgets

from evedataviewer.gui import measurement_characteristics_widget


class TestMeasurementCharacteristicsWidget(unittest.TestCase):
    def setUp(self):
        self.app = (
            QtWidgets.QApplication.instance() or QtWidgets.QApplication()
        )
        self.widget = (
            measurement_characteristics_widget.MeasurementCharacteristicsWidget()
        )
        self.addCleanup(self.release_qt_resources)

    def release_qt_resources(self):
        self.widget.deleteLater()
        self.app.sendPostedEvents(event_type=QtCore.QEvent.DeferredDelete)
        self.app.processEvents()

    def test_instantiate_class(self):
        pass

    def test_time_start_displays_correct_time(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        dataset = self.widget.model.datasets[dataset_name]
        self.assertEqual(
            dataset.metadata.measurement.start.isoformat(
                sep=" ", timespec="seconds"
            ),
            self.widget._time_start_value_label.text(),
        )

    def test_time_end_displays_correct_time(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        dataset = self.widget.model.datasets[dataset_name]
        self.assertEqual(
            dataset.metadata.measurement.end.isoformat(
                sep=" ", timespec="seconds"
            ),
            self.widget._time_end_value_label.text(),
        )

    def test_duration_displays_correct_time(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        dataset = self.widget.model.datasets[dataset_name]
        duration = dataset.metadata.measurement.end.replace(
            microsecond=0
        ) - dataset.metadata.measurement.start.replace(microsecond=0)
        self.assertEqual(
            str(duration),
            self.widget._duration_value_label.text(),
        )

    def test_duration_displays_correct_string(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        dataset = self.widget.model.datasets[dataset_name]
        self.assertEqual(
            dataset.metadata.measurement.location,
            self.widget._location_value_label.text(),
        )

    def test_delecting_dataset_clears_time_start(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.widget.model.current_dataset = ""
        self.assertFalse(self.widget._time_start_value_label.text())

    def test_delecting_dataset_clears_time_end(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.widget.model.current_dataset = ""
        self.assertFalse(self.widget._time_end_value_label.text())

    def test_delecting_dataset_clears_duration(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.widget.model.current_dataset = ""
        self.assertFalse(self.widget._duration_value_label.text())

    def test_delecting_dataset_clears_location(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.widget.model.current_dataset = ""
        self.assertFalse(self.widget._location_value_label.text())
