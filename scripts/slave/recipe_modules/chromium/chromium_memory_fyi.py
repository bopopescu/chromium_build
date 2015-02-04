# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from . import steps

SPEC = {
  'settings': {
    'build_gs_bucket': 'chromium-memory-fyi-archive',
  },
  'builders': {
    'Chromium Linux MSan Builder': {
      'recipe_config': 'chromium_msan',
      'chromium_apply_config': ['instrumented_libraries'],
      'GYP_DEFINES': {
        'msan_track_origins': 2,
      },
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'testing': {'platform': 'linux'},
      'enable_swarming': True,
      'use_isolate': True,
    },
    'Linux MSan Tests': {
      'recipe_config': 'chromium_msan',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
      ],
      'parent_buildername': 'Chromium Linux MSan Builder',
      'testing': {'platform': 'linux'},
      'enable_swarming': True,
    },
    'Linux MSan Browser (1)': {
      'recipe_config': 'chromium_msan',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
      ],
      'parent_buildername': 'Chromium Linux MSan Builder',
      'testing': {
        'platform': 'linux',
      },
    },
    'Linux MSan Browser (2)': {
      'recipe_config': 'chromium_msan',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
      ],
      'parent_buildername': 'Chromium Linux MSan Builder',
      'testing': {
        'platform': 'linux',
      },
    },
    'Linux MSan Browser (3)': {
      'recipe_config': 'chromium_msan',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
      ],
      'parent_buildername': 'Chromium Linux MSan Builder',
      'testing': {
        'platform': 'linux',
      },
    },
    'Chromium Linux ChromeOS MSan Builder': {
      'recipe_config': 'chromium_msan',
      'chromium_apply_config': ['instrumented_libraries'],
      'GYP_DEFINES': {
        'msan_track_origins': 2,
        'chromeos': 1
      },
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'builder',
      'testing': {
        'platform': 'linux',
      },
    },
    'Linux ChromeOS MSan Tests': {
      'recipe_config': 'chromium_msan',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
      ],
      'parent_buildername': 'Chromium Linux ChromeOS MSan Builder',
      'testing': {
        'platform': 'linux',
      },
    },
    'Linux ChromeOS MSan Browser (1)': {
      'recipe_config': 'chromium_msan',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
      ],
      'parent_buildername': 'Chromium Linux ChromeOS MSan Builder',
      'testing': {
        'platform': 'linux',
      },
    },
    'Linux ChromeOS MSan Browser (2)': {
      'recipe_config': 'chromium_msan',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
      ],
      'parent_buildername': 'Chromium Linux ChromeOS MSan Builder',
      'testing': {
        'platform': 'linux',
      },
    },
    'Linux ChromeOS MSan Browser (3)': {
      'recipe_config': 'chromium_msan',
      'chromium_config_kwargs': {
        'BUILD_CONFIG': 'Release',
        'TARGET_BITS': 64,
      },
      'bot_type': 'tester',
      'test_generators': [
        steps.generate_gtest,
        steps.generate_script,
      ],
      'parent_buildername': 'Chromium Linux ChromeOS MSan Builder',
      'testing': {
        'platform': 'linux',
      },
    },
  },
}
