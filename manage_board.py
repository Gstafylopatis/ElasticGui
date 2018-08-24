import time

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot

import kibana_api


class ManageBoard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        QLabel.setFont(self, QFont('Verdana', 8))

        # -------------------------- WIDGETS ----------------------------------#
        centralwidget = QWidget()

        userlabel = QLabel('Users: ')
        rolelabel = QLabel('Roles: ')

        self.userslist = QListWidget(self)
        self.roleslist = QListWidget(self)

        self.users = kibana_api.get_users()
        self.userslist.addItems(self.users)

        self.roles = kibana_api.get_roles()

        for index, user in enumerate(self.users):
            if 'superuser' in user:
                self.roles.insert(index, 'superuser')

        self.roleslist.addItems(self.roles)

        self.userslist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.userslist.customContextMenuRequested.connect(self.list_context)

        #------------------------- Creating Buttons --------------------------#

        man_createBtn = QPushButton('Manually create user')
        man_createBtn.clicked.connect(self.on_click)
        man_createBtn.setObjectName('Manual')

        auto_createBtn = QPushButton('Automatically create user')
        auto_createBtn.clicked.connect(self.on_click)
        auto_createBtn.setObjectName('Automatic')

        # ------------------------ Creating Layout ---------------------------#
        layout = QGridLayout()

        layout.addWidget(userlabel, 0, 0)
        layout.addWidget(rolelabel, 0, 1)
        layout.addWidget(self.userslist, 1, 0)
        layout.addWidget(self.roleslist, 1, 1)
        layout.addWidget(man_createBtn, 2, 0)
        layout.addWidget(auto_createBtn, 2,1)

        centralwidget.setLayout(layout)

        self.setCentralWidget(centralwidget)

        #self.setGeometry(250,300,250,200)
        self.setWindowTitle('Elastic')
        self.show()

    def list_context(self, pos):

        menu = QMenu(self)

        delAct = menu.addAction('Delete user')

        action = menu.exec_(self.mapToGlobal(pos))

        if action == delAct:
            print("shit")

    @pyqtSlot()
    def on_click(self):

        if self.sender().objectName() == 'Manual':
            self.show_dialog()

    def show_dialog(self):

        dialog = QDialog()

        #--------------- Dialog Widgets ---------------#
        userlabel = QLabel('Username:', dialog)
        userlabel.setAlignment(Qt.AlignHCenter)

        self.useredit = QLineEdit(dialog)
        self.useredit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.useredit.setToolTip('Case Sensitive')

        passlabel = QLabel('Password:', dialog)
        passlabel.setAlignment(Qt.AlignHCenter)

        self.passedit = QLineEdit(dialog)
        self.passedit.setEchoMode(QLineEdit.Password)
        self.passedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.passedit.setToolTip('Case Sensitive')

        passlabelconfirm = QLabel('Confirm Password:', dialog)
        passlabelconfirm.setAlignment(Qt.AlignHCenter)

        self.passeditconfirm = QLineEdit(dialog)
        self.passeditconfirm.setEchoMode(QLineEdit.Password)
        self.passeditconfirm.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.passeditconfirm.setToolTip('Case Sensitive')

        confBtn = QPushButton('Confirm', dialog)
        confBtn.clicked.connect(dialog.accept)
        cancelBtn = QPushButton('Cancel', dialog)

        #--------------- Dialog Layout ---------------#
        hbox1 = QHBoxLayout()
        hbox1.addWidget(userlabel)
        hbox1.addWidget(self.useredit, 0, Qt.AlignHCenter)


        hbox2 = QHBoxLayout()
        hbox2.addWidget(passlabel)
        hbox2.addWidget(self.passedit, 0, Qt.AlignHCenter)



        hbox3 = QHBoxLayout()
        hbox3.addWidget(passlabelconfirm)
        hbox3.addWidget(self.passeditconfirm, 0, Qt.AlignHCenter)

        hbox4 =QHBoxLayout()
        hbox4.addWidget(confBtn)
        hbox4.addWidget(cancelBtn)


        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        vbox.addLayout(hbox1)
        vbox.addSpacerItem(QSpacerItem(10, 10))
        vbox.addLayout(hbox2)
        vbox.addSpacerItem(QSpacerItem(10, 10))
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)

        dialog.setWindowTitle("Create user")
        dialog.setLayout(vbox)
        res = dialog.exec()

        if res == QDialog.Accepted:
            if self.passedit.text() == self.passeditconfirm.text():
                print("good")

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Escape:
            self.close()
