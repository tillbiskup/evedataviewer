=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.1
===============

Version 0.1 is meant as a first demonstrator, being able to load and display real data. This version should allow to get immediate feedback from the users: Are we developing the right tool? What are the most important next features to implement?

+ GUI features

  * Display subscans (requires changing importer)


For later versions
==================

* Display characteristics for each scan

  * maximum: position and value
  * FWHM
  * step width of scan
  * anything else?

* Display characteristics of the beamline

  * What exactly?

* Processing and analysis

  * energy edge (there should be code available... rewrite or include via plugin mechanism)
  * Should be seen in context of a ``radiometry`` Python package for data processing and analysis

* Further display modes

  * Comparing parameters for scans (perhaps with diff view and/or colours)

* Attachable status window with log messages


General
=======

A list of obvious things to discuss/decide/implement:

* Handling of files

  * Some files cannot easily be imported using paradise (and are currently logged) -- investigate and solve (may have been solved: datasets without data caused problems)
  * How to deal with datasets that have no preferred channel/axis set?

  * Larger discussion: How to continue with importers? Use evefile? Use an updated/improved version of paradise? Develop an own machinery?

* Most important basic features

  * What are the most important basic features of the viewer?

* Plotter modularisation/implementation

  * Modularise plotting: extract from model, use ASpecD-inspired plotters to allow for easy drop-in replacement

* Dataset model

  * Design a dataset model for the data
  * Should be seen in context of a ``radiometry`` Python package for data processing and analysis

* Handling of spectra (contained in HDF5 files?)

  * How and where to display?
  * Will probably need example files and input from actual users...

* Handling of external files (images)

  * Plotting should be rather straight-forward
  * How to implement in dataset model?
