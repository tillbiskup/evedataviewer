.. _use_cases:

=========
Use cases
=========

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

Generally, you will use the graphical user interface (GUI) of the evedataviewer package that you can start by typing ``evedataviewer`` in a terminal (once the package is installed).

For the time being, the following description of use cases is rather an idea how working with the evedataviewer GUI may look like than a description of what actually can be achieved.


Exploring data
==============

Usually, measuring even a single sample seems to result in a series of data files that need to be explored first to get an idea whether the measurement succeeded and to extract the relevant datasets for further analysis.

As data files are stored and organised in directories per calendar week, some kind of file browser allowing to both, navigate through a hierarchy of directories as well as flicking through the individual measurements and visually inspecting the resulting data (by means of graphical repesentations) are necessary.

As each dataset consists of multiple channels and axes, and not always the preferred axes and channels are marked in the datasets, setting/changing the channels and axes to be plotted needs to be possible. Probably, this information should be stored (at least within one session of the evedataviewer GUI), such that flicking through the files forwards and backwards will not reset the display unless the user intentionally changes these settings (for an individual dataset).


Standard tools for manipulating graphics
----------------------------------------

There is a series of standard tools expected to be present to manipulate the graphical display:

* zooming and panning
* data cursor (*e.g.*, cross-hair cursor) with display of current data point
* show/hide grid
* logarithmic axes

Most of this should be available and familiar from the default matplotlib figures. In any case, (most of) this functionality is provided by the :class:`qtbricks.plot.Plot` widget.


Display of dataset characteristics
----------------------------------

A series of characteristics of each individual scan/dataset should be readily availabe, either in a separate window or next to the graphical display:

* start/stop time of the scan (and total time taken)
* maximum: position and value
* FWHM
* step width of scan

These characteristics can be divided into measurement metadata (start/stop time; duration; location, *i.e.* beamline) and data(set) characteristics (maximum; FWHM; step width).


Displaying subscans
-------------------

Some datasets consist of subscans, hence the application needs to provide a convenient way of switching between an overview plot and the display of the individual subscans, with navigating through the subscans in a similar way to flicking through the individual datasets.


Comparing scans/datasets
========================

Different scans/datasets need to be compared, most easily and intuitively by selecting more than one dataset/file from the list and have them plotted together in the figure window.

Additional modes of display may be tabular (data) and a diff view for the parameters (metadata), perhaps either only displaying the differing parameters or highlighting (using colour or else) the differences.

Graphically displaying more than one dataset in one axes immediately raises some questions:

* How to deal with incompatible axes/channels?

  * Ignore/clean the axis labels and plot data anyway?
  * Display warning and do not plot?
  * Allow the user to choose (and change) the behaviour?

* What kinds of normalisation are necessary/useful for a meaningful comparison?


Basic processing and analysis
=============================

While a series of general characteristics should be available by default for every dataset displayed (see above), there is a series of processing and analysis steps required to extract data necessary to continue with measurements.

Those processing and analysis steps should be implemented *outside* the evedataviewer package (in a more general ``radiometry`` package), but made available in form of plugins or else. For certain characteristics/results of an analysis it may be useful to have them graphically displayed together with the data in the plot window.

