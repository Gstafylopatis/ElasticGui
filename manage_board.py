import time
from http import HTTPStatus

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

        self.userslist.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.userslist.setObjectName('users')
        self.userslist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.userslist.customContextMenuRequested.connect(self.list_context)

        self.roleslist.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.roleslist.setObjectName('roles')
        self.roleslist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.roleslist.customContextMenuRequested.connect(self.list_context)


        self.update_lists()

        # ------------------------- Creating Buttons --------------------------#

        man_createBtn = QPushButton('Manually create user')
        man_createBtn.clicked.connect(self.on_click)
        man_createBtn.setObjectName('Manual')

        auto_createBtn = QPushButton('Automatically create user')
        auto_createBtn.clicked.connect(self.on_click)
        auto_createBtn.setObjectName('Automatic')
        auto_createBtn.setToolTip('Gets distinct device names from Elastic database'
                                  ' and creates a user for each one with default'
                                  ' password="qwerty"')

        # ------------------------ Creating Layout ---------------------------#
        layout = QGridLayout()

        layout.addWidget(userlabel, 0, 0)
        layout.addWidget(rolelabel, 0, 1)
        layout.addWidget(self.userslist, 1, 0)
        layout.addWidget(self.roleslist, 1, 1)
        layout.addWidget(man_createBtn, 2, 0)
        layout.addWidget(auto_createBtn, 2, 1)

        centralwidget.setLayout(layout)

        self.setCentralWidget(centralwidget)

        # self.setGeometry(250,300,250,200)
        self.setWindowTitle('Elastic')
        self.show()

    def list_context(self, pos):

        menu = QMenu(self)

        delAct = menu.addAction('Delete')

        action = menu.exec_(self.sender().mapToGlobal(pos))

        if action == delAct:
            if self.sender().objectName() == 'users':
                res = kibana_api.delete_users(self.userslist.selectedItems())

                if res == 'OK':
                    QMessageBox().information(self, 'Success', 'User(s) deleted successfully', QMessageBox.Ok)
                    self.update_lists()

                else:
                    QMessageBox().warning(self, 'Warning', res, QMessageBox.Ok)

            else:
                res = kibana_api.delete_roles(self.roleslist.selectedItems())

                if res == 'OK':
                    QMessageBox().information(self, 'Success', 'Role(s) deleted successfully', QMessageBox.Ok)
                    self.update_lists()

                else:
                    QMessageBox().warning(self, 'Warning', res, QMessageBox.Ok)

    @pyqtSlot()
    def on_click(self):

        if self.sender().objectName() == 'Manual':
            self.show_dialog()
        else:
            req = kibana_api.manage_user()
            if req == 'OK':
                QMessageBox().information(self, 'Success', 'Users created '
                                          'successfully', QMessageBox.Ok)
                self.update_lists()

            else:
                QMessageBox().warning(self, 'Warning', req, QMessageBox.Ok)


    def show_dialog(self):

        dialog = QDialog()

        # --------------- Dialog Widgets ---------------#
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

        normaluser = QRadioButton('Normal user')
        normaluser.setChecked(True)
        superuser = QRadioButton('Superuser')

        normaluser.toggled.connect(lambda: superuser.setChecked(False))
        superuser.toggled.connect(lambda: normaluser.setChecked(False))

        confBtn = QPushButton('Confirm', dialog)
        confBtn.clicked.connect(dialog.accept)

        cancelBtn = QPushButton('Cancel', dialog)
        cancelBtn.clicked.connect(dialog.reject)

        # --------------- Dialog Layout ---------------#
        hbox1 = QHBoxLayout()
        hbox1.addWidget(userlabel)
        hbox1.addWidget(self.useredit, 0, Qt.AlignHCenter)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(passlabel)
        hbox2.addWidget(self.passedit, 0, Qt.AlignHCenter)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(passlabelconfirm)
        hbox3.addWidget(self.passeditconfirm, 0, Qt.AlignHCenter)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(normaluser)
        hbox4.addWidget(superuser)

        hbox5 = QHBoxLayout()
        hbox5.addWidget(confBtn)
        hbox5.addWidget(cancelBtn)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        vbox.addLayout(hbox1)
        vbox.addSpacerItem(QSpacerItem(10, 10))
        vbox.addLayout(hbox2)
        vbox.addSpacerItem(QSpacerItem(10, 10))
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)

        dialog.setWindowTitle("Create user")
        dialog.setLayout(vbox)
        res = dialog.exec()

        if res == QDialog.Accepted:

            res = kibana_api.validate(self.useredit.text(), self.passedit.text())

            if res == "Bad username":
                QMessageBox().critical(self, 'Error', 'Invalid username\nUsername\should not contain special '
                                                      'characters([!@#$%^&*()+=<>.,?/"\';:|\\[]{}`~) or space or '
                                                      'be blank',
                                       QMessageBox.Ok)
                return

            if res == "Bad password":
                QMessageBox().critical(self, 'Error', 'Invalid password\nPassword has to be >6 characters and cannot '
                                                      'contain whitespace or be blank',
                                       QMessageBox.Ok)
                return

            if self.passedit.text() == self.passeditconfirm.text():
                role = 'normal' if normaluser.isChecked() else 'superuser'
                print(role)
                req = kibana_api.manage_user(self.useredit.text(), self.passedit.text(), role)
                if req == 'OK':
                    QMessageBox().information(self, 'Success', 'User created successfully', QMessageBox.Ok)
                    self.update_lists()

                else:
                    QMessageBox().warning(self, 'Warning', req, QMessageBox.Ok)
            else:
                QMessageBox().warning(self, 'Warning', 'Passwords do not match', QMessageBox.Ok)

    def update_lists(self):

        users = kibana_api.get_users()
        roles = kibana_api.get_roles()

        self.userslist.clear()
        self.roleslist.clear()

        self.userslist.addItems(users)

        for index, user in enumerate(users):
            if 'superuser' in user:
                roles.insert(index, 'superuser')

        self.roleslist.addItems(roles)

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Escape:
            self.close()
