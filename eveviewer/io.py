"""
io module of the eveviewer package.

Quick&dirty reimplementation of the ASpecD concept of IO.

This module will be obsolete as soon as the radiometry package based on the
ASpecD framework starts to exist.

For the time being, only a subset of the interfaces of the respective
classes are implemented, to allow for a convenient drop-in replacement with
the radiometry package.
"""
import os

import numpy as np

from eveviewer import paradise
from eveviewer import dataset as eve_dataset


def report_problematic_file(filename=""):
    """
    Helper function reporting files that cannot be read by paradise.

    Some EVE files cannot be imported using paradise. To further investigate
    these problems, the file names are reported by appending them to a file in
    the user's home directory. The log file is currently hard-coded to
    ``~/.paradise_problematic_files``.

    Parameters
    ----------
    filename : :class:`str`
        Name (usually the full path) of the problematic file to be reported

    """
    if not filename:
        return
    logfile = os.path.expanduser("~/.paradise_problematic_files")
    with open(logfile, "a", encoding="utf-8") as file:
        file.write(f"{filename}\n")


class ImporterFactory:
    """Factory returning appropriate importer objects."""

    @staticmethod
    def get_importer(source=""):
        """
        Obtain importer for a given data source.

        Parameters
        ----------
        source : :class:`str`
            Name of the file to be imported

            This is the only information the factory gets to decide upon
            which importer to return.

        Returns
        -------
        importer
            Object that can be used to actually import the data.

            The source is passed on to the importer.

        """
        if os.path.splitext(source)[1] == ".h5":
            importer = EveHDF5Importer()
            importer.source = source
        else:
            importer = DummyImporter()
            importer.source = source
        return importer


class Importer:
    """
    Base class for importers.

    Although not formally an abstract class, it does not implement any
    actual functionality, but leaves this for the child classes

    Attributes
    ----------
    source : :class:`str`
        Filename (typically the complete path) to the data.

    """

    def __init__(self):
        self.source = ""

    def import_into(self, dataset=None):
        """
        Import data into the given dataset.

        Parameters
        ----------
        dataset : :class:`evefile.dataset.Dataset`
            Dataset to import the data into

        """


class DummyImporter(Importer):
    """
    Dummy implementation of an importer for testing purposes only.

    The data are generated with a random component, to make subsequent
    imports generally distinguishable.
    """

    def import_into(self, dataset=None):
        """
        Import data into the given dataset.

        Parameters
        ----------
        dataset : :class:`evefile.dataset.Dataset`
            Dataset to import the data into

        """
        xdata = np.arange(0.0, 4.0, 0.01)
        ydata = np.sin(4 * np.pi * xdata * np.random.random(1))
        dataset.data.data = ydata
        dataset.data.axes[0].values = xdata
        dataset.data.axes[0].quantity = "count"
        dataset.data.axes[0].unit = ""
        dataset.data.axes[1].quantity = "intensity"
        dataset.data.axes[1].unit = "a.u."


class EveHDF5Importer(Importer):
    """
    Importer for EVE HDF5 files.

    Currently, the importer uses the paradise module written by Mika
    Pflüger. However, it is planned to soon replace this with evefile.

    .. warning::
        As of now (2023-12), the importer is only rudimentary, importing
        only the data, but no metadata. Relevant metadata will follow in
        conjunction with developing a rich data model for the dataset.

    All channels are stored as ``device_data`` in the dataset and the
    preferred channel and preferred axis set if available. Otherwise,
    the first channel will be set as preferred and the index used as
    corresponding axis.

    Furthermore, a "PosCounter" entry will be added to ``device_data`` as a
    "dummy device". Thus, you are able to set the position counter as axis.

    """

    def import_into(self, dataset=None):
        """
        Import data into the given dataset.

        Parameters
        ----------
        dataset : :class:`evefile.dataset.Dataset`
            Dataset to import the data into

        """
        try:
            data = paradise.StandardMeasurement(self.source)
        except ValueError:
            data = paradise.EVEMeasurement(self.source)
            data.data = data.standard_data
        except KeyError:
            report_problematic_file(filename=self.source)
            print(
                f"{self.source} cannot be read using paradise; the filename "
                f"has been reported."
            )
            return
        for column in data.data.columns:
            device_data = eve_dataset.Data()
            device_data.data = data.data[column].to_numpy()
            device_data.axes[0].values = data.data.index.to_numpy()
            device_data.axes[0].quantity = data.data.index.name
            device_data.axes[1].quantity = column
            if column in data.units:
                device_data.axes[1].unit = data.units[column]
            else:
                device_data.axes[1].unit = ""
            dataset.device_data[column] = device_data
        # Add "PosCounter" as "dummy" device to be able to set it as axis
        position_counter = eve_dataset.Data()
        position_counter.data = data.data.index.to_numpy()
        position_counter.axes[0].values = data.data.index.to_numpy()
        position_counter.axes[0].quantity = data.data.index.name
        position_counter.axes[1].quantity = data.data.index.name
        dataset.device_data["PosCounter"] = position_counter
        if not data.preferred_channel:
            data.preferred_channel = data.data.columns[0]
            print(
                f"{self.source}: No preferred channel, using"
                f" {data.preferred_channel}"
            )
        if not data.preferred_axis:
            data.preferred_axis = data.data.index.name
        dataset.preferred_data = [data.preferred_axis, data.preferred_channel]
