# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from buildbot.schedulers.basic import SingleBranchScheduler

from master.factory import annotator_factory

m_annotator = annotator_factory.AnnotatorFactory()

def Update(c):
  c['schedulers'].extend([
      SingleBranchScheduler(name='webrtc_linux_scheduler',
                            branch='master',
                            treeStableTimer=30,
                            builderNames=[
          'Linux32 Debug',
          'Linux32 Release',
          'Linux64 Debug',
          'Linux64 Release',
          'Linux Asan',
          'Linux Memcheck',
          'Linux MSan',
          'Linux Tsan v2',
          'Linux UBSan vptr',
          'Linux64 Release [large tests]',
          'Linux64 Debug (GN)',
          'Linux64 Release (GN)',
          'Linux64 Release (Libfuzzer)',
      ]),
  ])

  # 'slavebuilddir' below is used to reduce the number of checkouts since some
  # of the builders are pooled over multiple slave machines.
  specs = [
    {'name': 'Linux32 Debug', 'slavebuilddir': 'linux32'},
    {'name': 'Linux32 Release', 'slavebuilddir': 'linux32'},
    {'name': 'Linux64 Debug', 'slavebuilddir': 'linux64'},
    {'name': 'Linux64 Release', 'slavebuilddir': 'linux64'},
    {'name': 'Linux Asan', 'slavebuilddir': 'linux_asan'},
    {'name': 'Linux MSan', 'slavebuilddir': 'linux_msan'},
    {'name': 'Linux Memcheck', 'slavebuilddir': 'linux_memcheck_tsan'},
    {'name': 'Linux Tsan v2', 'slavebuilddir': 'linux_tsan2'},
    {'name': 'Linux UBSan vptr', 'slavebuilddir': 'linux_ubsan_vptr'},
    {
      'name': 'Linux64 Release [large tests]',
      'category': 'compile|baremetal',
      'slavebuilddir': 'linux_baremetal',
    },
    {'name': 'Linux64 Debug (GN)', 'slavebuilddir': 'linux64_gn'},
    {'name': 'Linux64 Release (GN)', 'slavebuilddir': 'linux64_gn'},
    {
      'name': 'Linux64 Release (Libfuzzer)',
      'recipe': 'webrtc/libfuzzer',
      'slavebuilddir': 'linux64_libfuzzer',
    },
  ]

  c['builders'].extend([
      {
        'name': spec['name'],
        'factory': m_annotator.BaseFactory(spec.get('recipe',
                                                    'webrtc/standalone')),
        'notify_on_missing': True,
        'category': spec.get('category', 'compile|testers'),
        'slavebuilddir': spec['slavebuilddir'],
      } for spec in specs
  ])
