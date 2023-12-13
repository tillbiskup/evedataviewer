"""
dataset module of the eveviewer package.

Quick&dirty reimplementation of the ASpecD concept of a dataset.

This module will be obsolete as soon as the radiometry package based on the
ASpecD framework starts to exist.

For the time being, only a subset of the interfaces of the respective
classes are implemented, to allow for a convenient drop-in replacement with
the radiometry package.
"""

import copy

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

    subscans : :class:`dict`
        Information on subscans contained in the data of the dataset.

        boundaries : :class:`list`
            List of two-element lists containing the boundaries of each subscan

            The first element starts with 0 as first index, the last element
            ends with the length of the data vector as last element.

        current : :class:`int`
            Index of the current subscan

            Set to -1 to temporarily disable subscans.

    metadata : :class:`dict`
        All relevant metadata for the dataset.

        Currently, a plain dict, but will be replaced with appropriate classes.

    """

    def __init__(self):
        self.data = Data()
        self.device_data = {}
        self._preferred_data = []
        self.subscans = {
            "boundaries": [],
            "current": -1,
        }
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
            self.data.axes[0].quantity = (
                self.device_data[device].axes[0].quantity
            )
            self.data.axes[0].unit = self.device_data[device].axes[0].unit
        elif kind == "data":
            self.data.data = self.device_data[device].data
            self.data.axes[1].quantity = (
                self.device_data[device].axes[1].quantity
            )
            self.data.axes[1].unit = self.device_data[device].axes[1].unit

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

    @property
    def subscan(self):
        """
        Current subscan of data, including data and axes.

        The subscan is a copy of the original data. Hence, all manipulations on
        a subscan are *not* reflected back to the original data.

        Both, subscan boundaries and index of the current subscan are set within
        the :attr:`subscans` property. If the index of the current subscan is
        set to -1, the full data are returned.

        Returns
        -------
        subscan : :class:`Data`
            Current subscan of data, including data and axes.

        """
        if self.subscans["current"] == -1:
            sliced_data = self.data
        else:
            slice_ = slice(
                *self.subscans["boundaries"][self.subscans["current"]]
            )
            sliced_data = copy.copy(self.data)
            sliced_data.data = sliced_data.data[slice_]
            sliced_data.axes[0].values = sliced_data.axes[0].values[slice_]
        return sliced_data

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
