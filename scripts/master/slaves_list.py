#!/usr/bin/python
# Copyright (c) 2011 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import sys


def EntryToSlaveName(entry):
  """Extracts the buildbot slave name from the slaves list entry.

  The slave list entry is a dict."""
  return entry.get('slavename', None) or entry.get('hostname', None)


def _obj_as_list(obj):
  """Converts strings as 1 entry list."""
  if not isinstance(obj, (tuple, list)):
    return [obj]
  return obj


def _lower_values(s):
  """Returns a list of strings lower()'ed.

  If a string is passed, a one item list is returned.
  """
  return [x.lower() for x in _obj_as_list(s)]


def _Filter(slaves, key, value):
  """Filters slaves to keep only those with value in key,
  slaves[key] being a list or converted to a list.
  """
  if not value:
    return slaves
  value = value.lower()

  if value.startswith('~') or value.startswith('!'):
    value = value[1:]
    return [s for s in slaves if value not in _lower_values(s.get(key, []))]
  else:
    return [s for s in slaves if value in _lower_values(s.get(key, []))]


def _CheckDupes(items):
  dupes = set()
  while items:
    x = items.pop()
    assert x
    if x in items:
      dupes.add(x)
  if dupes:
    print >> sys.stderr, 'Found slave dupes!\n  %s' % ', '.join(dupes)
    assert False


class BaseSlavesList(object):
  def __init__(self, slaves, default_master=None):
    self.slaves = slaves
    self.default_master = default_master
    _CheckDupes([EntryToSlaveName(x).lower() for x in self.slaves])

  def GetSlaves(self, master=None, builder=None, os=None, tester=None,
                bits=None, version=None):
    """Returns the slaves listed in the private/slaves_list.py file.

    Optionally filter with master, builder, os, tester and bitness type.
    """
    slaves = self.slaves
    slaves = _Filter(slaves, 'master', master or self.default_master)
    slaves = _Filter(slaves, 'os', os)
    slaves = _Filter(slaves, 'bits', bits)
    slaves = _Filter(slaves, 'version', version)
    slaves = _Filter(slaves, 'builder', builder)
    slaves = _Filter(slaves, 'tester', tester)
    return slaves

  def GetSlave(self, master=None, builder=None, os=None, tester=None, bits=None,
               version=None):
    """Returns one slave or none if none or multiple slaves are found."""
    slaves = self.GetSlaves(master, builder, os, tester, bits, version)
    if len(slaves) != 1:
      return None
    return slaves[0]

  def GetSlavesName(self, master=None, builder=None, os=None, tester=None,
                    bits=None, version=None):
    """Similar to GetSlaves() except that it only returns the slave names."""
    return [
        EntryToSlaveName(e)
        for e in self.GetSlaves(master, builder, os, tester, bits, version)
    ]

  def GetSlaveName(self, master=None, builder=None, os=None, tester=None,
                   bits=None, version=None):
    """Similar to GetSlave() except that it only returns the slave name."""
    return EntryToSlaveName(
        self.GetSlave(master, builder, os, tester, bits, version))


class SlavesList(BaseSlavesList):
  def __init__(self, filename, default_master=None):
    local_vars = {}
    execfile(filename, local_vars)
    BaseSlavesList.__init__(self, local_vars['slaves'], default_master)


def Main(argv=None):
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('-f', '--filename', help='File to parse, REQUIRED')
  parser.add_option('-m', '--master', help='Master to filter')
  parser.add_option('-b', '--builder', help='Builder to filter')
  parser.add_option('-o', '--os', help='OS to filter')
  parser.add_option('-t', '--tester', help='Tester to filter')
  parser.add_option('-v', '--version', help='OS\'s version to filter')
  parser.add_option('--bits', help='OS bitness to filter')
  options, _ = parser.parse_args(argv)
  if not options.filename:
    parser.print_help()
    print('\nYou must specify a file to get the slave list from')
    return 1
  slaves = SlavesList(options.filename)
  for slave in slaves.GetSlavesName(options.master, options.builder,
                                    options.os, options.tester, options.bits,
                                    options.version):
    print slave
  return 0


if __name__ == '__main__':
  sys.exit(Main())
