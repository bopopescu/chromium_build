# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from recipe_engine.types import freeze

DEPS = [
  'depot_tools/bot_update',
  'chromium',
  'chromium_tests',
  'recipe_engine/json',
  'recipe_engine/path',
  'recipe_engine/platform',
  'recipe_engine/properties',
  'recipe_engine/python',
  'recipe_engine/step',
  'test_utils',
  'depot_tools/tryserver',
  'webrtc',
]


BUILDERS = freeze({
  'tryserver.v8': {
    'builders': {
      'v8_linux_chromium_gn_rel': {
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_PLATFORM': 'linux',
          'TARGET_BITS': 64,
        },
        'gclient_apply_config': [
          'v8_bleeding_edge_git',
          'chromium_lkcr',
          'show_v8_revision',
        ],
        'root_override': 'src/v8',
        'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      },
      'v8_android_chromium_gn_dbg': {
        'chromium_apply_config': ['gn_minimal_symbols'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
        },
        'gclient_apply_config': [
          'android',
          'v8_bleeding_edge_git',
          'chromium_lkcr',
          'show_v8_revision',
        ],
        'root_override': 'src/v8',
        'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      },
    },
  },
  'client.v8.fyi': {
    'builders': {
      'V8 Linux GN': {
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Release',
          'TARGET_PLATFORM': 'linux',
          'TARGET_BITS': 64,
        },
        'gclient_apply_config': [
          'v8_bleeding_edge_git',
          'chromium_lkcr',
          'show_v8_revision',
        ],
        'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      },
      'V8 Android GN (dbg)': {
        'chromium_apply_config': ['gn_minimal_symbols'],
        'chromium_config_kwargs': {
          'BUILD_CONFIG': 'Debug',
          'TARGET_PLATFORM': 'android',
          'TARGET_ARCH': 'arm',
        },
        'gclient_apply_config': [
          'android',
          'v8_bleeding_edge_git',
          'chromium_lkcr',
          'show_v8_revision',
        ],
        'set_component_rev': {'name': 'src/v8', 'rev_str': '%s'},
      },
    },
  },
})

def tests_in_compile_targets(api, compile_targets, tests):
  """Returns the tests in |tests| that have at least one of their compile
  targets in |compile_targets|."""
  result = []
  for test in tests:
    test_compile_targets = test.compile_targets(api)

    # Always return tests that don't require compile. Otherwise we'd never
    # run them.
    if ((set(compile_targets).intersection(set(test_compile_targets))) or
        not test_compile_targets):
      result.append(test)

  return result


def all_compile_targets(api, tests):
  """Returns the compile_targets for all the Tests in |tests|."""
  return sorted(set(x
                    for test in tests
                    for x in test.compile_targets(api)))


def _RunStepsInternal(api):
  mainname = api.properties.get('mainname')
  buildername = api.properties.get('buildername')
  bot_config = BUILDERS[mainname]['builders'][buildername]
  is_android = ('Android' in buildername or 'android' in buildername)
  force_clobber = bot_config.get('force_clobber', False)

  api.chromium.configure_bot(BUILDERS, ['mb'])
  bot_update_step = api.bot_update.ensure_checkout(
      force=True, patch_root=bot_config.get('root_override'))

  # because the 'mb' config is applied, we skip running gyp in the
  # the runhooks step.
  api.chromium.runhooks()

  # TODO(dpranke): Unify this with the logic in the chromium_trybot and
  # chromium recipes so that we can actually run the tests as well
  # and deapply patches and retry as need be.
  test_spec_file = '%s.json' % mainname
  test_spec = api.chromium_tests.read_test_spec(api, test_spec_file)

  tests = list(api.chromium_tests.steps.generate_gtest(
      api, api.chromium_tests, mainname, buildername, test_spec,
      bot_update_step))

  scripts_compile_targets = \
      api.chromium_tests.get_compile_targets_for_scripts().json.output
  tests += list(api.chromium_tests.steps.generate_script(
      api, api.chromium_tests, mainname, buildername, test_spec,
      bot_update_step, scripts_compile_targets=scripts_compile_targets))

  additional_compile_targets = test_spec.get(buildername, {}).get(
      'additional_compile_targets',
      ['chrome_public_apk' if is_android else 'all'])

  if api.tryserver.is_tryserver:
    affected_files = api.tryserver.get_files_affected_by_patch()

    test_targets = all_compile_targets(api, tests)

    test_targets, compile_targets = \
        api.chromium_tests.analyze(
            affected_files,
            test_targets,
            additional_compile_targets,
            'trybot_analyze_config.json')
    if compile_targets:
      api.chromium.run_mb(mainname, buildername, use_goma=True)
      api.chromium.compile(compile_targets,
                           force_clobber=force_clobber)
    tests = tests_in_compile_targets(api, test_targets, tests)
  else:
    api.chromium.run_mb(mainname, buildername, use_goma=True)
    api.chromium.compile(all_compile_targets(api, tests) +
                         additional_compile_targets,
                         force_clobber=force_clobber)

  if tests:
    bot_config_object = api.chromium_tests.create_bot_config_object(
        mainname, buildername)
    if api.tryserver.is_tryserver:
      api.chromium_tests.run_tests_on_tryserver(
          bot_config_object, api, tests, bot_update_step, affected_files)
    else:
      api.chromium_tests.configure_swarming('chromium', precommit=False,
                                            mainname=mainname)
      test_runner = api.chromium_tests.create_test_runner(api, tests)
      with api.chromium_tests.wrap_chromium_tests(bot_config_object, tests):
        test_runner()


def RunSteps(api):
  with api.tryserver.set_failure_hash():
    return _RunStepsInternal(api)


def GenTests(api):
  overrides = {}
  for mainname, main_dict in BUILDERS.items():
    for buildername in main_dict['builders']:

      # The Android bots are currently all only builders and cannot
      # run tests; more importantly, the recipe isn't set up to run
      # tests on Android correctly, and if we specify any tests in
      # the step_data, the recipe will crash :). We will eventually
      # fix this by killing this recipe altogether and moving to the
      # main chromium recipes.
      is_android = ('Android' in buildername or 'android' in buildername)
      gtest_tests = [] if is_android else ['base_unittests']

      overrides.setdefault(mainname, {})
      overrides[mainname][buildername] = (
          api.override_step_data(
              'read test spec',
              api.json.output({
                  buildername: {
                    'gtest_tests': gtest_tests,
                  },
              })))

      if 'tryserver' in mainname:
          overrides[mainname][buildername] += api.override_step_data(
            'analyze',
            api.json.output({
                'status': 'Found dependency',
                'test_targets': gtest_tests,
                'compile_targets': gtest_tests,
            }))

  for test in api.chromium.gen_tests_for_builders(BUILDERS, overrides):
    yield test

  yield (
    api.test('compile_failure') +
    api.platform.name('linux') +
    api.properties.tryserver(
        buildername='v8_linux_chromium_gn_rel',
        mainname='tryserver.v8') +
    api.step_data('compile', retcode=1) +
    overrides['tryserver.v8']['v8_linux_chromium_gn_rel']
  )

  yield (
    api.test('use_v8_patch_on_chromium_gn_trybot') +
    api.platform.name('linux') +
    api.properties.tryserver(
        buildername='v8_linux_chromium_gn_rel',
        mainname='tryserver.v8',
        patch_project='v8') +
    overrides['tryserver.v8']['v8_linux_chromium_gn_rel']
  )

  yield (
    api.test('no_tests_run') +
    api.platform.name('linux') +
    api.properties.tryserver(
        buildername='v8_linux_chromium_gn_rel',
        mainname='tryserver.v8') +
    api.override_step_data(
        'read test spec',
        api.json.output({'linux_chromium_gn_rel': {
           'additional_compile_targets': ['net_unittests'],
           'gtest_tests': ['base_unittests'],
        }})) +
    api.override_step_data(
        'analyze',
        api.json.output({
          'status': 'Found dependency',
          'test_targets': ['net_unittests'],
          'compile_targets': ['net_unittests'],
        }))
  )
