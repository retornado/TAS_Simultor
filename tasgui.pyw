# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 17:27:21 2017

@author: luowei
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from TasCommand import *
import TasPara as tp
import TasSimulate as ts
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as figureCanvas
import matplotlib.pyplot as plt
import sys


class DrawWidget(QWidget):
    def __init__(self,parent=None):
        super(DrawWidget,self).__init__(parent)
        #self.figure = plt.gcf() #返回当前的figure
        self.figure = plt.figure(figsize=(11*2,6*2))
        self.canvas = figureCanvas(self.figure)
        self.browser = QTextBrowser()
        self.browser_error = QTextBrowser()

        self.lineedit = QLineEdit('Enter scan order')
        self.lineedit.selectAll()
        self.lineedit.setFocus()
        
        self.connect(self.lineedit,SIGNAL('returnPressed()'),self.updateUi)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.addWidget(self.browser)
        layout.addWidget(self.browser_error)
        layout.addWidget(self.lineedit)
        self.setWindowTitle("CTAS Simulator --- luowei 2017")

    def updateUi(self):
        try:
            text = unicode(self.lineedit.text())
            junk = text_to_order(text)
            try:
                obj = eval(junk)
                data_plot = obj.data_plot
                points = obj.points
                if not data_plot[tp.TasStatus.tas_status.index | tp.LimitNumb.limit_example.index].isnull().any().any():
                    a  = ts.TasAnimate(self.figure,data_plot)
                    a.tas_animate()
                    self.canvas.draw()
                    self.browser.append("%s" % (points))
            except Exception as exc:
                self.browser_error.append(exc.__str__())
                # clear input in lineedit
            self.lineedit.clear()
        except:
            pass


def main():
    app = QApplication(sys.argv)
    ui = DrawWidget()
    ui.show()
    app.exec_()