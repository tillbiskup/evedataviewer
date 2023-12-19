import unittest

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication

import eveviewer.dataset
from eveviewer.gui import model as gui_model


class SignalReceiver:
    """
    Context manager class detecting whether a QSignal has been emitted.

    Adapted from https://stackoverflow.com/a/48128768
    """

    def __init__(self, test, signal, *args):
        self.test = test
        self.signal = signal
        self.called = False
        self.expected_args = args
        self.actual_args = None

    def slot(self, *args):
        self.actual_args = args
        self.called = True

    def __enter__(self):
        self.signal.connect(self.slot)

    def __exit__(self, e, msg, traceback):
        if e:
            raise e(msg)
        self.test.assertTrue(self.called, "Signal not called!")
        self.test.assertEqual(
            self.expected_args,
            self.actual_args,
            f"""Signal arguments don't match!
            actual:   {self.actual_args}
            expected: {self.expected_args}""",
        )


class TestCaseUsingQSignals(unittest.TestCase):
    """
    Test class for testing whether a QSignal has been emitted.

    Adapted from https://stackoverflow.com/a/48128768
    """

    def setUp(self):
        """Create the QApplication instance"""
        _instance = QApplication.instance()
        if not _instance:
            _instance = QApplication([])
        self.app = _instance

    def tearDown(self):
        """Delete the reference owned by self"""
        del self.app

    def assertSignalReceived(self, signal, args):
        return SignalReceiver(self, signal, args)


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = gui_model.Model()

    def test_instantiate_class(self):
        pass

    def test_setting_datasets_to_display_loads_dataset(self):
        dataset = "foo"
        self.model.datasets_to_display = [dataset]
        self.assertIn(dataset, self.model.datasets)

    def test_loaded_dataset_is_dataset_object(self):
        dataset = "foo"
        self.model.datasets_to_display = [dataset]
        self.assertIsInstance(
            self.model.datasets[dataset], eveviewer.dataset.Dataset
        )

    def test_setting_multiple_datasets_to_display_loads_datasets(self):
        datasets = ["foo", "bar"]
        self.model.datasets_to_display = datasets
        for dataset in datasets:
            self.assertIn(dataset, self.model.datasets)

    def test_appending_dataset_loads_dataset(self):
        dataset = "foo"
        self.model.datasets_to_display.append(dataset)
        self.assertIn(dataset, self.model.datasets)

    def test_removing_dataset_from_datasets_to_display_keeps_dataset(self):
        dataset = "foo"
        self.model.datasets_to_display.append(dataset)
        self.model.datasets_to_display.remove(dataset)
        self.assertIn(dataset, self.model.datasets)
        self.assertNotIn(dataset, self.model.datasets_to_display)

    def test_load_data_adds_dataset(self):
        dataset = "foo"
        self.model.load_data(filename=dataset)
        self.assertIn(dataset, self.model.datasets)

    def test_plot_data_adds_data_to_figure(self):
        fig, ax = plt.subplots()
        self.assertFalse(ax.has_data())
        self.model.figure = fig
        self.model.datasets_to_display = ["foo"]
        self.model.plot_data()
        self.assertTrue(ax.has_data())

    def test_plot_data_clears_axes_before_plotting(self):
        fig, ax = plt.subplots()
        ax.plot([1.0, 2.0], [0.0, 1.0])
        self.model.figure = fig
        self.model.datasets_to_display = ["foo"]
        self.model.plot_data()
        self.assertEqual(1, len(ax.get_lines()))

    def test_appending_dataset_displays_dataset(self):
        dataset = "foo"
        fig, ax = plt.subplots()
        self.model.figure = fig
        self.assertFalse(ax.has_data())
        self.model.datasets_to_display.append(dataset)
        self.assertTrue(ax.has_data())

    def test_alternative_display_mode_calls_respective_method(self):
        class MockModel(gui_model.Model):
            def __init__(self):
                super().__init__()
                self.method_called = False

            def print_data(self):
                self.method_called = True

        mock = MockModel()
        mock._display_mode = "print"
        mock.display_data()
        self.assertTrue(mock.method_called)

    def test_set_datasets_to_display_to_identical_list_doesnt_plot(self):
        class MockModel(gui_model.Model):
            def __init__(self):
                super().__init__()
                self.method_called = False

            def display_data(self):
                super().display_data()
                self.method_called = True

        mock = MockModel()
        mock.datasets_to_display = ["foo"]
        mock.method_called = False
        mock.datasets_to_display = ["foo"]
        self.assertFalse(mock.method_called)


class TestModelSignals(TestCaseUsingQSignals):
    def setUp(self):
        super().setUp()
        self.model = gui_model.Model()

    def test_dataset_selection_changed_signal_can_be_emitted(self):
        with self.assertSignalReceived(
            self.model.dataset_selection_changed, []
        ):
            self.model.dataset_selection_changed.emit([])

    def test_change_in_datasets_emits_signal(self):
        datasets = ["foo.bla", "bar.blub"]
        with self.assertSignalReceived(
            self.model.dataset_selection_changed, datasets
        ):
            self.model.datasets_to_display = datasets
