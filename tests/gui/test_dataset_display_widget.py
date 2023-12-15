import os
import unittest

from PySide6 import QtCore, QtWidgets

from eveviewer.gui import dataset_display_widget


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
        self.widget._update_ui()
        self.assertEqual(
            os.path.split(dataset_name)[1],
            self.widget._dataset_combobox.itemText(0),
        )

    def test_dataset_in_model_sets_axes_comboboxes(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        axes = self.widget.model.datasets[dataset_name].devices
        self.widget._update_ui()
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
        self.widget._dataset_combobox.setModelColumn(1)
        axes = self.widget.model.datasets[dataset_names[1]].devices
        self.widget._update_ui()
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
        self.widget._update_ui()
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
