"""
Model for the eveviewer GUI application.

.. note::

    A note for developers: Following the Model--View (MV) pattern, the model
    does not care nor knows about the view, but the view (here:
    :class:`eveviewer.gui.mainwindow.MainWindow`) knows about the model
    and connects to the appropriate signals and slots. The model is the
    place to define the "business logic", *i.e.* the (abstract) behaviour of
    the application. Furthermore, the model is responsible to provide the
    data to the connected view(s).


Core business logic
===================

For the time being, a perhaps simplistic birds-eye view on what eveviewer
is supposed to do:

* Allow the user to browse data files and select one or several files for
  display.
* Allow for several different display modes of the data (graphical, tabular,
  ...).


For the model, this boils down to:

* Provide a list of datasets to be displayed.
* Load data contained in the list of datasets to be selected.
* Display data contained in the list of datasets to be displayed,
  with the display mode depending on internal settings.


Additional aspects not yet implemented, but necessary:

* Select channels and axes to plot (basically, *x* and *y* data)
* Handle subscans within a dataset (and remember the current subscan number)


Things to be decided upon:

* How to deal with displaying multiple datasets with incompatible axes?
* Shall datasets remember the setting for channel/axis/subscan during one
  session of the GUI? Probably yes...
* Shall datasets remember plot-specific settings?


Implementation
==============

Currently, the idea is very simplistic:

* dictionary with loaded datasets

  * keys are the corresponding filenames

* list of datasets to be displayed

  * list comes, e.g., from FileBrowser widget
  * if element in list has no corresponding entry in dict with loaded
    datasets, load dataset
  * if list changes, refresh plot

* figure

  * handle of Matplotlib figure
  * if None, do not plot


Module documentation
====================

"""

from PySide6 import QtCore

import eveviewer.dataset
import eveviewer.io
from eveviewer import utils


class Model(QtCore.QObject):
    """
    Model for the eveviewer application.

    Attributes
    ----------
    datasets : :class:`dict`
        Datasets loaded

        The keys are the filenames, and the datasets are accessed
        accordingly by their filenames.

        .. note::
            Currently, every dataset once loaded is retained in this dict.
            If this ever gets a problem due to memory consumption, we will
            need to implement something taking care of a threshold of memory
            consumption of this object and starting to delete the oldest
            (*i.e.* first) entries. Note, however, that the first entry is
            not necessarily the longest not visited (hence least
            important) one. Therefore, it might be better to have a second
            structure containing keys and timestamps of last visit that
            allow for detecting the longest not-visited dataset.

            For inspiration of a :func:`sys.getsizeof` equivalent that works
            with containers such as a :class:`dict`,
            see https://code.activestate.com/recipes/577504/

    figure : :class:`matplotlib.figure.Figure`
        Figure used to plot data

    """

    dataset_selection_changed = QtCore.Signal(list)
    """
    Signal emitted when the selection of datasets changed.

    The signal contains the names of the selected datasets as :class:`list` 
    parameter.
    """

    dataset_changed = QtCore.Signal(str)
    """
    Signal that should be emitted whenever a dataset changes.

    The signal contains the name of the dataset that has changed.
    """

    plot_changed = QtCore.Signal()
    """
    Signal that should be emitted whenever the plot or its properties change.
    """

    def __init__(self):
        super().__init__()
        self.datasets = {}
        self._datasets_to_display = utils.NotifyingList(
            callback=self.display_data
        )
        self.figure = None
        self.dataset_changed.connect(self.display_data)
        self.plot_changed.connect(self._refresh_plot)

        self._display_mode = "plot"
        self._importer_factory = eveviewer.io.ImporterFactory()

    @property
    def datasets_to_display(self):
        # noinspection PyUnresolvedReferences
        """
        Datasets that should be displayed.

        Parameters
        ----------
        datasets : :class:`list`
            Datasets to be displayed

        Returns
        -------
        datasets : :class:`list`
            Datasets to be displayed

        """
        return self._datasets_to_display

    @datasets_to_display.setter
    def datasets_to_display(self, datasets):
        if utils.lists_are_equal(self._datasets_to_display, datasets):
            return
        self._datasets_to_display = datasets
        self.display_data()
        self.dataset_selection_changed.emit(self._datasets_to_display)

    @QtCore.Slot()
    def display_data(self):
        """
        Display the datasets listed as to be displayed.

        This method is a Qt slot events can be connected to. Hence,
        a GUI widget changing the state of the model or datasets contained
        therein usually connects to this slot.

        Which kind of display will be used depends on the state of the
        internal property :attr:`_display_mode`. Thus, you can easily set/add
        different display modes and need not care of how to display the data.

        Possibilities would be, besides the currently implemented graphical
        display (``plot``), a tabular display or even a diff display for two
        or more datasets, showing the differences in the metadata.

        .. important::
            Usually, you should call this method rather than those methods
            dealing with a concrete display mode, such as :meth:`plot_data`,
            as this method takes care of loading the data if they are not
            yet internally available.

        .. note::
            For developers: For maximum flexibility and modularity,
            the actual display mode is used as first part of the method
            name. Hence, if you want to implement/support further display
            types, create a non-public method :meth:`<display_mode>_data`
            and implement all necessary functionality therein.

        """
        for dataset in self.datasets_to_display:
            if dataset not in self.datasets:
                self.load_data(dataset)
        getattr(self, f"{self._display_mode}_data")()

    def load_data(self, filename=""):
        """
        Load data from a given filename.

        Parameters
        ----------
        filename : :class:`str`
            Name of the file the data should be loaded from


        .. note::
            For developers: For maximum flexibility and modularity, loading
            data is delegated to importers and datasets, and the importer
            obtained using an importer factory. These concepts are all
            implemented in the ASpecD framework and mimicked here, allowing
            for a later drop-in replacement with an ASpecD-derived package.

        """
        dataset = eveviewer.dataset.Dataset()
        importer = self._importer_factory.get_importer(source=filename)
        dataset.import_from(importer)
        self.datasets[filename] = dataset

    def plot_data(self):
        """
        Graphically display the data currently selected.

        If not figure is provided (by means of :attr:`figure`), the method
        silently returns.

        .. todo::
            Should be replaced with a modular approach using plotters,
            similar to what has been done for loading data.

        """
        if not self.figure:
            return
        self.figure.axes[0].cla()
        for dataset in self.datasets_to_display:
            self.datasets[dataset].plot(figure=self.figure)
        self.figure.canvas.draw_idle()

    def _refresh_plot(self):
        if self.figure:
            self.figure.canvas.draw_idle()


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    model = Model()
    model.figure = fig

    model.load_data("foo")
    model.load_data("bar")

    model.datasets_to_display.append("foo")
    model.datasets_to_display.append("bar")
    model.datasets_to_display.remove("foo")

    model.datasets_to_display = ["foo", "bar"]

    plt.show()
