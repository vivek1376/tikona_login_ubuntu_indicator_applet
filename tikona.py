#!/usr/bin/env python 

import sys
import mechanize
import time
from optparse import OptionParser
import getpass
import socket
import signal

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
import json
from urllib2 import Request, urlopen, URLError
from gi.repository import Notify as notify

APPINDICATOR_ID = 'tikona_login_appindicator'

username = '1120349127'
password = 'viVtk1@88'

def build_menu():
    menu = gtk.Menu()
    item_login = gtk.MenuItem('Login')
    item_login.connect('activate', Login)
    menu.append(item_login)

    item_logout = gtk.MenuItem('Logout')
    item_logout.connect('activate', Logout)
    menu.append(item_logout)

    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)

    menu.show_all()

    return menu


def quit(_):
    notify.uninit()
    gtk.main_quit()


class CustomTimeoutException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)


def check_internet(host="8.8.8.8", port=53, timeout=2):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
#        print ex.message
        return False


def timeout_signal_handler(signum, frame):
    raise CustomTimeoutException("Timed out!")

def notify_connected():
    notify.Notification.new("<b>Connected :)</b>", None, None).show()

def notify_disconnected():
    notify.Notification.new("<b>Not Connected :(</b>", None, None).show()

def Login(_):
    if check_internet() == True:
        notify_connected()
        return
        
    print ">>> trying to connect.."
    br = mechanize.Browser()
    response  = br.open('https://login.tikona.in')
    print ">>> ok"
    print ">>> " + br.title()
    #print response.geturl()
    #print ">>>"
    print ">>> redirecting to login.do"
    br.select_form(nr=0)
    br.form.action = 'https://login.tikona.in/userportal/login.do?requesturi=http%3A%2F%2F1.254.254.254%2F&act=null'
    br.form.method = 'POST'
    print ">>> submitting.."
    response = br.submit()
    print ">>> got response"
    br.select_form(name="form1")
    br["username"] = username
    br["password"] = password
    br.find_control(name="type").value = ["2"]
    br.form.method="POST"
    print ">>> proceeding to login.."
    br.form.action="https://login.tikona.in/userportal/newlogin.do?phone=0"
#    print ">>> loggin in..."
 #   print ">>> ok " 
  #  print ">>> " + br.title()

    signal.signal(signal.SIGALRM, timeout_signal_handler)
    signal.alarm(5)

    try:
        response = br.submit()
        signal.alarm(0)
    except CustomTimeoutException as ex:
        print "handled"
    except Exception:
        print "handled2"

    print response.info()

    if check_internet():
        notify_connected()
    else:
        notify_disconnected()

    #response.get_data()

    #print response.read()


def Logout(_):
    print "Logging out.."
    br = mechanize.Browser()
    response = br.open('https://login.tikona.in/userportal/logout.do?svccat=1')
    print response.geturl()
    print response.info()
    print response.read()


def main():
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, gtk.STOCK_YES, appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    notify.init(APPINDICATOR_ID)
 
    gtk.main()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
