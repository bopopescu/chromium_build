# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from main import main_config
from main.factory import annotator_factory, chromeos_factory

from buildbot.schedulers.basic import SingleBranchScheduler as Scheduler

def Builder(factory_obj, dname, sname, flavor, board):
  cbb_name = '%s-tot-chromium-pfq-informational' % (board,)
  builder = {
      'name': '%s (%s)' % (dname, flavor),
      'builddir': '%s-tot-chromeos-%s' % (flavor, sname),
      'category': '2chromium',
      'factory': chromeos_factory.ChromiteRecipeFactory(
          factory_obj, 'cros/cbuildbot'),
      'gatekeeper': 'pfq',
      'scheduler': 'chromium_cros',
      'notify_on_missing': True,
      'properties': {
          'cbb_config': cbb_name,
      },
  }
  return builder


def Update(_config, active_main, c):
  factory_obj = annotator_factory.AnnotatorFactory(
      active_main=active_main)

  builders = [
      Builder(factory_obj, 'X86', 'x86', 'chromium', 'x86-generic'),
      Builder(factory_obj, 'AMD64', 'amd64', 'chromium', 'amd64-generic'),
      Builder(factory_obj, 'Daisy', 'daisy', 'chromium', 'daisy'),
  ]

  c['schedulers'] += [
      Scheduler(name='chromium_cros',
                branch='main',
                treeStableTimer=60,
                builderNames=[b['name'] for b in builders],
      ),
  ]
  c['builders'] += builders
