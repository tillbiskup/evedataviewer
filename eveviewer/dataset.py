"""
dataset module of the eveviewer package.

Quick&dirty reimplementation of the ASpecD concept of a dataset.

This module will be obsolete as soon as the radiometry package based on the
ASpecD framework starts to exist.

For the time being, only a subset of the interfaces of the respective
classes are implemented, to allow for a convenient drop-in replacement with
the radiometry package.
"""

import numpy as np


class Dataset:
    """
    Quick&dirty reimplementation of ASpecD concept of dataset.

    Will be replaced by proper dataset class based on the ASpecD framework.

    Attributes
    ----------
    data : :class:`Data`
        Actual data of the dataset.

        The data stored in here are acted upon by all processing, analysis,
        plot and other steps.

    device_data : :class:`dict`
        Series of devices and their corresponding data.

        The keys of the dict correspond to the names of the devices. The
        actual device data, *i.e.* the values corresponding to the keys, are
        stored as :class:`Data`.

    metadata : :class:`dict`
        All relevant metadata for the dataset.

        Currently, a plain dict, but will be replaced with appropriate classes.

    """

    def __init__(self):
        self.data = Data()
        self.device_data = {}
        self._preferred_data = []
        self.metadata = {}

    @property
    def preferred_data(self):
        # noinspection PyUnresolvedReferences
        """
        Names of the devices used as preferred data.

        Preferred data are used for both, axes and data values. Valid names
        for the preferred data are the keys of the :attr:`device_data`
        property.

        Setting preferred data will change data and axes values in
        :attr:`data` accordingly.

        Parameters
        ----------
        devices : :class:`list`
            List of device names (as strings)

        Returns
        -------
        preferred_data : :class:`list`
            List of device names (as strings) set as preferred data

        """
        return self._preferred_data

    @preferred_data.setter
    def preferred_data(self, devices=None):
        old_preferred_data = self._preferred_data
        self._preferred_data = devices
        if self._preferred_data != old_preferred_data:
            self._set_data(device=self._preferred_data[0], kind="axes")
            self._set_data(device=self._preferred_data[1], kind="data")

    def _set_data(self, device="", kind=""):
        if kind == "axes":
            self.data.axes[0].values = self.device_data[device].data
        elif kind == "data":
            self.data.data = self.device_data[device].data

    @property
    def devices(self):
        """
        Names of the devices data are available for.

        Device data are stored in :attr:`device_data`, the names of the
        devices are the keys of the :attr:`device_data` dict.

        Returns
        -------
        devices : :class:`list`
            List of strings with device names

        """
        return list(self.device_data.keys())

    def import_from(self, importer):
        """
        Import data from an external source using an importer.

        Parameters
        ----------
        importer : :class:`eveviewer.io.Importer`
            Importer object used to import the data

        """
        importer.import_into(self)

    def plot(self, figure=None):
        """
        Plot data

        Parameters
        ----------
        figure : :class:`matplotlib.figure.Figure`
            Figure to plot data (in)to

        """
        if not figure:
            return
        axes = figure.axes[0]
        axes.plot(self.data.axes[0].values, self.data.data, marker=".")
        axes.set_xlabel(self.data.axes[0].label)
        axes.set_ylabel(self.data.axes[1].label)


class Data:
    """
    Quick&dirty reimplementation of ASpecD concept of data.

    Will be obsolete as soon as the radiometry package based on the ASpecD
    framework starts to exist.
    """

    def __init__(self):
        self.data = np.ndarray([0])
        self.axes = [Axis(), Axis()]


class Axis:
    """
    Quick&dirty reimplementation of ASpecD concept of axis.

    Will be obsolete as soon as the radiometry package based on the ASpecD
    framework starts to exist.
    """

    def __init__(self, quantity="", unit=""):
        self.values = np.ndarray([0])
        self.quantity = quantity
        self.unit = unit

    @property
    def label(self):
        """
        Properly formatted axis label according to IUPAC nomenclature.

        Axis labels should separate quantity and unit with a slash (``/``),
        not have units in square brackets. Furthermore, the slash is only
        present if a unit is given.

        Returns
        -------
        label : :class:`str`
            formatted axis label

        """
        if self.unit:
            label = " / ".join([self.quantity, self.unit])
        else:
            label = self.quantity
        return label
