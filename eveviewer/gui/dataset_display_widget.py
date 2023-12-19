"""
Widget for setting dataset display options.

**Purpose:** For each individual dataset, the axes and data to be displayed
need to be changeable. Furthermore, depending on the dataset, displaying and
flicking through sub-scans should be possible as well.

**Design principles:** The widget should be as self-contained and
self-consistent as possible, corresponding with the model of the main window
giving access to the datasets and the list of currently selected datasets.

**Limitations:** This widget is meant to actively set display options of the
individual datasets currently displayed. Presenting information (metadata)
of the respective dataset should be handled by other widgets.

Below is a first summary of what the widget should allow doing:

* Select a dataset from the list of currently selected/active datasets.

  If no dataset is selected, this list and the entire widget may be
  disabled, at least no dataset should be shown.

  The datasets should probably be identified by the filenames excluding the
  path, as otherwise, the combobox will be quite wide. Best to use the
  "label" attribute of the dataset and have the importer initially set this
  to a sensible value (and in the long run, provide the user with the ability
  to change it).

* For the selected dataset, select one or both of x and y axes from the
  list of available channels (*i.e.*, device data in the dataset).

  Usually, all channels have the identical number of values,
  hence setting arbitrary combinations should be possible.

* For the selected dataset, flick through the sub-scans if there are any.

  Setting the sub-scan index to ``-1`` should disable the sub-scan
  display and display the entire dataset instead. Using ``-1`` rather than
  ``0`` internally is due to the zero-based indexing of Python. For the
  actual display, this may be changed depending on user preferences.

The widget gets added to the main GUI window of the eveviewer GUI, either as
dockable window (preferable) or fixed in the layout.

"""

from PySide6 import QtWidgets, QtCore
import qtbricks.utils

from eveviewer.gui import model as gui_model


