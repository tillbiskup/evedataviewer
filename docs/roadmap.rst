=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.1
===============

* ...


General
=======

A list of obvious things to discuss/decide/implement:

* Handling of files

  * Some files cannot easily be imported using paradise (and are currently logged) -- investigate and solve
  * How to deal with datasets that have no preferred channel/axis set?

  * Larger discussion: How to continue with importers? Use evefile? Use an updated/improved version of paradise? Develop an own machinery?

* Most important basic feature

  * What are the most important basic features of the viewer?

* Plotter modularisation/implementation

  * Modularise plotting: extract from model, use ASpecD-inspired plotters to allow for easy drop-in replacement

* Dataset model

  * Design a dataset model for the data

* Handling of external files (images)

  * Plotting should be rather straight-forward
  * How to implement in dataset model?
