# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from buildbot.status.builder import FAILURE
from master import chromium_notifier
from master import master_utils


v8_steps = [
  'update',
  'runhooks',
  'gn',
  'compile',
  'Presubmit',
  'Static-Initializers',
  'Check',
  'Unittests',
  'OptimizeForSize',
  'Mjsunit',
  'Webkit',
  'Benchmarks',
  'Test262',
  'Mozilla',
  'GCMole',
  'Fuzz',
  'Deopt Fuzz',
  'Simple Leak Check',
  # TODO(machenbach): Enable mail notifications as soon as a try builder is
  # set up.
  # 'webkit_tests',
]

# This is the list of the builder categories and the corresponding critical
# steps. If one critical step fails, the blame list will be notified.
# Note: don't include 'update scripts' since we can't do much about it when
# it's failing and the tree is still technically fine.
categories_steps = {
  '': v8_steps,
}

exclusions = {
  'V8 Linux - mipsel - sim - builder': [],
  'V8 Linux - mips64el - sim - builder': [],
  'V8 Linux - mipsel - sim': [],
  'V8 Mips - builder': [],
  'V8 Mips - big endian - nosnap - 1': [],
  'V8 Mips - big endian - nosnap - 2': [],
  'V8 Linux - x87 - nosnap - debug': [],
  'V8 Linux - predictable': [],
  'V8 Linux64 - custom snapshot - debug': [],
  'Chrome Mac10.6 Perf': [],
  'Chrome Win7 Perf': [],
}

forgiving_steps = ['update_scripts', 'update', 'svnkill', 'taskkill',
                   'gclient_revert']

x87_categories_steps = {'x87': ['runhooks', 'compile', 'Check']}
vtunejit_categories_steps = {'vtunejit': ['runhooks', 'compile']}
mem_sheriff_categories_steps = {'mem_sheriff': v8_steps}
predictable_categories_steps = {'predictable': v8_steps}
custom_snapshot_categories_steps = {'custom_snapshot': v8_steps}

class V8Notifier(chromium_notifier.ChromiumNotifier):
  def isInterestingStep(self, build_status, step_status, results):
    """Watch only failing steps."""
    return results[0] == FAILURE


def Update(config, active_master, c):
  c['status'].append(V8Notifier(
      fromaddr=active_master.from_address,
      categories_steps=categories_steps,
      exclusions=exclusions,
      relayhost=config.Master.smtp,
      sendToInterestedUsers=True,
      status_header='buildbot failure in %(project)s on %(builder)s, %(steps)s',
      lookup=master_utils.FilterDomain(),
      forgiving_steps=forgiving_steps))
  c['status'].append(V8Notifier(
      fromaddr=active_master.from_address,
      categories_steps=x87_categories_steps,
      exclusions={},
      relayhost=config.Master.smtp,
      sendToInterestedUsers=False,
      extraRecipients=['weiliang.lin@intel.com', 'chunyang.dai@intel.com'],
      status_header='buildbot failure in %(project)s on %(builder)s, %(steps)s',
      lookup=master_utils.FilterDomain(),
      forgiving_steps=forgiving_steps))
  c['status'].append(V8Notifier(
      fromaddr=active_master.from_address,
      categories_steps=vtunejit_categories_steps,
      exclusions={},
      relayhost=config.Master.smtp,
      sendToInterestedUsers=False,
      extraRecipients=['chunyang.dai@intel.com'],
      status_header='buildbot failure in %(project)s on %(builder)s, %(steps)s',
      lookup=master_utils.FilterDomain(),
      forgiving_steps=forgiving_steps))
  c['status'].append(V8Notifier(
      fromaddr=active_master.from_address,
      categories_steps=mem_sheriff_categories_steps,
      exclusions={},
      relayhost=config.Master.smtp,
      sendToInterestedUsers=False,
      extraRecipients=['hpayer@chromium.org', 'ulan@chromium.org'],
      status_header='buildbot failure in %(project)s on %(builder)s, %(steps)s',
      lookup=master_utils.FilterDomain(),
      forgiving_steps=forgiving_steps))
  c['status'].append(V8Notifier(
      fromaddr=active_master.from_address,
      categories_steps=predictable_categories_steps,
      exclusions={},
      relayhost=config.Master.smtp,
      sendToInterestedUsers=False,
      extraRecipients=['ishell@chromium.org'],
      status_header='buildbot failure in %(project)s on %(builder)s, %(steps)s',
      lookup=master_utils.FilterDomain(),
      forgiving_steps=forgiving_steps))
  c['status'].append(V8Notifier(
      fromaddr=active_master.from_address,
      categories_steps=custom_snapshot_categories_steps,
      exclusions={},
      relayhost=config.Master.smtp,
      sendToInterestedUsers=False,
      extraRecipients=['yangguo@chromium.org'],
      status_header='buildbot failure in %(project)s on %(builder)s, %(steps)s',
      lookup=master_utils.FilterDomain(),
      forgiving_steps=forgiving_steps))
