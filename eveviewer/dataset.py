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
    """

    def __init__(self):
        self.data = Data()
        self.metadata = {}

    def import_from(self, importer):
        """
        Import data from an external source using an importer.

        Parameters
        ----------
        importer : :class:`eveviewer.io.EveHDF5Importer`
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
