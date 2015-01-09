#***************************************************************************
#*   (c) Yorik van Havre (yorik@uncreated.net) 2014                        *
#*                                                                         *
#*   This file is part of the FreeCAD CAx development system.              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   FreeCAD is distributed in the hope that it will be useful,            *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************/


'''
These are a common functions and classes for creating custom post processors.  
'''

from PySide import QtCore, QtGui
import FreeCADGui

class OldHighlighter(QtGui.QSyntaxHighlighter):
    def highlightBlock(self, text):
        myClassFormat = QtGui.QTextCharFormat()
        myClassFormat.setFontWeight(QtGui.QFont.Bold)
        myClassFormat.setForeground(QtCore.Qt.green)
        # the regex pattern to be colored
        pattern = "(G.*?|M.*?)\\s"
        expression = QtCore.QRegExp(pattern)
        index = text.index(expression)
        while index >= 0:
            length = expression.matchedLength()
            setFormat(index, length, myClassFormat)
            index = text.index(expression, index + length)
            


class GCodeHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(GCodeHighlighter, self).__init__(parent)
        

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.cyan)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)
        keywordPatterns = ["\\bG[0-9]+\\b",
                           "\\bM[0-9]+\\b"]

        self.highlightingRules = [(QtCore.QRegExp(pattern), keywordFormat) for pattern in keywordPatterns]

        speedFormat = QtGui.QTextCharFormat()
        speedFormat.setFontWeight(QtGui.QFont.Bold)
        speedFormat.setForeground(QtCore.Qt.green)
        self.highlightingRules.append((QtCore.QRegExp("\\bF[0-9\\.]+\\b"),speedFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)



class GCodeEditorDialog(QtGui.QDialog):
    def __init__(self, parent = FreeCADGui.getMainWindow()):
        QtGui.QDialog.__init__(self,parent)

        layout = QtGui.QVBoxLayout(self)

        # nice text editor widget for editing the gcode
        self.editor = QtGui.QTextEdit()
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.editor.setFont(font)
        self.editor.setText("G01 X55 Y4.5 F300.0")
        self.highlighter = GCodeHighlighter(self.editor.document())
        layout.addWidget(self.editor)

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

def stringsplit(commandline):
    returndict = {'command':None, 'X':None, 'Y':None, 'Z':None, 'A':None, 'B':None, 'F':None, 'S':None, 'I':None, 'J':None,'K':None, 'txt': None}
    wordlist = [a.strip() for a in commandline.split(" ")]
    if wordlist[0][0] == '(':
        returndict['command'] = 'message'
        returndict['txt'] = wordlist[0]
    else:
        returndict['command'] = wordlist[0]
    for word in wordlist[1:]:
        returndict[word[0]] = word[1:]

    return returndict 
