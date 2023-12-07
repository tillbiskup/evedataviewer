"""
eveviewer app.

This module provides the high-level interface to the app and a function that
gets wired up as "gui_script" entry point in the ``setup.py``.
"""

import sys

from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt

import qtbricks.utils

from eveviewer.gui import mainwindow


def splash_screen():
    """
    Create a splash screen normally used during GUI startup.

    Depending on the complexity of a GUI main window, startup may take some
    time. Hence, it is good practice to present the user with a splash
    screen as immediate feedback that something is happening in the background.

    Usually, a splash screen will present an image and perhaps a message.

    Returns
    -------
    splash : :class:`PySide6.QtWidgets.QSplashScreen`
        Splash screen object

        Necessary to interact with the splash screen, *e.g.*, set messages
        and finally remove it from the screen.

    """
    splash = QtWidgets.QSplashScreen(
        QtGui.QPixmap(qtbricks.utils.image_path("splash.svg"))
    )
    splash.show()
    return splash


def main():
    """
    Entry point for the GUI application.

    This function serves as main entry point to the GUI application and gets
    added as "gui_script" entry point. Additionally, the essential
    aspects of the (Qt) application are set that are relevant for saving and
    restoring settings, as well as the window icon.
    """
    app = QtWidgets.QApplication(sys.argv)
    splash = splash_screen()

    app.setOrganizationName("eveviewer")
    app.setOrganizationDomain("ptb.de")
    app.setApplicationName("eveviewer")
    app.setWindowIcon(QtGui.QIcon(qtbricks.utils.image_path("icon.svg")))
    window = mainwindow.MainWindow()
    window.show()
    alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
    splash.showMessage("Loaded main window", alignment=alignment)
    splash.finish(window)

    app.exec()


if __name__ == "__main__":
    main()
