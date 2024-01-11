"""
Main GUI window.

There is usually one main window of a GUI, and this window consists of all
the default parts provided by the Qt framework, namely menu bar and toolbars
at the top, status bar at the bottom, and areas for dockable windows/widgets
on all four sides of the central widget.

Rather than creating an instance of :class:`MainWindow` yourself, you will
usually call the :func:`eveviewer.gui.app.main` function of the
:mod:`eveviewer.gui.app` module, or simply call the GUI by means of the
respective gui_scripts entry point defined in ``setup.py``.


Some notes for developers
=========================

GUI programming can be quite complex, and the :class:`MainWindow` class
provides only a small set of (sensible) defaults for the most common tasks.
For this, it relies on the :mod:`qtbricks.mainwindow` module of the
:mod:`qtbricks` package. For some further general advice and an overview of
the functionality implemented see its documentation. A few additional hints
are given below.


Adding a central widget
-----------------------

Each window typically consists of a central widget, although the central
widget can be a complex and composed widget, such as a
:class:`PySide6.QtWidgets.QSplitter`. In many cases, you will need to add
the :mod:`PySide6.QtWidgets` module to the import statements on top of this
module:


.. code-block::

    from PySide6 import QtWidgets


The actual central widget is setup in the non-public method
:meth:`qtbricks.mainwindow.MainWindow._create_central_widget`. Typically,
the central widget itself, however, is defined in the constructor of the
main window and referenced in this method accordingly. As
:meth:`qtbricks.mainwindow.MainWindow._create_central_widget` gets called
automatically from within the constructor of the
:class:`qtbricks.mainwindow.MainWindow` class, make sure to define your
widgets *before* calling the parent constructor. A simplified example may
look as follows:


.. code-block::

    def __init__(self):
        self.file_browser = qtbricks.filebrowser.FileBrowser()
        self.plot = qtbricks.plot.Plot()
        # Needs to appear after the central widgets, but before the model
        super().__init__()

    def _create_central_widget(self):
        splitter = QtWidgets.QSplitter()
        self.file_browser.setParent(splitter)
        self.plot.setParent(splitter)
        self.setCentralWidget(splitter)


Separating model and view
-------------------------

Your main window, although the main entry point for the users, is "just" a
view, and it shall not contain the application logic. Only the high-level
logic connecting (via the signal--slot mechanism of Qt) the different parts
of a GUI and the underlying model are defined here.

Typically, you will define the model in a separate module and import it
accordingly. In your case, the relevant code excerpts may look like this:

.. code-block::

    import eveviewer.gui.model as model


    class MainWindow(qtbricks.mainwindow.MainWindow):

        def __init__(self):
            self.file_browser = qtbricks.filebrowser.FileBrowser()
            self.plot = qtbricks.plot.Plot()
            # Needs to appear after the central widgets, but before the model
            super().__init__()
            self.model = model.Model()
            self.model.figure = self.plot.figure
            self.file_browser.selection_changed.connect(self._update_model)

        def _create_central_widget(self):
            splitter = QtWidgets.QSplitter()
            self.file_browser.setParent(splitter)
            self.plot.setParent(splitter)
            self.setCentralWidget(splitter)

        def _update_model(self, datasets):
            self.model.datasets_to_display = list(datasets)



Module documentation
====================

"""

import os

from PySide6 import QtWidgets, QtCore

import qtbricks.filebrowser
import qtbricks.mainwindow
import qtbricks.plot
import qtbricks.utils

from eveviewer.gui import model, dataset_display_widget
from eveviewer.gui import measurement_characteristics_widget as measurement


class MainWindow(qtbricks.mainwindow.MainWindow):
    """
    Main GUI window of the application.

    There is usually one main window of a GUI, and this window consists of
    all the default parts provided by the Qt framework, namely menu bar and
    toolbars at the top, status bar at the bottom, and areas for dockable
    windows/widgets on all four sides of the central widget.

    For details on how to implement the actual functionality in your main
    window, have a look at the documentation of the parent class,
    :class:`qtbricks.mainwindow.MainWindow`.

    While any more complex dialogs and widgets are often designed using
    the QtDesigner tool, the main window, consisting typically of one
    central widget, is laid out programmatically.

    Rather than creating an instance of :class:`MainWindow` yourself,
    you will usually call the :func:`eveviewer.gui.app.main` function of the
    :mod:`eveviewer.gui.app` module, or simply call the GUI by means of the
    respective gui_scripts entry point defined in ``setup.py``.

    By default, window geometry and state will be saved on close and
    restored on startup. This creates a file, typically in the user's home
    directory, and depending on the respective platform. Directory and file
    name depend on the settings of organisation and application name on the
    application level. For details, see the :func:`eveviewer.gui.app.main`
    function in the :mod:`eveviewer.gui.app` module.

    Attributes
    ----------
    file_browser : :class:`qtbricks.filebrowser.FileBrowser`
        Widget for browsing and navigating through files and directories

    plot : :class:`qtbricks.plot.Plot`
        Widget for graphical display of data

    model : :class:`eveviewer.gui.model.Model`
        Model for the eveviewer GUI application.

    package_name : :class:`str`
        Name of the package the main GUI window belongs to.

        This information is required, *i.a.*, for the "Help About" window.

    logo : :class:`str`
        Path to logo image file

        The logo is used, *i.a.*, for the Help About window.

    """

    def __init__(self):
        self.file_browser = qtbricks.filebrowser.FileBrowser()
        self.file_browser.model_settings = {
            "filters": ["*.py", "*.h5"],
            "filter_disables": False,
        }
        self.plot = qtbricks.plot.Plot()
        self._dataset_display = dataset_display_widget.DatasetDisplayWidget()
        self._measurement_characteristics = (
            measurement.MeasurementCharacteristicsWidget()
        )
        self._dataset_controls = QtWidgets.QWidget()

        # Needs to appear after the central widgets, but before the model
        super().__init__()

        self.setMinimumSize(QtCore.QSize(1000, 600))
        self.model = model.Model()
        self.model.figure = self.plot.figure
        self.file_browser.selection_changed.connect(self._update_model)
        self.package_name = "eveviewer"
        self.logo = qtbricks.utils.image_path(
            "icon.svg", base_dir=os.path.dirname(__file__)
        )

        self._dataset_display.model = self.model
        self._measurement_characteristics.model = self.model

    def _create_central_widget(self):
        splitter = QtWidgets.QSplitter()
        self.file_browser.setParent(splitter)
        self.plot.setParent(splitter)
        self.setCentralWidget(splitter)

    def _update_model(self, datasets):
        self.model.datasets_to_display = list(datasets)

    def _create_dock_windows(self):
        dataset_control_layout = QtWidgets.QVBoxLayout()
        dataset_control_layout.addWidget(self._dataset_display)
        dataset_control_layout.addWidget(self._measurement_characteristics)
        self._dataset_controls.setLayout(dataset_control_layout)
        dataset_display_dock = qtbricks.mainwindow.GeneralDockWindow(
            title="Dataset display",
            widget=self._dataset_controls,
            object_name="dataset_display",
        )
        dataset_display_dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self._add_dock_window(dock_window=dataset_display_dock)
