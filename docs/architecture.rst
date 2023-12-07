====================
General architecture
====================

The eveviewer package aims at modularity and maintainability over a long time period and with different maintainers. Hence a few comments on how this can be achieved and what consequences this will have for the overall software architecture.


Key aspects
===========

Writing software that just about "works for me" is easy. Writing software that can be maintained for long(er) time and extended and adapted to future needs is an entirely different matter. The following aspects are best practices of (scientific) software development the eveviewer package tries to follow closely:

* Strict separation of concerns

  * GUI and actual data processing are entirely separate aspects/domains
  * GUI development follows the model--view pattern
  * Complex GUI widgets based on `qtbricks <https://qtbricks.docs.till-biskup.de/>`_ package

* Clean code

  * Focus on readable code: expressive names, consistent use of Python idioms
  * Automatic code formatting using `Black <https://black.readthedocs.io/>`_
  * Regular static code checks using `Prospector <https://prospector.landscape.io/>`_
  * Code development using `pymetacode <https://python.docs.meta-co.de/>`_ for consistency
  * Developed mostly test-driven, for robust code and high test coverage, allowing for easy refactorings and further developments

* Python package following best practices

  * Should *always* be installed in a virtual environment
  * Readily installable using ``pip`` (even from local directory)

* Extensive documentation

  * Both, conceptual documentation as well as API documentation
  * Automatically generated and updated using `Sphinx <https://www.sphinx-doc.org/>`_

* Fundamental infrastructure

  * Version control using git
  * Automatic incrementing of version numbers
  * Automatic code formatting using `Black <https://black.readthedocs.io/>`_
  * Static code checking using `Prospector <https://prospector.landscape.io/>`_
  * Documentation generated using `Sphinx <https://www.sphinx-doc.org/>`_
  * Code development using `pymetacode <https://python.docs.meta-co.de/>`_


Programming language: Python
============================

Why Python? In short: Because Python is nowadays in widespread use in both, science and technology and is rather easy to get started with, even for people not too familiar with programming. Furthermore, Python is open-source and free of charge, hence no vendor lock-in or hidden costs. Not to forget: Python comes with an excellent scientific software stack, making implementing processing and analysis routines for data comparably easy.

For the time being, Python may be the language of choice for scientific software, particularly in a context where scientists and engineers that have no formal qualification as software developers are primarily in charge of developing and maintaining the project.


GUI framework: Qt6/PySide6
==========================

A GUI necessarily requires using a GUI toolkit. Why Qt? Why Qt6/PySide6 (and not Qt5 or PyQt)? Why a GUI framework (Qt) rather than a GUI toolkit (tkinter)? In short (details perhaps later):

* GUI programming quickly gets complex and reaches far beyond arranging widgets in a window. Hence a framework (Qt) providing an event mechanism (Qt signals and slots) as well as supporting the MV(C) pattern, besides more complex widgets with clear separation of model and view, not only a toolkit (tkinter).

* Qt is platform-independent, stable, widely used and well-documented (at least the original C++ part).

* Qt6 is the current version of Qt, hence for a new project, there is no point in starting with Qt5, only to have to update to Qt6 in a few years time.

* PySide6 is maintained by the Qt company itself, *i.e.* the maintainers and developers of the Qt framework. PyQt is maintained by a small company (some say a single person). Although both are widely compatible and similar, PySide seems to be the better choice regarding long-term maintenance.


