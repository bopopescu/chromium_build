# Copyright (c) 2011 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from master import master_config
from master.factory import chromium_factory

defaults = {}

helper = master_config.Helper(defaults)
B = helper.Builder
D = helper.Dependent
F = helper.Factory
S = helper.Scheduler

def win(): return chromium_factory.ChromiumFactory('src/build', 'win32')


################################################################################
## Release
################################################################################

defaults['category'] = '1webkit win deps'

# Archive location
rel_archive = master_config.GetArchiveUrl('ChromiumWebkit',
                                          'Webkit Win Builder (deps)',
                                          'webkit-win-pinned-rel', 'win32')

#
# Main release scheduler for chromium
#
S('s1_chromium_rel', branch='src', treeStableTimer=60)

#
# Dependent scheduler for the dbg builder
#
D('s1_chromium_rel_dep', 's1_chromium_rel')

#
# Win Rel Builder
#
B('Webkit Win Builder (deps)', 'f_webkit_win_rel',
  scheduler='s1_chromium_rel', builddir='webkit-win-pinned-rel')
F('f_webkit_win_rel', win().ChromiumFactory(
    slave_type='Builder',
    project='all.sln;webkit_builder_win'))

#
# Win Rel Webkit testers
#
B('Webkit Win (deps)', 'f_webkit_rel_tests',
  scheduler='s1_chromium_rel_dep', auto_reboot=True)
F('f_webkit_rel_tests', win().ChromiumFactory(
    slave_type='Tester',
    build_url=rel_archive,
    tests=['test_shell', 'webkit', 'webkit_gpu', 'webkit_unit'],
    factory_properties={'archive_webkit_results': True,
                        'test_results_server': 'test-results.appspot.com'}))

################################################################################
## Debug
################################################################################

dbg_archive = master_config.GetArchiveUrl('ChromiumWebkit',
                                          'Webkit Win Builder (deps)(dbg)',
                                          'webkit-win-pinned-dbg', 'win32')

#
# Main debug scheduler for chromium
#
S('s1_chromium_dbg', branch='src', treeStableTimer=60)

#
# Dependent scheduler for the dbg builder
#
D('s1_chromium_dbg_dep', 's1_chromium_dbg')

#
# Win Dbg Builder
#
B('Webkit Win Builder (deps)(dbg)', 'f_webkit_win_dbg',
  scheduler='s1_chromium_dbg', builddir='webkit-win-pinned-dbg')
F('f_webkit_win_dbg', win().ChromiumFactory(
    target='Debug',
    slave_type='Builder',
    project='all.sln;webkit_builder_win'))

#
# Win Dbg Webkit testers
#

B('Webkit Win (deps)(dbg)(1)', 'f_webkit_dbg_tests_1',
  scheduler='s1_chromium_dbg_dep', auto_reboot=True)
F('f_webkit_dbg_tests_1', win().ChromiumFactory(
    target='Debug',
    slave_type='Tester',
    build_url=dbg_archive,
    tests=['test_shell', 'webkit', 'webkit_gpu', 'webkit_unit'],
    factory_properties={'archive_webkit_results': True,
                        'test_results_server': 'test-results.appspot.com',
                        'layout_part': '1:2'}))

B('Webkit Win (deps)(dbg)(2)', 'f_webkit_dbg_tests_2',
  scheduler='s1_chromium_dbg_dep', auto_reboot=True)
F('f_webkit_dbg_tests_2', win().ChromiumFactory(
    target='Debug',
    slave_type='Tester',
    build_url=dbg_archive,
    tests=['webkit', 'webkit_gpu'],
    factory_properties={'archive_webkit_results': True,
                        'test_results_server': 'test-results.appspot.com',
                        'layout_part': '2:2'}))

def Update(config, active_master, c):
  return helper.Update(c)
