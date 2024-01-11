===============
Target audience
===============

Who is the target audience of the eveviewer package? Is it interesting for me?

The eveviewer package primarily addresses **radiometry** people working at the synchrotron beamlines at BESSY-II and MLS in Berlin operated by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt (PTB) <https://www.ptb.de/>`_. Furthermore, it is a **data viewer tool**, aimed at conveniently inspecting data directly at the beamline. To this end, basic analysis tools will increasingly be included.

However, extended **data analysis is not the focus** of this package, and the required data processing and analysis routines will be developed separately in a package currently dubbed "radiometry" and most probably based on the `ASpecD framework <https://docs.aspecd.de/>`_. Why the discrimination? Simply because exploring and inspecting data is not primarily concerned with reproducibility, while scientific data analysis clearly needs to be reproducible to be scientific. The latter requires, *i.a.*, a complete protocol ("audit trail") of all tasks performed on the data including all relevant parameters and metadata.
