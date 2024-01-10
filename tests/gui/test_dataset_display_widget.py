import os
import unittest

import matplotlib.pyplot as plt
from PySide6 import QtCore, QtWidgets, QtTest
import qtbricks.testing

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
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        for widget in self.widget._subscan_widgets:
            self.assertTrue(widget.isEnabled())

    def test_subscans_widgets_are_reenabled_if_dataset_has_subscans(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_names = ["/foo/bar/bla.blub", "/foo/bar/__init__.blub"]
        self.widget.model.datasets_to_display = [dataset_names[0]]
        self.widget.model.datasets_to_display = [dataset_names[1]]
        for widget in self.widget._subscan_widgets:
            self.assertTrue(widget.isEnabled())

    def test_subscans_widgets_display_number_of_total_subscans(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        n_subscans = len(
            self.widget.model.datasets[dataset_name].subscans["boundaries"]
        )
        self.assertEqual(
            str(n_subscans),
            self.widget._subscan_number_label.text(),
        )

    def test_changing_back_to_dataset_wo_subscans_resets_subscan_widgets(
        self,
    ):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_names = ["/foo/bar/__init__.blub", "/foo/bar/bla.blub"]
        self.widget.model.datasets_to_display = [dataset_names[0]]
        self.widget.model.datasets_to_display = [dataset_names[1]]
        self.assertEqual("0", self.widget._subscan_number_label.text())

    def test_subscans_edit_validator_has_correct_upper_limit(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        n_subscans = len(
            self.widget.model.datasets[dataset_name].subscans["boundaries"]
        )
        self.assertEqual(
            n_subscans,
            self.widget._subscan_current_edit.validator().top(),
        )

    def test_subscan_edit_set_beyond_upper_limit_sets_to_upper_limit(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        n_subscans = len(
            self.widget.model.datasets[dataset_name].subscans["boundaries"]
        )
        qtbricks.testing.qtest_enter_text(
            widget=self.widget._subscan_current_edit, text=str(n_subscans + 1)
        )
        self.assertEqual(
            str(n_subscans),
            self.widget._subscan_current_edit.text(),
        )

    def test_subscan_edit_sets_current_subscan_in_dataset(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        qtbricks.testing.qtest_enter_text(
            widget=self.widget._subscan_current_edit, text="1"
        )
        # Important: Offset of 1, as "-1" means temporarily disable subscans.
        self.assertEqual(
            int(self.widget._subscan_current_edit.text()) - 1,
            self.widget.model.datasets[dataset_name].subscans["current"],
        )

    def test_subscan_decrement_button_disabled_when_subscans_zero(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.assertFalse(self.widget._subscan_decrement_button.isEnabled())

    def test_subscan_increment_button_disabled_when_subscans_max(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        n_subscans = len(
            self.widget.model.datasets[dataset_name].subscans["boundaries"]
        )
        qtbricks.testing.qtest_enter_text(
            widget=self.widget._subscan_current_edit,
            text=str(n_subscans),
        )
        self.assertFalse(self.widget._subscan_increment_button.isEnabled())

    def test_subscan_increment_button_sets_current_subscan(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        QtTest.QTest.mouseClick(
            self.widget._subscan_increment_button,
            QtCore.Qt.MouseButton.LeftButton,
        )
        # Hint: We start with -1, meaning temporarily disable subscans.
        self.assertEqual(
            0,
            self.widget.model.datasets[dataset_name].subscans["current"],
        )

    def test_subscan_increment_button_updates_widgets(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        QtTest.QTest.mouseClick(
            self.widget._subscan_increment_button,
            QtCore.Qt.MouseButton.LeftButton,
        )
        self.assertEqual(
            "1",
            self.widget._subscan_current_edit.text(),
        )

    def test_subscan_decrement_button_sets_current_subscan(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        n_subscans = len(
            self.widget.model.datasets[dataset_name].subscans["boundaries"]
        )
        qtbricks.testing.qtest_enter_text(
            widget=self.widget._subscan_current_edit, text=str(n_subscans)
        )
        QtTest.QTest.mouseClick(
            self.widget._subscan_decrement_button,
            QtCore.Qt.MouseButton.LeftButton,
        )
        # Hint: Zero-based indexing only in dataset, not in display
        self.assertEqual(
            n_subscans - 2,
            self.widget.model.datasets[dataset_name].subscans["current"],
        )

    def test_subscan_decrement_button_updates_widget(self):
        # Convention from DummyImporter: __init__ in filename creates subscans
        dataset_name = "/foo/bar/__init__.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        n_subscans = len(
            self.widget.model.datasets[dataset_name].subscans["boundaries"]
        )
        qtbricks.testing.qtest_enter_text(
            widget=self.widget._subscan_current_edit, text=str(n_subscans)
        )
        QtTest.QTest.mouseClick(
            self.widget._subscan_decrement_button,
            QtCore.Qt.MouseButton.LeftButton,
        )
        self.assertEqual(
            str(n_subscans - 1),
            self.widget._subscan_current_edit.text(),
        )

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

    def test_changing_x_axis_scale_combobox_sets_axis_scale(self):
        fig, ax = plt.subplots()
        self.widget.model.figure = fig
        self.widget._x_axis_scale_combobox.setCurrentIndex(1)
        self.assertEqual(
            ax.get_xscale(),
            self.widget._x_axis_scale_combobox.currentText(),
        )

    def test_changing_y_axis_scale_combobox_sets_axis_scale(self):
        fig, ax = plt.subplots()
        self.widget.model.figure = fig
        self.widget._y_axis_scale_combobox.setCurrentIndex(1)
        self.assertEqual(
            ax.get_yscale(),
            self.widget._y_axis_scale_combobox.currentText(),
        )

    def test_deselecting_any_dataset_clears_x_axis_combobox(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.assertTrue(self.widget._x_axis_combobox.currentText())
        self.widget.model.datasets_to_display = []
        self.assertFalse(self.widget._x_axis_combobox.currentText())

    def test_deselecting_any_dataset_clears_y_axis_combobox(self):
        dataset_name = "/foo/bar/bla.blub"
        self.widget.model.datasets_to_display = [dataset_name]
        self.assertTrue(self.widget._y_axis_combobox.currentText())
        self.widget.model.datasets_to_display = []
        self.assertFalse(self.widget._y_axis_combobox.currentText())

    def test_changing_dataset_selection_updates_model(self):
        dataset_names = ["/foo/bar/bla.blub", "/foo/bar/foobar.blub"]
        self.widget.model.datasets_to_display = dataset_names
        self.widget._dataset_combobox.setCurrentIndex(1)
        self.assertEqual(dataset_names[1], self.widget.model.current_dataset)

    def test_clearing_dataset_selection_updates_model(self):
        dataset_names = ["/foo/bar/bla.blub", "/foo/bar/foobar.blub"]
        self.widget.model.datasets_to_display = dataset_names
        self.widget._dataset_combobox.setCurrentIndex(-1)
        self.assertEqual("", self.widget.model.current_dataset)
