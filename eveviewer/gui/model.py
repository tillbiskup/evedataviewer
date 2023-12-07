"""
Model for the eveViewer application.

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

"""

import eveviewer.dataset
import eveviewer.io
from eveviewer import utils


class Model:
    """
    Model for the eveViewer application.

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

    def __init__(self):
        self.datasets = {}
        self._datasets_to_display = utils.NotifyingList(
            callback=self.display_data
        )
        self.figure = None

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

    def display_data(self):
        """
        Display the datasets listed as to be displayed.

        Which kind of display will be used depends on the state of the
        internal property :attr:`_display_mode`. Thus, you can easily set/add
        different display modes and need not care of how to display the data.

        Possibilities would be, besides the currently implemented graphical
        display (``plot``), a tabular display or even a diff display for two
        or more datasets, showing the differences in the metadata.

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
