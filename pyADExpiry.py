#!/usr/bin/env python2

import sys
# XXX(coolj): is there a better way to make sure this is
#             added to the path inside a virtualenv?
sys.path.extend(['/usr/local/lib/python2.7', '/usr/lib/python2.7/dist-packages'])

import os
import signal
from datetime import datetime
from ldap3 import Server, Connection, ALL
from ConfigParser import ConfigParser
from PyQt4 import QtGui
from PyQt4.QtCore import QTimer


class PyADExpiry(object):

    def __init__(self):
        exp_days = self.get_ad_expiry()

        app = QtGui.QApplication(sys.argv)
        QtGui.QApplication.setQuitOnLastWindowClosed(False)


        self.ok_icon = QtGui.QIcon('lock.png')
        self.warn_icon = QtGui.QIcon('warn.png')

        self.tray_icon = QtGui.QSystemTrayIcon(self.ok_icon, app)
        self.tray_icon.activated.connect(self.activate_callback)
        
        menu = QtGui.QMenu()
        exit_action = QtGui.QAction('&Exit', app)
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
        self.check_expiry()
        self.tray_icon.setToolTip('You AD password will expire in {} days.'.format(self.exp_days))

        timer = QTimer()
        timer.timeout.connect(self.activate_callback)
        timer.start(86400000) # check every 24 hours

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        sys.exit(app.exec_())

    def get_config(self):
        config = ConfigParser()
        home_dir = os.path.expanduser('~')
        curr_dir = os.getcwd()
        inst_dir = os.path.dirname(sys.argv[0])
        for path in (home_dir, curr_dir, inst_dir):
            conf_file = os.path.join(path, 'pyADExpiry.ini')
            if os.path.exists(conf_file):
                config.read(conf_file)
                break
        else:
            config.set('DEFAULT', 'full_name', 'Fill This In')
            config.set('DEFAULT', 'edir_uri', 'auth.edir.rackspace.com')
            conf_file = os.path.join(home_dir, 'pyADExpiry.ini')
            with open(conf_file, 'w') as fh:
                config.write(fh)
            print('Wrote config file to {}.'
                  ' Please edit the file and set full_name to your'
                  ' name as displayed in CORE'.format(conf_file))
            sys.exit(1)
        return config

    def get_ad_expiry(self):
        config = self.get_config()
        server = Server(config.get('DEFAULT', 'edir_uri'), get_info=ALL)
        conn = Connection(server, auto_bind=True)
        result = conn.search('o=rackspace',
                             '(displayname={})'.format(config.get('DEFAULT', 'full_name')),
                             attributes=['passwordExpirationTime'])
        
        if conn.entries and hasattr(conn.entries[0], 'passwordExpirationTime'):
            expiry = str(conn.entries[0].passwordExpirationTime)
            # format: 2017-08-23 08:58:32+00:00
            exp_date = datetime.strptime(expiry.split('+')[0],
                                         '%Y-%m-%d %H:%M:%S')
            exp_days = (exp_date - datetime.now()).days
            return exp_days

    def check_expiry(self):
        self.exp_days = self.get_ad_expiry()
        if self.exp_days <= 14:
            self.show_warn_dialog()
            self.tray_icon.setIcon(self.warn_icon)
        else:
            self.tray_icon.setIcon(self.ok_icon)

    def show_warn_dialog(self):
        dialog = QtGui.QMessageBox()
        if self.exp_days <= 14:
            dialog.setIcon(QtGui.QMessageBox.Warning)
        else:
            dialog.setIcon(QtGui.QMessageBox.Information)
        dialog.setWindowTitle('Password expiration')
        dialog.setText('Your AD password will expire in {} days.'.format(self.exp_days))
        dialog.exec_()

    def activate_callback(self, reason=None):
        if not reason or reason == QtGui.QSystemTrayIcon.Trigger:
            if not hasattr(self, 'exp_days'):
                self.exp_days = self.get_ad_expiry()
            self.show_warn_dialog()


if __name__ == '__main__':
    PyADExpiry()

