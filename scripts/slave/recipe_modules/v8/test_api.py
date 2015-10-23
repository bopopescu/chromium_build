# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Exposes the builder and recipe configurations to GenTests in recipes.

import re

from recipe_engine import recipe_test_api
from . import builders

# Simulated branch names for testing. Optionally upgrade these in branch
# period to reflect the real branches used by the gitiles poller.
STABLE_BRANCH = '4.2'
BETA_BRANCH = '4.3'


def _sanitize_nonalpha(text):
  return ''.join(c if c.isalnum() else '_' for c in text)


class V8TestApi(recipe_test_api.RecipeTestApi):
  BUILDERS = builders.BUILDERS
  SLOWEST_TESTS = [
    {
      'name': 'mjsunit/Cool.Test',
      'flags': ['-f'],
      'command': 'd8 -f mjsunit/Cool.Test',
      'duration': 61.0028,
    },
    {
      'name': 'mjsunit/Cool.Test2',
      'flags': ['-f', '-g'],
      'command': 'd8 -f mjsunit/Cool.Test2',
      'duration': 0.1012,
    },
  ]

  def iter_builders(self):
    return builders.iter_builders()

  def output_json(self, has_failures=False, wrong_results=False, flakes=False):
    if not has_failures:
      return self.m.json.output([{
        'arch': 'theArch',
        'mode': 'theMode',
        'results': [],
        'slowest_tests': V8TestApi.SLOWEST_TESTS,
      }])
    if wrong_results:
      return self.m.json.output([{
        'arch': 'theArch1',
        'mode': 'theMode1',
        'results': [],
        'slowest_tests': V8TestApi.SLOWEST_TESTS,
      },
      {
        'arch': 'theArch2',
        'mode': 'theMode2',
        'results': [],
        'slowest_tests': V8TestApi.SLOWEST_TESTS,
      }])
    if flakes:
      return self.m.json.output([{
        'arch': 'theArch1',
        'mode': 'theMode1',
        'results': [
          {
            'flags': [],
            'result': 'FAIL',
            'expected': ['PASS', 'SLOW'],
            'duration': 3,
            'variant': 'default',
            'random_seed': 123,
            'run': 1,
            'stdout': 'Some output.',
            'stderr': 'Some errput.',
            'name': 'suite-name/dir/test-name',
            'command': 'd8 test.js',
            'exit_code': 1,
          },
          {
            'flags': [],
            'result': 'PASS',
            'expected': ['PASS', 'SLOW'],
            'duration': 10,
            'variant': 'default',
            'random_seed': 123,
            'run': 2,
            'stdout': 'Some output.',
            'stderr': '',
            'name': 'suite-name/dir/test-name',
            'command': 'd8 test.js',
            'exit_code': 1,
          },
          {
            'flags': [],
            'result': 'FAIL',
            'expected': ['PASS', 'SLOW'],
            'duration': 1.5,
            'variant': 'default',
            'random_seed': 123,
            'run': 1,
            'stdout': 'Some output.',
            'stderr': 'Some errput.',
            'name': 'suite-name/dir/test-name2',
            'command': 'd8 test.js',
            'exit_code': 1,
          },
          {
            'flags': [],
            'result': 'PASS',
            'expected': ['PASS', 'SLOW'],
            'duration': 10,
            'variant': 'default',
            'random_seed': 123,
            'run': 2,
            'stdout': 'Some output.',
            'stderr': '',
            'name': 'suite-name/dir/test-name2',
            'command': 'd8 test.js',
            'exit_code': 1,
          },
        ],
        'slowest_tests': V8TestApi.SLOWEST_TESTS,
      }])


    # Add enough failures to exceed the maximum number of shown failures
    # (test-name9 will be cut off).
    results = []
    for i in range(0, 10):
      results.append({
        'flags': ['--opt42'],
        'result': 'FAIL',
        'expected': ['PASS', 'SLOW'],
        'duration': 61.0028,
        'variant': 'default',
        'random_seed': 123,
        'run': 1,
        'stdout': 'Some output.',
        'stderr': 'Some errput.',
        'name': 'suite-name/dir/test-name%d' % i,
        'command': 'out/theMode/d8 --opt42 test/suite-name/dir/test-name.js',
        'exit_code': 1,
      })
      results.append({
        'flags': ['--other'],
        'result': 'FAIL',
        'duration': 3599.9999,
        'variant': 'default',
        'random_seed': 123,
        'run': 1,
        'stdout': 'Some output.',
        'stderr': 'Some errput.',
        'name': 'suite-name/dir/test-name%d' % i,
        'command': 'out/theMode/d8 --other test/suite-name/dir/test-name.js',
        'exit_code': 1,
      })
      results.append({
        'flags': ['--other'],
        'result': 'CRASH',
        'duration': 0.1111,
        'variant': 'default',
        'random_seed': 123,
        'run': 1,
        'stdout': 'Some output\nwith\nmore\nlines.',
        'stderr': 'Some errput.',
        'name': 'other-suite/dir/other-test-very-long-name%d' % i,
        'command': ('out/theMode/d8 --other '
                    'test/other-suite/dir/other-test-very-long-name.js'),
        'exit_code': 1,
      })

    return self.m.json.output([{
      'arch': 'theArch',
      'mode': 'theMode',
      'results': results,
      'slowest_tests': V8TestApi.SLOWEST_TESTS,
    }])

  def one_failure(self):
    return self.m.json.output([{
      'arch': 'theArch',
      'mode': 'theMode',
      'results': [
        {
          'flags': [],
          'result': 'FAIL',
          'expected': ['PASS', 'SLOW'],
          'duration': 5,
          'variant': 'default',
          'random_seed': 123,
          'run': 1,
          'stdout': 'Some output.',
          'stderr': 'Some errput.',
          'name': 'suite-name/dir/test-name',
          'command': 'd8 test.js',
          'target_name': 'd8',
          'exit_code': 1,
        },
      ],
      'slowest_tests': V8TestApi.SLOWEST_TESTS,
    }])

  def failures_example(self):
    return self.m.json.output([{
      'arch': 'theArch',
      'mode': 'theMode',
      'results': [
        {
          'flags': [],
          'result': 'FAIL',
          'expected': ['PASS', 'SLOW'],
          'duration': 3,
          'variant': 'default',
          'random_seed': 123,
          'run': 1,
          'stdout': 'Some output.',
          'stderr': 'Some errput.',
          'name': 'suite-name/dir/slow',
          'command': 'd8 test.js',
          'target_name': 'd8',
          'exit_code': 1,
        },
        {
          'flags': [],
          'result': 'FAIL',
          'expected': ['PASS', 'SLOW'],
          'duration': 1.5,
          'variant': 'default',
          'random_seed': 123,
          'run': 1,
          'stdout': 'Some output.',
          'stderr': 'Some errput.',
          'name': 'suite-name/dir/fast',
          'command': 'd8 test.js',
          'target_name': 'd8',
          'exit_code': 1,
        },
      ],
      'slowest_tests': V8TestApi.SLOWEST_TESTS,
    }])

  def perf_json(self, has_failures=False):
    result = {
      'errors': [],
      'traces':[
        {
          'units': 'score',
          'graphs': ['v8', 'Richards'],
          'results': ['30', '10', '20'],
        },
        {
          'units': 'ms',
          'graphs': ['v8', 'DeltaBlue'],
          'results': ['1.2', '1.2'],
        },
        {
          'units': 'score',
          'graphs': ['v8', 'Empty'],
          'results': [],
        },
      ],
    }
    if has_failures:
      result['errors'].extend(['Error line 1.', 'Error line 2.'])
    return self.m.json.output(result)

  def perf_improvement_json(self):
    result = {
      'errors': [],
      'traces':[
        {
          'units': 'score',
          'graphs': ['v8', 'Richards'],
          'results': ['50', '20', '30'],
        },
        {
          'units': 'ms',
          'graphs': ['v8', 'DeltaBlue'],
          'results': ['2.2', '2.2'],
        },
        {
          'units': 'score',
          'graphs': ['v8', 'Empty'],
          'results': [],
        },
      ],
    }
    return self.m.json.output(result)

  def example_buildbot_changes(self):
    return self.m.json.output({
      'changes': [
        {'revision': 'a1'},
        {'revision': 'a2'},
        {'revision': 'a3'},
      ]
    })

  def example_one_buildbot_change(self):
    return self.m.json.output({
      'changes': [
        {'revision': 'a1'},
      ]
    })

  def example_bisection_range(self):
    # Git returns changes in the order newest -> oldest.
    return self.m.raw_io.stream_output('a3\na2\na1', stream='stdout')

  def example_latest_previous_hash(self):
    return self.m.raw_io.stream_output('a0', stream='stdout')

  def example_available_builds(self, revision):
    # When 'gsutil ls' is called, it will only find builds for a1 or a3.
    available_builds = {
      'a1': 'gs://chromium-v8/v8-linux64-dbg/full-build-linux_a1.zip',
      'a3': 'gs://chromium-v8/v8-linux64-dbg/full-build-linux_a3.zip',
    }
    return self.m.raw_io.stream_output(
        available_builds.get(revision, ''),
        stream='stdout',
    )

  def _get_test_branch_name(self, mastername, buildername):
    if mastername == 'client.dart.fyi':
      return STABLE_BRANCH
    if re.search(r'stable branch', buildername):
      return STABLE_BRANCH
    if re.search(r'beta branch', buildername):
      return BETA_BRANCH
    return 'master'

  def test(self, mastername, buildername, suffix='', **kwargs):
    name = '_'.join(filter(bool, [
      'full',
      _sanitize_nonalpha(mastername),
      _sanitize_nonalpha(buildername),
      suffix,
    ]))
    builders_list = builders.BUILDERS[mastername]['builders']
    bot_config = builders_list[buildername]
    v8_config_kwargs = bot_config.get('v8_config_kwargs', {})
    parent_buildername = bot_config.get('parent_buildername')
    branch=self._get_test_branch_name(mastername, buildername)

    if bot_config.get('bot_type') in ['builder', 'builder_tester']:
      assert parent_buildername is None

    test = (
        recipe_test_api.RecipeTestApi.test(name) +
        self.m.properties.generic(
            mastername=mastername,
            buildername=buildername,
            branch=branch,
            parent_buildername=parent_buildername,
            revision='20123',
            **kwargs
        ) +
        self.m.platform(
            bot_config['testing']['platform'],
            v8_config_kwargs.get('TARGET_BITS', 64),
        )
    )
    if parent_buildername:
      test += self.m.properties(parent_got_revision='54321')

      # Add isolated-tests property from parent builder.
      parent = builders_list[parent_buildername]
      swarm_hashes = parent['testing'].get('swarm_hashes')
      if swarm_hashes:
        test += self.m.properties(swarm_hashes=swarm_hashes)

    if mastername.startswith('tryserver'):
      test += self.m.properties(
          revision='12345',
          patch_url='svn://svn-mirror.golo.chromium.org/patch',
      )

    return test

  def fail(self, step_name):
    return self.override_step_data(
        step_name, self.failures_example())

  def stdout(self, step_name, output, retcode=0):
    return self.override_step_data(
        step_name,
        self.m.raw_io.stream_output(output, stream='stdout'),
        retcode=retcode,
    )

  def stderr(self, step_name, output, retcode=0):
    return self.override_step_data(
        step_name,
        self.m.raw_io.stream_output(output, stream='stderr'),
        retcode=retcode,
    )

  @recipe_test_api.mod_test_data
  @staticmethod
  def test_failures(has_failures):
    return has_failures

  @recipe_test_api.mod_test_data
  @staticmethod
  def flakes(flakes):
    return flakes

  @recipe_test_api.mod_test_data
  @staticmethod
  def wrong_results(wrong_results):
    return wrong_results

  @recipe_test_api.mod_test_data
  @staticmethod
  def perf_failures(has_failures):
    return has_failures

  def __call__(self, test_failures=False, wrong_results=False,
               perf_failures=False, flakes=False):
    return (self.test_failures(test_failures) +
            self.wrong_results(wrong_results) +
            self.flakes(flakes) +
            self.perf_failures(perf_failures))
