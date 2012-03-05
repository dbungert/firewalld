#
# Copyright (C) 2011,2012 Red Hat, Inc.
#
# Authors:
# Thomas Woerner <twoerner@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import dbus
import pwd

def command_of_pid(pid):
    """ Get command for pid from /proc """
    try:
        f = open("/proc/%d/cmdline" % pid, "r")
        cmd = f.readlines()[0].replace('\0', " ").strip()
        f.close()
    except:
        return None
    return cmd

def pid_of_sender(bus, sender):
    """ Get pid from sender string using 
    org.freedesktop.DBus.GetConnectionUnixProcessID """

    dbus_obj = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
    dbus_iface = dbus.Interface(dbus_obj, 'org.freedesktop.DBus')

    try:
        pid = int(dbus_iface.GetConnectionUnixProcessID(sender))
    except:
        return None
    return pid

def uid_of_sender(bus, sender):
    """ Get user id from sender string using 
    org.freedesktop.DBus.GetConnectionUnixUser """

    dbus_obj = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
    dbus_iface = dbus.Interface(dbus_obj, 'org.freedesktop.DBus')

    try:
        uid = dbus_iface.GetConnectionUnixUser(sender)
    except:
        return None
    return uid

def user_of_uid(uid):
    """ Get user for uid from pwd """

    try:
        pws = pwd.getpwuid(uid)
    except Exception, msg:
        return None
    return pws[0]

def context_of_sender(bus, sender):
    """ Get SELinux context from sender string using 
    org.freedesktop.DBus.GetConnectionSELinuxSecurityContext """

    dbus_obj = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
    dbus_iface = dbus.Interface(dbus_obj, 'org.freedesktop.DBus')

    try:
        context =  dbus_iface.GetConnectionSELinuxSecurityContext(sender)
    except:
        return None
    return context

def command_of_sender(bus, sender):
    """ Return command of D-BUS sender """

    return command_of_pid(pid_of_sender(bus, sender))

def user_of_sender(bus, sender):
    return user_of_uid(uid_of_sender(bus, sender))

def dbus_to_python(obj):
    if not obj:
        return obj
    elif isinstance(obj, dbus.types.Boolean):
        return obj == True
    elif isinstance(obj, dbus.types.String) or \
            isinstance(obj, dbus.types.UTF8String) or \
            isinstance(obj, dbus.types.ObjectPath):
        return str(obj)
    elif isinstance(obj, dbus.types.Byte) or \
            isinstance(obj, dbus.types.Int16) or \
            isinstance(obj, dbus.types.Int32) or \
            isinstance(obj, dbus.types.Int64) or \
            isinstance(obj, dbus.types.UInt16) or \
            isinstance(obj, dbus.types.UInt32) or \
            isinstance(obj, dbus.types.UInt64):
        return int(obj)
    elif isinstance(obj, dbus.types.Double):
        return float(obj)
    elif isinstance(obj, dbus.types.Array) or \
            isinstance(obj, dbus.types.Struct):
        ret = [ ]
        for x in obj:
            ret.append(dbus_to_python(x))
        return ret
    elif isinstance(obj, dbus.types.Dictionary):
        ret = { }
        for x in obj.keys():
            ret[dbus_to_python(x)] = dbus_to_python(obj[x])
        return ret
    else:
        raise TypeError, "Unhandled %s" % obj
