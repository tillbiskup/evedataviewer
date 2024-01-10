"""
Widget for displaying measurement characteristics.

**Purpose:** For each individual dataset, a series of crucial
characteristics of the measurement should be displayed.

**Design principles:** The widget should be as self-contained and
self-consistent as possible, corresponding with the model of the main window
giving access to the datasets and the currently selected dataset.

**Limitations:** This widget is meant to present information (metadata)
of the respective dataset. Actively setting display options of the
individual datasets currently displayed should be handled by other widgets.
In short: This widget is entirely read-only.
"""

from PySide6 import QtWidgets, QtCore

from eveviewer.gui import model as gui_model


class MeasurementCharacteristicsWidget(QtWidgets.QWidget):
    """
    Display measurement characteristics of individual datasets.

    For each individual dataset, crucial characteristics of the measurement
    performed (such as its timing and location) should be directly
    accessible to the user.

    Note that the widget is currently entirely read-only.
    """

    def __init__(self):
        super().__init__()

        self._model = gui_model.Model()
        self._model.current_dataset_changed.connect(
            self._update_ui, QtCore.Qt.UniqueConnection
        )

        # Define all UI elements (widgets) here as non-public attributes
        self._time_start_label = QtWidgets.QLabel()
        self._time_start_value_label = QtWidgets.QLabel()
        self._time_end_label = QtWidgets.QLabel()
        self._time_end_value_label = QtWidgets.QLabel()
        self._duration_label = QtWidgets.QLabel()
        self._duration_value_label = QtWidgets.QLabel()
        self._location_label = QtWidgets.QLabel()
        self._location_value_label = QtWidgets.QLabel()

        self._setup_ui()
        self._update_ui()

    @property
    def model(self):
        # noinspection PyUnresolvedReferences
        """
        Model of the Model--View architecture used by the widget.

        When setting the model, the
        :attr:`eveviewer.gui.model.Model.dataset_selection_changed` signal is
        connected to the widget update method.

        Parameters
        ----------
        model : :class:`eveviewer.gui.model.Model`
            The model used by the widget.

        Returns
        -------
        model : :class:`eveviewer.gui.model.Model`
            The model used by the widget.

        """
        return self._model

    @model.setter
    def model(self, model=None):
        self._model = model
        self._model.current_dataset_changed.connect(
            self._update_ui, QtCore.Qt.UniqueConnection
        )

    def _setup_ui(self):
        """
        Set up the widget.

        This method takes care of setting up all the elements of the widget.
        This is a three-step process, each carried out calling the
        corresponding non-public method:

        #. Set the widget properties
        #. Set the layout
        #. Connect the signals and slots

         A requirement is to define all widgets as non-public attributes in
         the class constructor. This comes with the advantage to separate
         the different tasks into methods.
        """
        self._set_widget_properties()
        self._set_layout()
        self._connect_signals()

    def _update_ui(self):
        """
        Update all the elements of the widget.

        This is the once central place taking care of updating all the
        user-facing elements of your widget.
        """
        if not self.model.current_dataset:
            self._time_start_value_label.setText("")
            self._time_end_value_label.setText("")
            self._duration_value_label.setText("")
            self._location_value_label.setText("")
            return
        dataset = self.model.datasets[self.model.current_dataset]
        start = dataset.metadata.measurement.start.replace(microsecond=0)
        end = dataset.metadata.measurement.end.replace(microsecond=0)
        self._time_start_value_label.setText(start.isoformat(sep=" "))
        self._time_end_value_label.setText(end.isoformat(sep=" "))
        self._duration_value_label.setText(str(end - start))
        self._location_value_label.setText(
            dataset.metadata.measurement.location
        )

    def _set_widget_properties(self):
        """
        Set the widgets of all the UI components.

        Usually, a widget will contain a number of other widgets whose
        properties need to be set initially. This is the one central place
        to do this.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        self._time_start_label.setText("Time start:")
        self._time_start_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self._time_end_label.setText("Time end:")
        self._time_end_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self._duration_label.setText("Duration:")
        self._duration_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self._location_label.setText("Location:")
        self._location_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )

    def _set_layout(self):
        """
        Lay out the elements of the widget.

        Usually, a widget will contain a number of other widgets that need
        to be laid out in some way. This is the central place to do this.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        top_layout = QtWidgets.QGridLayout()
        top_layout.setColumnStretch(1, 1)
        top_layout.addWidget(self._time_start_label, 0, 0)
        top_layout.addWidget(self._time_start_value_label, 0, 1)
        top_layout.addWidget(self._time_end_label, 1, 0)
        top_layout.addWidget(self._time_end_value_label, 1, 1)
        top_layout.addWidget(self._duration_label, 2, 0)
        top_layout.addWidget(self._duration_value_label, 2, 1)
        top_layout.addWidget(self._location_label, 3, 0)
        top_layout.addWidget(self._location_value_label, 3, 1)
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addStretch(1)
        self.setLayout(layout)

    def _connect_signals(self):
        """
        Connect all signals and slots of the widget.

        To have a widget perform its tasks interactively, it will usually
        define signals and slots that need to be connected. This is the
        central place to do this.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """


if __name__ == "__main__":

    class _MainWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            widget = MeasurementCharacteristicsWidget()
            dataset_names = ["/foo/bar/bla.blub", "/foo/bar/foobar.blub"]
            widget.model.datasets_to_display = dataset_names
            # widget.model.current_dataset = dataset_names[0]
            self.setCentralWidget(widget)
            self.show()

    app = QtWidgets.QApplication()
    w = _MainWindow()
    app.exec()
