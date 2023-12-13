"""
Widget for setting dataset display options.

For each individual dataset, the axes and data to be displayed need to be
changeable. Furthermore, depending on the dataset, displaying and flicking
through sub-scans should be possible as well.

The widget should be as self-contained and self-consistent as possible,
corresponding with the model of the main window giving access to the
datasets and the list of currently selected datasets.

Below is a first summary of what the widget should allow doing:

* Select a dataset from the list of currently selected/active datasets.

  If no dataset is selected, this list and the entire widget may be
  disabled, at least no dataset should be shown.

  The datasets should probably be identified by the filenames excluding the
  path, as otherwise, the combobox will be quite wide.

* For the selected dataset, select one or both of x and y axes from the
  list of available channels (*i.e.*, device data in the dataset).

  Usually, all channels have the identical number of values,
  hence setting arbitrary combinations should be possible.

* For the selected dataset, flick through the sub-scans if there are any.

  Setting the sub-scan index to ``-1`` should disable the sub-scan
  display and display the entire dataset instead.

The widget gets added to the main GUI window of the eveviewer GUI, either as
dockable window (preferable) or fixed in the layout.

"""

from PySide6 import QtWidgets


class DatasetDisplayWidget(QtWidgets.QWidget):
    """
    Display settings for individual datasets, allowing to select the dataset.

    For each individual dataset, the axes and data to be displayed need to be
    changeable. Furthermore, depending on the dataset, displaying and
    flicking through sub-scans should be possible as well.


    Attributes
    ----------
    attr : :class:`None`
        Short description

    cls.signal_name : :class:`QtCore.Signal`
        Signal emitted when ...

    """

    def __init__(self):
        super().__init__()

        # Define all UI elements (widgets) here as non-public attributes
        self._dataset_combobox = QtWidgets.QComboBox()
        self._dataset_label = QtWidgets.QLabel()
        self._x_axis_combobox = QtWidgets.QComboBox()
        self._x_axis_label = QtWidgets.QLabel()
        self._y_axis_combobox = QtWidgets.QComboBox()
        self._y_axis_label = QtWidgets.QLabel()

        self._setup_ui()
        self._update_ui()

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

    def _set_widget_properties(self):
        """
        Set the widgets of all the UI components.

        Usually, a widget will contain a number of other widgets whose
        properties need to be set initially. This is the one central place
        to do this.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        self._dataset_combobox.setObjectName("dataset_combobox")
        self._dataset_combobox.setToolTip("Dataset to set axes for")
        self._dataset_label.setText("Dataset:")
        self._dataset_label.setObjectName("dataset_label")
        self._dataset_label.setBuddy(self._dataset_combobox)

        self._x_axis_combobox.setObjectName("x_axis_combobox")
        self._x_axis_combobox.setToolTip("Set x axis of dataset")
        self._x_axis_label.setText("x axis:")
        self._x_axis_label.setObjectName("x_axis_label")
        self._x_axis_label.setBuddy(self._x_axis_combobox)

        self._y_axis_combobox.setObjectName("y_axis_combobox")
        self._y_axis_combobox.setToolTip("Set y axis of dataset")
        self._y_axis_label.setText("y axis:")
        self._y_axis_label.setObjectName("y_axis_label")
        self._y_axis_label.setBuddy(self._y_axis_combobox)

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
        top_layout.addWidget(self._dataset_label, 0, 0)
        top_layout.addWidget(self._dataset_combobox, 0, 1)
        top_layout.addWidget(self._x_axis_label, 1, 0)
        top_layout.addWidget(self._x_axis_combobox, 1, 1)
        top_layout.addWidget(self._y_axis_label, 2, 0)
        top_layout.addWidget(self._y_axis_combobox, 2, 1)
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top_layout)
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
            widget = DatasetDisplayWidget()
            self.setCentralWidget(widget)
            self.show()

    app = QtWidgets.QApplication()
    w = _MainWindow()
    app.exec()
