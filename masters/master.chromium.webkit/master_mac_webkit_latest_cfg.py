# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# WebKit test builders using the Skia graphics library.
#
# Note that we use the builder vs tester role separation differently
# here than in our other buildbot configurations.
#
# In this configuration, the testers build the tests themselves rather than
# extracting them from the builder.  That's because these testers always
# fetch from webkit HEAD, and by the time the tester runs, webkit HEAD may
# point at a different revision than it did when the builder fetched webkit.
#
# Even though the testers don't extract the build package from the builder,
# the builder is still useful because it can cycle more quickly than the
# builder+tester can, and can alert us more quickly to build breakages.
#
# If you have questions about this, you can ask nsylvain.

from main import main_config
from main.factory import annotator_factory

import main_site_config

ActiveMain = main_site_config.ChromiumWebkit

defaults = {}

helper = main_config.Helper(defaults)
B = helper.Builder
F = helper.Factory
T = helper.Triggerable


m_annotator = annotator_factory.AnnotatorFactory()

defaults['category'] = 'layout'

################################################################################
## Release
################################################################################

#
# Triggerable scheduler for testers
#
T('s5_webkit_rel_trigger')

#
# Mac Rel Builder
#
B('WebKit Mac Builder', 'f_webkit_mac_rel',
  auto_reboot=False, scheduler='global_scheduler',
  builddir='webkit-mac-latest-rel')
F('f_webkit_mac_rel', m_annotator.BaseFactory(
    'chromium', triggers=['s5_webkit_rel_trigger']))

#
# Mac Rel WebKit testers
#

B('WebKit Mac10.6', 'f_webkit_rel_tests_106', scheduler='s5_webkit_rel_trigger')
F('f_webkit_rel_tests_106', m_annotator.BaseFactory('chromium'))

B('WebKit Mac10.7', 'f_webkit_rel_tests_107', scheduler='s5_webkit_rel_trigger')
F('f_webkit_rel_tests_107', m_annotator.BaseFactory('chromium'))

B('WebKit Mac10.8', 'f_webkit_rel_tests_108',
  scheduler='s5_webkit_rel_trigger')
F('f_webkit_rel_tests_108', m_annotator.BaseFactory('chromium'))

B('WebKit Mac10.9 (retina)', 'f_webkit_rel_tests_109_retina',
  scheduler='s5_webkit_rel_trigger')
F('f_webkit_rel_tests_109_retina', m_annotator.BaseFactory('chromium'))

B('WebKit Mac10.9', 'f_webkit_rel_tests_109',
  scheduler='s5_webkit_rel_trigger')
F('f_webkit_rel_tests_109', m_annotator.BaseFactory('chromium'))

B('WebKit Mac10.10', 'f_webkit_rel_tests_1010',
  scheduler='s5_webkit_rel_trigger')
F('f_webkit_rel_tests_1010', m_annotator.BaseFactory('chromium'))

B('WebKit Mac non-Oilpan', 'f_webkit_mac_oilpan_rel',
  scheduler='global_scheduler', category='oilpan')
F('f_webkit_mac_oilpan_rel', m_annotator.BaseFactory('chromium'))


################################################################################
## Debug
################################################################################

# Archive location
dbg_archive = main_config.GetGSUtilUrl('chromium-build-transfer',
                                         'WebKit Mac Builder (dbg)')

#
# Triggerable scheduler for testers
#
T('s5_webkit_dbg_trigger')

#
# Mac Dbg Builder
#
B('WebKit Mac Builder (dbg)', 'f_webkit_mac_dbg', auto_reboot=False,
  scheduler='global_scheduler', builddir='webkit-mac-latest-dbg')
F('f_webkit_mac_dbg', m_annotator.BaseFactory(
    'chromium', triggers=['s5_webkit_dbg_trigger']))

#
# Mac Dbg WebKit testers
#

B('WebKit Mac10.7 (dbg)', 'f_webkit_dbg_tests',
    scheduler='s5_webkit_dbg_trigger')
F('f_webkit_dbg_tests', m_annotator.BaseFactory('chromium'))

B('WebKit Mac non-Oilpan (dbg)', 'f_webkit_mac_oilpan_dbg',
    scheduler='global_scheduler', category='oilpan')
F('f_webkit_mac_oilpan_dbg', m_annotator.BaseFactory('chromium'))


################################################################################
##
################################################################################

def Update(_config, _active_main, c):
  return helper.Update(c)
