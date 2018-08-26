import sys
from http import HTTPStatus

import yaml
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import kibana_api
from manage_board import ManageBoard


class Login(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        # Checking if readme is selected
        try:
            with open('data.yml', 'r') as infile:
                try:
                    data = yaml.load(infile)
                    self.remember = data['remember']
                except yaml.YAMLError as ymler:
                    print('Error: ' + ymler)
                    self.remember = False
        except FileNotFoundError:
            self.remember = False

        QToolTip.setFont(QFont('Verdana', 8))
        self.statusBar().setFont(QFont('Verdana', 7))
        self.statusBar().showMessage('Ready')

        centralwidget = QWidget()

        # -------------------------- WIDGETS ----------------------------------#

        # Username Widgets
        userlabel = QLabel('Username:')
        userlabel.setAlignment(Qt.AlignHCenter)

        self.useredit = QLineEdit()
        self.useredit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.useredit.setToolTip('Case Sensitive')
        if self.remember is True:
            self.useredit.setText(data['username'])

        # Password Widgets
        passlabel = QLabel('Password:')
        passlabel.setAlignment(Qt.AlignHCenter)

        self.passedit = QLineEdit()
        self.passedit.setEchoMode(QLineEdit.Password)
        self.passedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.passedit.setToolTip('Case Sensitive')

        # Elastic Widgets
        elasticlabel = QLabel('Elastic IP:')
        elasticlabel.setAlignment(Qt.AlignHCenter)

        self.ipedit = QLineEdit()
        self.ipedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if self.remember is True:
            self.ipedit.setText(data['elasticip'])

        # Login Button
        loginbtn = QPushButton('Login', self)
        loginbtn.resize(loginbtn.sizeHint())
        loginbtn.setToolTip('You will need super user privileges to make changes to users/roles')
        loginbtn.clicked.connect(self.on_click)
        loginbtn.setShortcut('Return')

        # Checkbox
        self.checkbox = QCheckBox('Remember me', self)
        if self.remember is True:
            self.checkbox.setCheckState(Qt.Checked)

        self.checkbox.stateChanged.connect(self.clickBox)

        # ------------------------ Creating Layout ---------------------------#
        vbox1 = QVBoxLayout()
        vbox1.addWidget(userlabel)
        vbox1.addWidget(self.useredit, 0, Qt.AlignHCenter)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(passlabel)
        vbox2.addWidget(self.passedit, 0, Qt.AlignHCenter)

        vbox3 = QVBoxLayout()
        vbox3.addWidget(elasticlabel)
        vbox3.addWidget(self.ipedit, 0, Qt.AlignHCenter)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        vbox.addLayout(vbox1)
        vbox.addSpacerItem(QSpacerItem(10, 10))
        vbox.addLayout(vbox2)
        vbox.addSpacerItem(QSpacerItem(10, 10))
        vbox.addLayout(vbox3)
        vbox.addWidget(loginbtn)
        vbox.addWidget(self.checkbox, 0, Qt.AlignHCenter)

        centralwidget.setLayout(vbox)
        self.setCentralWidget(centralwidget)

        # self.setGeometry(250,300,250,200)
        self.setWindowTitle('Elastic')
        self.show()

    ''' Checking for the checkbox parameter. If checkbox is checked the remember attribute will be set to True
        and next time the program loads it will set the fields username and elasticip to the saved values stored in
        data.yml
    '''

    def clickBox(self, state):

        if state == Qt.Checked:
            self.remember = True
        else:
            self.remember = False

    # if
    def write_yaml(self):

        data = {
            'remember': self.remember,
            'username': self.useredit.text() if self.remember is True else '',
            'elasticip': self.ipedit.text() if self.remember is True else ''
        }

        with open('data.yml', 'w') as outfile:
            yaml.dump(data, outfile)

    @pyqtSlot()
    def on_click(self):
        self.statusBar().showMessage('Connecting to Elastic Server')

        result = kibana_api.authenticate(self.useredit.text(), self.passedit.text(), self.ipedit.text())

        if not isinstance(result, str):
            if result != HTTPStatus.OK.value:
                error = HTTPStatus(result)
                self.statusBar().showMessage("Error " + str(error.value) + ', ' + error.phrase)
                return
        else:
            QMessageBox().critical(self, "Error", result, QMessageBox.Ok)
            return

        self.statusBar().showMessage('Connected')

        # Write yml file
        self.write_yaml()

        # sleep(0.5)
        self.board = ManageBoard()
        self.close()

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()
    sys.exit(app.exec_())
