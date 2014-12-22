# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from . import steps


def _GetTargetName(platform, target_bits):
  return ('Release_x64' if platform is 'win' and target_bits is 64
            else 'Release')

def _Spec(platform, parent_builder, perf_id, index, num_shards, target_bits):
  return {
    'disable_tests': True,
    'bot_type': 'tester',
    'chromium_config_kwargs': {
      'BUILD_CONFIG': 'Release',
      'TARGET_BITS': target_bits,
    },
    'parent_buildername': parent_builder,
    'recipe_config': 'perf',
    'testing': {
      'platform': platform,
    },
    'tests': [
      steps.DynamicPerfTests(
          _GetTargetName(platform, target_bits).lower(),
          perf_id, index, num_shards),
    ],
  }


def _AddBotSpec(name, platform, parent_builder, perf_id, target_bits,
  num_shards):
  if num_shards > 1:
    for i in range(0, num_shards):
      builder_name = "%s (%d)" % (name, i + 1)
      SPEC['builders'][builder_name] = _Spec(platform, parent_builder, perf_id,
        i, num_shards, target_bits)
  else:
    SPEC['builders'][name] = _Spec(platform, parent_builder, perf_id,
        0, 1, target_bits)


SPEC = {
  'settings': {
    'build_gs_bucket': 'chrome-perf',
  },
  'builders': {
    'Linux Builder': {
      'disable_tests': True,
      'recipe_config': 'official',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'compile_targets': [
        'chromium_builder_perf',
      ],
      'testing': {
        'platform': 'linux',
      },
      'chromium_apply_config': ['chromium_perf']
    },
    'Win Builder': {
      'disable_tests': True,
      'recipe_config': 'official',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 32,
      },
      'bot_type': 'builder',
      'compile_targets': [
        'chromium_builder_perf',
      ],
      'testing': {
        'platform': 'win',
      },
      'chromium_apply_config': ['chromium_perf']
    },
    'Win x64 Builder': {
      'disable_tests': True,
      'recipe_config': 'official',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'compile_targets': [
        'chromium_builder_perf',
      ],
      'testing': {
        'platform': 'win',
      },
      'chromium_apply_config': ['chromium_perf']
    },
    'Mac Builder': {
      'disable_tests': True,
      'recipe_config': 'official',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'compile_targets': [
        'chromium_builder_perf',
      ],
      'testing': {
        'platform': 'mac',
      },
      'chromium_apply_config': ['chromium_perf']
    },
    'Android Builder': {
      'disable_tests': True,
      'recipe_config': 'official',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 32,
        'TARGET_ARCH': 'arm',
      },
      'bot_type': 'builder',
      'testing': {
        'platform': 'linux',
      },
      'chromium_apply_config': ['chromium_perf', 'android'],
      'gclient_apply_config': ['android', 'perf'],
    },
  }
}

_AddBotSpec(
    name='Linux Perf',
    platform='linux',
    parent_builder='Linux Builder',
    perf_id='linux-release',
    target_bits=64,
    num_shards=5)
_AddBotSpec(
    name='Win 8 Perf',
    platform='win',
    parent_builder='Win Builder',
    perf_id='chromium-rel-win8-dual',
    target_bits=32,
    num_shards=2)
_AddBotSpec(
    name='Win 7 Perf',
    platform='win',
    parent_builder='Win Builder',
    perf_id='chromium-rel-win7-dual',
    target_bits=32,
    num_shards=5)
_AddBotSpec(
    name='Win 7 x64 Perf',
    platform='win',
    parent_builder='Win x64 Builder',
    perf_id='chromium-rel-win7-x64-dual',
    target_bits=64,
    num_shards=2)
_AddBotSpec(
    name='Win 7 ATI GPU Perf',
    platform='win',
    parent_builder='Win Builder',
    perf_id='chromium-rel-win7-gpu-ati',
    target_bits=32,
    num_shards=1)
_AddBotSpec(
    name='Win 7 Intel GPU Perf',
    platform='win',
    parent_builder='Win Builder',
    perf_id='chromium-rel-win7-gpu-intel',
    target_bits=32,
    num_shards=1)
_AddBotSpec(
    name='Win 7 Nvidia GPU Perf',
    platform='win',
    parent_builder='Win Builder',
    perf_id='chromium-rel-win7-gpu-nvidia',
    target_bits=32,
    num_shards=1)
_AddBotSpec(
    name='Win 7 Low-End Perf',
    platform='win',
    parent_builder='Win Builder',
    perf_id='chromium-rel-win7-single',
    target_bits=32,
    num_shards=2)
_AddBotSpec(
    name='Win XP Perf',
    platform='win',
    parent_builder='Win Builder',
    perf_id='chromium-rel-xp-dual',
    target_bits=32,
    num_shards=5)
_AddBotSpec(
    name='Mac 10.9 Perf',
    platform='mac',
    parent_builder='Mac Builder',
    perf_id='chromium-rel-mac9',
    target_bits=64,
    num_shards=5)
_AddBotSpec(
    name='Mac 10.8 Perf',
    platform='mac',
    parent_builder='Mac Builder',
    perf_id='chromium-rel-mac8',
    target_bits=64,
    num_shards=5)

_AndroidSpecs = {
  'Android Nexus4 Perf': {
    'perf_id': 'android-nexus4',
    'num_device_shards': 8,
  },
  'Android Nexus5 Perf': {
    'perf_id': 'android-nexus5',
    'num_device_shards': 8,
  },
  'Android Nexus7v2 Perf': {
    'perf_id': 'android-nexus7v2',
    'num_device_shards': 8,
  },
  'Android Nexus10 Perf': {
    'perf_id': 'android-nexus10',
    'num_device_shards': 8,
  },
  'Android MotoE Perf': {
    'perf_id': 'android-motoe',
    'num_device_shards': 8,
  },
}
for k, v in _AndroidSpecs.iteritems():
  SPEC['builders'][k] = {
    'disable_tests': True,
    'bot_type': 'tester',
    'chromium_config_kwargs': {
      'BUILD_CONFIG': 'Release',
      'TARGET_BITS': 32,
      'TARGET_PLATFORM': 'android',
    },
    'gclient_config': 'perf',
    'gclient_apply_config': ['android'],
    'parent_buildername': 'Android Builder',
    'recipe_config': 'perf',
    'android_config': 'perf',
    'testing': {
      'platform': 'linux',
    },
    'tests': [
      steps.AndroidPerfTests(v['perf_id'], v['num_device_shards']),
    ],
  }
