import os
import unittest

from PySide6 import QtCore, QtWidgets

from eveviewer.gui import dataset_display_widget, model


class TestDatasetDisplayWidget(unittest.TestCase):
    def setUp(self):
        self.app = (
            QtWidgets.QApplication.instance() or QtWidgets.QApplication()
        )
        self.widget = dataset_display_widget.DatasetDisplayWidget()
        self.addCleanup(self.release_qt_resources)

    def release_qt_resources(self):
        self.widget.deleteLater()
        self.app.sendPostedEvents(event_type=QtCore.QEvent.DeferredDelete)
        self.app.processEvents()

    def test_instantiate_class(self):
        pass

    def test_dataset_in_model_appears_in_combobox(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.assertEqual(
            os.path.split(dataset_name)[1],
            self.widget._dataset_combobox.itemText(0),
        )

    def test_dataset_in_model_sets_axes_comboboxes(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        axes = self.widget.model.datasets[dataset_name].devices
        self.assertListEqual(
            axes,
            [
                self.widget._x_axis_combobox.itemText(idx)
                for idx in range(self.widget._x_axis_combobox.count())
            ],
        )
        self.assertListEqual(
            axes,
            [
                self.widget._y_axis_combobox.itemText(idx)
                for idx in range(self.widget._y_axis_combobox.count())
            ],
        )

    def test_axes_comboboxes_show_axes_of_selected_dataset(self):
        dataset_names = ["/foo/bar/bla.blub", "/foo/bar/foobar.blub"]
        self.widget.model.datasets_to_display = dataset_names
        self.widget._dataset_combobox.setCurrentIndex(1)
        axes = self.widget.model.datasets[dataset_names[1]].devices
        self.assertListEqual(
            axes,
            [
                self.widget._x_axis_combobox.itemText(idx)
                for idx in range(self.widget._x_axis_combobox.count())
            ],
        )
        self.assertListEqual(
            axes,
            [
                self.widget._y_axis_combobox.itemText(idx)
                for idx in range(self.widget._y_axis_combobox.count())
            ],
        )

    def test_axes_comboboxes_select_preferred_axes(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        axes = self.widget.model.datasets[dataset_name].preferred_data
        self.assertEqual(
            axes[0],
            self.widget._x_axis_combobox.itemText(
                self.widget._x_axis_combobox.currentIndex()
            ),
        )
        self.assertEqual(
            axes[1],
            self.widget._y_axis_combobox.itemText(
                self.widget._y_axis_combobox.currentIndex()
            ),
        )

    def test_subscans_widgets_are_disabled_if_dataset_has_no_subscans(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.widget.model.datasets[dataset_name].subscans["boundaries"] = []
        for widget in self.widget._subscan_widgets:
            self.assertFalse(widget.isEnabled())

    def test_subscans_widgets_are_enabled_if_dataset_has_subscans(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.widget.model.datasets[dataset_name].subscans["boundaries"] = [
            0,
            42,
        ]
        self.widget._update_ui()  # TODO: Replace with signal if possible
        for widget in self.widget._subscan_widgets:
            self.assertTrue(widget.isEnabled())

    def test_subscans_widgets_are_reenabled_if_dataset_has_subscans(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.widget.model.datasets[dataset_name].subscans["boundaries"] = [
            0,
            42,
        ]
        self.widget._update_ui()  # TODO: Replace with signal if possible
        for widget in self.widget._subscan_widgets:
            self.assertTrue(widget.isEnabled())

    def test_changing_model_still_updates_widget(self):
        self.widget.model = model.Model()
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.assertEqual(
            os.path.split(dataset_name)[1],
            self.widget._dataset_combobox.itemText(0),
        )

    def test_changing_x_axis_combobox_sets_preferred_axis_in_dataset(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        axes = self.widget.model.datasets[dataset_name].devices
        self.widget._x_axis_combobox.setCurrentIndex(1)
        self.assertEqual(
            self.widget.model.datasets[dataset_name]._preferred_data[0],
            axes[1],
        )

    def test_changing_y_axis_combobox_sets_preferred_axis_in_dataset(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        axes = self.widget.model.datasets[dataset_name].devices
        self.widget._y_axis_combobox.setCurrentIndex(1)
        self.assertEqual(
            self.widget.model.datasets[dataset_name]._preferred_data[1],
            axes[1],
        )
