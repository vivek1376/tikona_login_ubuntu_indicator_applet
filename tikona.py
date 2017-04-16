#!/usr/bin/env python

import sys
import mechanize
import time
import socket
import signal

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

APPINDICATOR_ID = 'tikona_login_appindicator'

tikona_username = '1120349127'
tikona_password = 'viVtk1@88'

url1='http://1.254.254.254'
url2='https://login.tikona.in/userportal/login.do?requesturi=http%3A%2F%2F1.254.254.254%2F%3F&act=null'
url3='https://login.tikona.in/userportal/newlogin.do?phone=0'
url4='https://login.tikona.in/userportal/logout.do?svccat=1'


def build_menu(ind):
    menu = gtk.Menu()
    item_login = gtk.MenuItem('Login')
    item_login.connect('activate', Login, ind)
    menu.append(item_login)

    item_logout = gtk.MenuItem('Logout')
    item_logout.connect('activate', Logout, ind)
    menu.append(item_logout)

    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)

    menu.show_all()

    return menu


def quit(_):
    notify.uninit()
    gtk.main_quit()


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
        return False


def timeout_signal_handler(signum, frame):
    raise Exception("Timed out!")


def notify_internet_status(indicator_obj=None):

    if check_internet():
        notify_connected(indicator_obj)
    else:
        notify_disconnected(indicator_obj)


def notify_connected(indicator_obj=None):
    if indicator_obj is not None:
        indicator_obj.set_icon(gtk.STOCK_YES)

    notify.Notification.new("<b>Connected :)</b>", None, None).show()


def notify_disconnected(indicator_obj=None):
    if indicator_obj is not None:
        indicator_obj.set_icon(gtk.STOCK_INFO)

    notify.Notification.new("<b>Disconnected</b>", None, None).show()


def Login(_, indicator_obj=None):

    if check_internet() == True:
        notify_connected(indicator_obj)
        return

    br = mechanize.Browser()

    br.set_handle_robots(False)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36')]

    try:
        res = br.open(url1, timeout=5)
        res = br.open(url2, data={}, timeout=5)
    except Exception as ex:
        print "login - exception in br open"
        notify_internet_status(indicator_obj)
        return

    br.select_form(name='form1')
    br.set_value(tikona_username, name='username')
    br.set_value(tikona_password, name='password')
    br.find_control('type').value = ['2']
    br.form.method = 'POST'
    br.form.action = url3

    signal.signal(signal.SIGALRM, timeout_signal_handler)

    try:
        signal.alarm(5)
        response = br.submit()
        signal.alarm(0)
    except Exception as ex:
        signal.alarm(0)
        print "exception: %s" % str(ex)

    notify_internet_status(indicator_obj)


def Logout(_, indicator_obj=None):

    if check_internet() == False:
        notify_disconnected(indicator_obj)
        return

    br = mechanize.Browser()

    br.set_handle_robots(False)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36')]

    try:
        res = br.open(url1, timeout=5)
        res = br.open(url2, {}, timeout=5)
        res = br.open(url4, timeout=5)
    except Exception as ex:
        print "logout - exception in br open"
        pass

    notify_internet_status(indicator_obj)


def main():
    if check_internet():
        app_icon = gtk.STOCK_YES
    else:
        app_icon = gtk.STOCK_INFO
    
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, app_icon, appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu(indicator))
    notify.init(APPINDICATOR_ID)

    gtk.main()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
