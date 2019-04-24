#!/usr/bin/env python3
"""
File: scale.py
Author: AleNriG
Email: agorokhov94@gmail.com
Github: https://github.com/alenrig
Description: TODO
Copyright © 2018 AleNriG. All Rights Reserved.
"""
import functools
import sys

from PyQt5.QtGui import QColor
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget


def once(function):
    @functools.wraps(function)
    def inner(*args, **kwargs):
        if not inner.called:
            function(*args, **kwargs)
            inner.called = True

    inner.called = False
    return inner


class Main(QMainWindow):

    """Class for main window of a program."""

    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()

    def initUI(self):
        """Init of buttons, bars ang geometry."""

        """ Actions """
        # Exit application
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Exit application")
        self.exit_action.triggered.connect(self.close)

        # TODO: Icons appears on widget even if it runs from other directory
        # Open file
        self.open_file = QAction(QIcon("./icons/open.png"), "Open", self)
        self.open_file.setShortcut("Ctrl+O")
        self.open_file.setStatusTip("Open new file")
        self.open_file.triggered.connect(self.openFile)

        # Save file
        self.save_file = QAction(QIcon("./icons/save_as.png"), "Save as", self)
        self.save_file.setShortcut("Ctrl+S")
        self.save_file.setStatusTip("Save as new file")
        self.save_file.triggered.connect(self.saveFile)

        """ Menubar """
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu("&File")
        self.file_menu.addAction(self.exit_action)
        self.file_menu.addAction(self.open_file)
        self.file_menu.addAction(self.save_file)

        """ Toolbar """
        self.toolbar = self.addToolBar("Files")
        self.toolbar.addAction(self.open_file)
        self.toolbar.addAction(self.save_file)

        self.setGeometry(30, 30, 600, 400)
        self.setWindowTitle("SEM Scale")
        self.statusBar()
        self.show()

    def openFile(self):
        """File dialog for image opening."""

        file_name = QFileDialog.getOpenFileName(
            self, "Open file", "~/Documents/code/sims/tests/"
        )[0]
        self.image_widget = ImageWidget(file_name)
        self.setCentralWidget(self.image_widget)
        # +70 to take into account the status bar height
        self.setGeometry(
            30,
            30,
            self.image_widget.image.width(),
            self.image_widget.image.height() + 70,
        )

        self.askMeasureUnit()
        self.drawToolBar()

    def askMeasureUnit(self):
        """Ask user to input measurement unit."""
        number, ok = QInputDialog.getText(
            self, "Scale unit", "Enter measurement unit: "
        )
        if ok:
            self.image_widget.legend = float(number)

    @once
    def drawToolBar(self):
        """Box with pen colors choice."""
        self.pen_colors = QComboBox()
        colors = ["Black", "Red", "Yellow", "Green"]
        icons = []
        px = QPixmap(10, 10)

        for color in colors:
            px.fill(QColor(color.lower()))
            icon = QIcon(px)
            icons.append(icon)

        for icon, color in zip(icons, colors):
            self.pen_colors.addItem(icon, color)

        self.toolbar = self.addToolBar("Tools")
        self.toolbar.addWidget(self.pen_colors)
        self.pen_colors.activated[str].connect(self.penColor)

    def penColor(self, text):
        """Send chosen pen color to image widget."""
        self.image_widget.pen_color.setNamedColor(text.lower())

    # TODO: save image
    def saveFile(self):
        """File dialog for saving image."""
        pass


class Image:
    def __init__(self, file_name):
        self.pixmap = QPixmap(file_name)
        self.image = self.pixmap.toImage()
        self._find_scale_bar()

    def _find_scale_bar(self):
        """Find the scale bar.

        Find longest white line from both direction. Line can be the leftmost
        or rightmost, so there are breaks after first white line inclusions.
        """
        scale_bar = 0

        for y in range(self.image.height() * 3 // 4, self.image.height()):
            counter = 0
            for x in range(self.image.width()):
                pixel = self.image.pixel(x, y)
                *rgb, _ = QColor(pixel).getRgbF()

                if all(i > 0.9 for i in rgb):
                    counter += 1

                if any(i < 0.9 for i in rgb) and counter != 0:
                    break

            if counter > scale_bar:
                scale_bar = counter

        self.scale_bar = scale_bar


class ImageWidget(QWidget):

    """Class for image widget."""

    def __init__(self, file_name):
        QWidget.__init__(self)
        image = Image(file_name)

        self.pixmap = image.pixmap
        self.image = image.image
        self.scale_bar = image.scale_bar

        self.pen_color = QColor()
        self.initUI()

    def initUI(self):
        self.show()

    def mousePressEvent(self, event):
        """Remember starting point of a line."""
        self.start_point = event.x(), event.y()

    def mouseReleaseEvent(self, event):
        """Draw line and calculate it distance."""
        x1, y1 = self.start_point

        painter = QPainter(self.pixmap)
        pen = QPen()
        pen.setColor(self.pen_color)

        painter.begin(self)
        painter.setPen(pen)

        # we need only vertical lines
        painter.drawLine(x1, y1, x1, event.y())
        # small horizontal lines at the end points
        painter.drawLine(x1 - 5, y1, x1 + 5, y1)
        painter.drawLine(x1 - 5, event.y(), x1 + 5, event.y())

        self.distance = self.legend * abs(y1 - event.y()) / self.scale_bar
        painter.drawText(
            x1 + 3, min(y1, event.y()) + abs(y1 - event.y()) // 2, f"{self.distance:.2}"
        )

        self.update()

    def paintEvent(self, event):
        """Redraw opened image after every event."""
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)
        self.initUI()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    scale = Main()
    sys.exit(app.exec_())
