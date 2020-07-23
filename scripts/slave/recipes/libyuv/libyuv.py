# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Recipe for building and running tests for Libyuv stand-alone.
"""

from recipe_engine.types import freeze

DEPS = [
  'depot_tools/bot_update',
  'chromium',
  'depot_tools/gclient',
  'libyuv',
  'recipe_engine/path',
  'recipe_engine/platform',
  'recipe_engine/properties',
  'recipe_engine/step',
  'depot_tools/tryserver',
]

RECIPE_CONFIGS = freeze({
  'libyuv': {
    'chromium_config': 'libyuv',
    'gclient_config': 'libyuv',
  },
  'libyuv_clang': {
    'chromium_config': 'libyuv_clang',
    'gclient_config': 'libyuv',
  },
  'libyuv_android': {
    'chromium_config': 'libyuv_android',
    'gclient_config': 'libyuv_android',
  },
  'libyuv_android_clang': {
    'chromium_config': 'libyuv_android_clang',
    'gclient_config': 'libyuv_android',
  },
  'libyuv_ios': {
    'chromium_config': 'libyuv_ios',
    'gclient_config': 'libyuv_ios',
  },
})

BUILDERS = freeze({
  'client.libyuv': {
    'builders': {
      'Win32 Debug (VS2010)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2010'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'Win32 Release (VS2010)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2010'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'Win64 Debug (VS2010)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2010'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'Win64 Release (VS2010)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2010'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'Win32 Debug (VS2012)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2012'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'Win32 Release (VS2012)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2012'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'Win64 Debug (VS2012)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2012'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'Win64 Release (VS2012)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2012'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'Win32 Debug (VS2013)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2013'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'Win32 Release (VS2013)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2013'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'Win64 Debug (VS2013)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2013'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'Win64 Release (VS2013)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['msvs2013'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'Win32 Debug (Clang)': {
        'recipe_config': 'libyuv_clang',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'Win32 Release (Clang)': {
        'recipe_config': 'libyuv_clang',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'Win64 Debug (Clang)': {
        'recipe_config': 'libyuv_clang',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'Win64 Release (Clang)': {
        'recipe_config': 'libyuv_clang',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'Mac64 Debug': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'mac'},
      },
      'Mac64 Release': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'mac'},
      },
      'Mac Asan': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['asan'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'mac'},
      },
      'iOS Debug': {
        'recipe_config': 'libyuv_ios',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 32,
          'TARGET_ARCH': 'arm',
          'TARGET_PLATFORM': 'ios',
        },
        'testing': {'platform': 'mac'},
      },
      'iOS Release': {
        'recipe_config': 'libyuv_ios',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 32,
          'TARGET_ARCH': 'arm',
          'TARGET_PLATFORM': 'ios',
        },
        'testing': {'platform': 'mac'},
      },
      'iOS ARM64 Debug': {
        'recipe_config': 'libyuv_ios',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
          'TARGET_ARCH': 'arm',
          'TARGET_PLATFORM': 'ios',
        },
        'testing': {'platform': 'mac'},
      },
      'iOS ARM64 Release': {
        'recipe_config': 'libyuv_ios',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
          'TARGET_ARCH': 'arm',
          'TARGET_PLATFORM': 'ios',
        },
        'testing': {'platform': 'mac'},
      },
      'Linux32 Debug': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux32 Release': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux64 Debug': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux64 Release': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux64 Debug (GN)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['gn'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux64 Release (GN)': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['gn'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux Asan': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['asan', 'lsan'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux Memcheck': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['memcheck'],
        'gclient_apply_config': ['libyuv_valgrind'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux MSan': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['msan', 'msan_full_origin_tracking',
                                  'prebuilt_instrumented_libraries'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux Tsan v2': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['tsan2'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux UBSan': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['ubsan'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Linux UBSan vptr': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['ubsan_vptr'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Android Debug': {
        'recipe_config': 'libyuv_android',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'Android Release': {
        'recipe_config': 'libyuv_android',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'Android ARM64 Debug': {
        'recipe_config': 'libyuv_android',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'Android Clang Debug': {
        'recipe_config': 'libyuv_android_clang',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'Android GN': {
        'recipe_config': 'libyuv_android',
        'chromium_apply_config': ['gn'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'Android GN (dbg)': {
        'recipe_config': 'libyuv_android',
        'chromium_apply_config': ['gn'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
    },
  },
  'tryserver.libyuv': {
    'builders': {
      'win': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'win_rel': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'win_x64_rel': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'win_clang': {
        'recipe_config': 'libyuv_clang',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'win_clang_rel': {
        'recipe_config': 'libyuv_clang',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'win'},
      },
      'win_x64_clang_rel': {
        'recipe_config': 'libyuv_clang',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'win'},
      },
      'mac': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'mac'},
      },
      'mac_rel': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'mac'},
      },
      'mac_asan': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['asan'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'mac'},
      },
      'ios': {
        'recipe_config': 'libyuv_ios',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 32,
          'TARGET_ARCH': 'arm',
          'TARGET_PLATFORM': 'ios',
        },
        'testing': {'platform': 'mac'},
      },
      'ios_rel': {
        'recipe_config': 'libyuv_ios',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 32,
          'TARGET_ARCH': 'arm',
          'TARGET_PLATFORM': 'ios',
        },
        'testing': {'platform': 'mac'},
      },
      'ios_arm64': {
        'recipe_config': 'libyuv_ios',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
          'TARGET_ARCH': 'arm',
          'TARGET_PLATFORM': 'ios',
        },
        'testing': {'platform': 'mac'},
      },
      'ios_arm64_rel': {
        'recipe_config': 'libyuv_ios',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
          'TARGET_ARCH': 'arm',
          'TARGET_PLATFORM': 'ios',
        },
        'testing': {'platform': 'mac'},
      },
      'linux': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'linux_rel': {
        'recipe_config': 'libyuv',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'linux_gn': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['gn'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'linux_gn_rel': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['gn'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'linux_asan': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['asan', 'lsan'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'linux_memcheck': {
        'recipe_config': 'libyuv',
        'chromium_apply_config': ['memcheck'],
        'gclient_apply_config': ['libyuv_valgrind'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'linux_msan': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['msan', 'msan_full_origin_tracking',
                                  'prebuilt_instrumented_libraries'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'linux_tsan2': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['tsan2'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'linux_ubsan': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['ubsan'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'linux_ubsan_vptr': {
        'recipe_config': 'libyuv_clang',
        'chromium_apply_config': ['ubsan_vptr'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'android': {
        'recipe_config': 'libyuv_android',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'android_rel': {
        'recipe_config': 'libyuv_android',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'android_clang': {
        'recipe_config': 'libyuv_android_clang',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'android_arm64': {
        'recipe_config': 'libyuv_android',
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 64,
        },
        'testing': {'platform': 'linux'},
      },
      'android_gn': {
        'recipe_config': 'libyuv_android',
        'chromium_apply_config': ['gn'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
      'android_gn_rel': {
        'recipe_config': 'libyuv_android',
        'chromium_apply_config': ['gn'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
          'TARGET_BITS': 32,
        },
        'testing': {'platform': 'linux'},
      },
    },
  },
})

def RunSteps(api):
  mainname = api.properties.get('mainname')
  buildername = api.properties.get('buildername')
  main_dict = BUILDERS.get(mainname, {})
  bot_config = main_dict.get('builders', {}).get(buildername)
  assert bot_config, ('Unrecognized builder name "%r" for main "%r".' %
                      (buildername, mainname))
  recipe_config_name = bot_config['recipe_config']
  recipe_config = RECIPE_CONFIGS.get(recipe_config_name)
  assert recipe_config, ('Cannot find recipe_config "%s" for builder "%r".' %
                         (recipe_config_name, buildername))

  api.chromium.set_config(recipe_config['chromium_config'],
                          **bot_config.get('chromium_config_kwargs', {}))
  api.gclient.set_config(recipe_config['gclient_config'])
  for c in bot_config.get('gclient_apply_config', []):
    api.gclient.apply_config(c)
  for c in bot_config.get('chromium_apply_config', []):
    api.chromium.apply_config(c)

  if api.tryserver.is_tryserver:
    api.chromium.apply_config('trybot_flavor')

  api.bot_update.ensure_checkout(force=True)
  api.chromium.runhooks()

  if api.chromium.c.project_generator.tool == 'gn':
    api.chromium.run_gn(use_goma=True)
    api.chromium.compile(targets=['all'])
  else:
    api.chromium.compile()

  if api.chromium.c.TARGET_PLATFORM in ('win', 'mac', 'linux'):
    api.chromium.runtest('libyuv_unittest')


def _sanitize_nonalpha(text):
  return ''.join(c if c.isalnum() else '_' for c in text.lower())


def GenTests(api):
  def generate_builder(mainname, buildername, revision, suffix=None):
    suffix = suffix or ''
    bot_config = BUILDERS[mainname]['builders'][buildername]

    chromium_kwargs = bot_config.get('chromium_config_kwargs', {})
    test = (
      api.test('%s_%s%s' % (_sanitize_nonalpha(mainname),
                            _sanitize_nonalpha(buildername), suffix)) +
      api.properties(mainname=mainname,
                     buildername=buildername,
                     subordinatename='subordinatename',
                     BUILD_CONFIG=chromium_kwargs['BUILD_CONFIG']) +
      api.platform(bot_config['testing']['platform'],
                   chromium_kwargs.get('TARGET_BITS', 64))
    )

    if revision:
      test += api.properties(revision=revision)

    if mainname.startswith('tryserver'):
      test += api.properties(patch_url='try_job_svn_patch')
    return test

  for mainname, main_config in BUILDERS.iteritems():
    for buildername in main_config['builders'].keys():
      yield generate_builder(mainname, buildername, revision='12345')

  # Forced builds (not specifying any revision) and test failures.
  mainname = 'client.libyuv'
  yield generate_builder(mainname, 'Linux64 Debug', revision=None,
                         suffix='_forced')
  yield generate_builder(mainname, 'Android Debug', revision=None,
                         suffix='_forced')

  yield generate_builder('tryserver.libyuv', 'linux', revision=None,
                         suffix='_forced')