# pylint: disable=too-many-instance-attributes
# noinspection PyUnresolvedReferences
class DatasetDisplayWidget(QtWidgets.QWidget):
    """
    Display settings for individual datasets, allowing to select the dataset.

    For each individual dataset, the axes and data to be displayed need to be
    changeable. Furthermore, depending on the dataset, displaying and
    flicking through sub-scans should be possible as well.
    """

    def __init__(self):
        super().__init__()

        self._model = gui_model.Model()
        self._model.dataset_selection_changed.connect(
            self._update_ui, QtCore.Qt.UniqueConnection
        )

        # Define all UI elements (widgets) here as non-public attributes
        self._dataset_combobox = QtWidgets.QComboBox()
        self._dataset_label = QtWidgets.QLabel()
        self._x_axis_combobox = QtWidgets.QComboBox()
        self._x_axis_label = QtWidgets.QLabel()
        self._y_axis_combobox = QtWidgets.QComboBox()
        self._y_axis_label = QtWidgets.QLabel()
        self._subscan_decrement_button = QtWidgets.QPushButton()
        self._subscan_increment_button = QtWidgets.QPushButton()
        self._subscan_current_edit = QtWidgets.QLineEdit("-1")
        self._subscan_number_label = QtWidgets.QLabel("0")
        self._subscan_label = QtWidgets.QLabel()

        self._subscan_widgets = [
            getattr(self, attr)
            for attr in dir(self)
            if attr.startswith("_subscan_")
        ]

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
        self._model.dataset_selection_changed.connect(
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
        user-facing elements of the widget.
        """
        self._update_dataset_combobox()
        self._update_axes_comboboxes()
        self._update_subscan_widgets()

    def _update_dataset_combobox(self):
        dataset_labels = [
            self.model.datasets[dataset].label
            for dataset in self.model.datasets_to_display
        ]
        combobox_items = [
            self._dataset_combobox.itemText(idx)
            for idx in range(self._dataset_combobox.count())
        ]
        if dataset_labels != combobox_items:
            self._dataset_combobox.clear()
            self._dataset_combobox.addItems(dataset_labels)

    def _update_axes_comboboxes(self):
        if self.model.datasets_to_display:
            selected_dataset = self._dataset_combobox.currentIndex()
            dataset_name = self.model.datasets_to_display[selected_dataset]
            axes = self.model.datasets[dataset_name].devices
            preferred = self.model.datasets[dataset_name].preferred_data
            self._x_axis_combobox.clear()
            self._x_axis_combobox.addItems(axes)
            self._x_axis_combobox.setCurrentIndex(
                self._x_axis_combobox.findText(preferred[0])
            )
            self._y_axis_combobox.clear()
            self._y_axis_combobox.addItems(axes)
            self._y_axis_combobox.setCurrentIndex(
                self._y_axis_combobox.findText(preferred[1])
            )

    def _update_subscan_widgets(self):
        selected_dataset = self._dataset_combobox.currentIndex()
        if selected_dataset == -1:
            return
        dataset_name = self.model.datasets_to_display[selected_dataset]
        if self.model.datasets[dataset_name].subscans["boundaries"]:
            for widget in self._subscan_widgets:
                widget.setDisabled(False)
            self._subscan_decrement_button.setDisabled(False)
            self._subscan_increment_button.setDisabled(False)
        else:
            for widget in self._subscan_widgets:
                widget.setDisabled(True)
            self._subscan_decrement_button.setDisabled(True)
            self._subscan_increment_button.setDisabled(True)

    def _update_axes_and_subscans(self):
        self._update_axes_comboboxes()
        self._update_subscan_widgets()

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

        self._subscan_decrement_button = qtbricks.utils.create_button(
            text="",
            slot=None,
            shortcut="",
            icon="circle-left.svg",
            checkable=False,
            tooltip="Show previous sub-scan",
        )
        self._subscan_decrement_button.setFixedSize(
            self._y_axis_combobox.sizeHint().height(),
            self._y_axis_combobox.sizeHint().height(),
        )
        self._subscan_increment_button = qtbricks.utils.create_button(
            text="",
            slot=None,
            shortcut="",
            icon="circle-right.svg",
            checkable=False,
            tooltip="Show next sub-scan",
        )
        self._subscan_increment_button.setFixedSize(
            self._y_axis_combobox.sizeHint().height(),
            self._y_axis_combobox.sizeHint().height(),
        )
        self._subscan_current_edit.setFixedSize(
            self._y_axis_combobox.sizeHint().height() * 1.2,
            self._y_axis_combobox.sizeHint().height(),
        )
        self._subscan_current_edit.setAlignment(QtCore.Qt.AlignRight)
        self._subscan_label.setText("Sub-scans:")
        self._subscan_label.setObjectName("subscan_label")

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
        subscans_layout = QtWidgets.QHBoxLayout()
        subscans_layout.addWidget(self._subscan_decrement_button)
        subscans_layout.addWidget(self._subscan_increment_button)
        subscans_layout.addWidget(self._subscan_current_edit)
        subscans_layout.addWidget(QtWidgets.QLabel("/"))
        subscans_layout.addWidget(self._subscan_number_label)
        subscans_layout.addStretch(1)
        top_layout.addWidget(self._subscan_label, 3, 0)
        top_layout.addLayout(subscans_layout, 3, 1)
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
        self._dataset_combobox.currentIndexChanged.connect(
            self._update_axes_and_subscans
        )
        self._x_axis_combobox.currentIndexChanged.connect(
            self._set_dataset_preferred_data
        )
        self._y_axis_combobox.currentIndexChanged.connect(
            self._set_dataset_preferred_data
        )

    def _set_dataset_preferred_data(self):
        dataset = self._model.datasets_to_display[
            self._dataset_combobox.currentIndex()
        ]
        x_axis = self._x_axis_combobox.currentText()
        y_axis = self._y_axis_combobox.currentText()
        devices = self.model.datasets[dataset].devices
        if x_axis and y_axis and x_axis in devices and y_axis in devices:
            self.model.datasets[dataset].preferred_data = [
                self._x_axis_combobox.currentText(),
                self._y_axis_combobox.currentText(),
            ]
            self.model.dataset_changed.emit(dataset)


if __name__ == "__main__":

    class _MainWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            widget = DatasetDisplayWidget()
            dataset_names = ["/foo/bar/bla.blub", "/foo/bar/foobar.blub"]
            widget.model.datasets_to_display = dataset_names
            # noinspection PyProtectedMember
            widget._update_ui()
            self.setCentralWidget(widget)
            self.show()

    app = QtWidgets.QApplication()
    w = _MainWindow()
    app.exec()
