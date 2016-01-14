# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import ast
import copy

from recipe_engine.types import freeze


MB_CONFIG_FILENAME = ['tools', 'mb', 'mb_config.pyl']


class BotConfig(object):
  """Wrapper that allows combining several compatible bot configs."""

  def __init__(self, bots_dict, bot_ids):
    self._bots_dict = bots_dict

    assert len(bot_ids) >= 1
    self._bot_ids = bot_ids

  def _consistent_get(self, getter, name, default=None):
    result = getter(self._bot_ids[0], name, default)
    for bot_id in self._bot_ids:
      other_result = getter(bot_id, name, default)
      assert result == other_result, (
          'Inconsistent value for %r: bot %r has %r, '
          'but bot %r has %r' % (
              name, self._bot_ids[0], result, bot_id, other_result))
    return result

  def _get_bot_config(self, bot_id):
    # WARNING: This doesn't take into account dynamic
    # tests from test spec etc. If you need that, please use bot_db.
    return self._bots_dict.get(bot_id['mastername'], {}).get(
        'builders', {}).get(bot_id['buildername'], {})

  def _get(self, bot_id, name, default=None):
    return self._get_bot_config(bot_id).get(name, default)

  def get(self, name, default=None):
    return self._consistent_get(self._get, name, default)

  def _get_master_setting(self, bot_id, name, default=None):
    return self._bots_dict.get(bot_id['mastername'], {}).get(
        'settings', {}).get(name, default)

  def get_master_setting(self, name, default=None):
    return self._consistent_get(self._get_master_setting, name, default)

  def _get_test_spec(self, chromium_tests_api):
    # TODO(phajdan.jr): Make test specs work for more than 1 bot.
    assert len(self._bot_ids) == 1

    bot_config = self._get_bot_config(self._bot_ids[0])
    mastername = self._bot_ids[0]['mastername']
    buildername = self._bot_ids[0]['buildername']

    # The official builders specify the test spec using a test_spec property in
    # the bot_config instead of reading it from a file.
    if 'test_spec' in bot_config:
      return { buildername: bot_config['test_spec'] }

    test_spec_file = bot_config.get('testing', {}).get(
        'test_spec_file', '%s.json' % mastername)

    # TODO(phajdan.jr): Bots should have no generators instead.
    if bot_config.get('disable_tests'):
      return {}
    return chromium_tests_api.read_test_spec(chromium_tests_api.m, test_spec_file)

  def initialize_bot_db(self, chromium_tests_api, bot_db):
    # TODO(phajdan.jr): Make this work for more than 1 bot.
    assert len(self._bot_ids) == 1

    bot_config = self._get_bot_config(self._bot_ids[0])
    mastername = self._bot_ids[0]['mastername']
    buildername = self._bot_ids[0]['buildername']

    test_spec = self._get_test_spec(chromium_tests_api)

    # TODO(phajdan.jr): Bots should have no generators instead.
    if bot_config.get('disable_tests'):
      scripts_compile_targets = {}
    else:
      scripts_compile_targets = \
          chromium_tests_api.get_compile_targets_for_scripts().json.output

    # We manually thaw the path to the elements we are modifying, since the
    # builders are frozen.
    master_dict = dict(self._bots_dict[mastername])
    builders = master_dict['builders'] = dict(master_dict['builders'])
    bot_config = builders[buildername]
    for loop_buildername in builders:
      builder_dict = builders[loop_buildername] = (
          dict(builders[loop_buildername]))
      builders[loop_buildername]['tests'] = (
          chromium_tests_api.generate_tests_from_test_spec(
              chromium_tests_api.m, test_spec, builder_dict,
              loop_buildername, mastername,
              # TODO(phajdan.jr): Get enable_swarming value from builder_dict.
              # Above should remove the need to get bot_config and buildername
              # in this method.
              bot_config.get('enable_swarming', False),
              scripts_compile_targets, builder_dict.get('test_generators', [])
          ))

    bot_db._add_master_dict_and_test_spec(
        mastername, freeze(master_dict), freeze(test_spec))

  def should_force_legacy_compiling(self, chromium_tests_api):
    """Determines if a given chromium revision needs to be built with gyp.

    This is done by checking the contents of tools/mb/mb_config.pyl at the rev.

    Returns:
      True if the revision occurred before the changeover from GYP to MP.
    """
    try:
      config_pyl = chromium_tests_api.m.file.read(
          'Reading MB config',
          chromium_tests_api.m.path['checkout'].join(*MB_CONFIG_FILENAME),
          test_data=('{\'masters\': {'
                     '\'tryserver.chromium.perf\': {'
                     '\'linux_perf_bisect_builder\':'
                     '\'gyp_something_something\'}}}'))
      config = ast.literal_eval(config_pyl or '{}')
      for bot_id in self._bot_ids:
        _ = config['masters'][bot_id['mastername']][bot_id['buildername']]
      result_text = 'MB is enabled for this builder at this revision.'
      log_name = 'Builder MB-ready'
      p = chromium_tests_api.m.step.active_result.presentation
      p.logs[log_name] = [result_text]
      return False
    except (chromium_tests_api.m.step.StepFailure, KeyError):
      result_text = 'MB is not enabled for this builder at this revision.'
      log_name = 'Builder NOT MB-ready'
      p = chromium_tests_api.m.step.active_result.presentation
      p.logs[log_name] = [result_text]
      p.status = chromium_tests_api.m.step.WARNING
      return True

  def get_compile_targets_and_tests(
      self, chromium_tests_api, bot_db, override_bot_type=None,
      override_tests=None):
    bot_type = override_bot_type or self.get('bot_type', 'builder_tester')
    if bot_type not in ['builder', 'builder_tester']:
      return [], []

    if override_tests:
      tests = override_tests
    else:
      tests = []
      for bot_id in self._bot_ids:
        bot_config = bot_db.get_bot_config(
            bot_id['mastername'], bot_id['buildername'])
        tests.extend([copy.deepcopy(t) for t in bot_config.get('tests', [])])

    compile_targets = set()
    tests_including_triggered = list(tests)
    for bot_id in self._bot_ids:
      bot_config = bot_db.get_bot_config(
          bot_id['mastername'], bot_id['buildername'])
      compile_targets.update(set(bot_config.get('compile_targets', [])))
      compile_targets.update(bot_db.get_test_spec(
          bot_id['mastername'], bot_id['buildername']).get(
              'additional_compile_targets', []))

      for _, test_bot in bot_db.bot_configs_matching_parent_buildername(
          bot_id['mastername'], bot_id['buildername']):
        tests_including_triggered.extend(test_bot.get('tests', []))

    if self.get('add_tests_as_compile_targets', True):
      for t in tests_including_triggered:
        compile_targets.update(t.compile_targets(chromium_tests_api.m))

    return sorted(compile_targets), tests_including_triggered

  def matches_any_bot_id(self, fun):
    return any(fun(bot_id) for bot_id in self._bot_ids)


class BotConfigAndTestDB(object):
  """An immutable database of bot configurations and test specifications.
  Holds the data for potentially multiple waterfalls (masternames). Most
  queries against this database are made with (mastername, buildername)
  pairs.
  """

  def __init__(self):
    # Indexed by mastername. Each entry contains a master_dict and a
    # test_spec.
    self._db = {}

  def _add_master_dict_and_test_spec(self, mastername, master_dict, test_spec):
    """Only used during construction in chromium_tests.prepare_checkout. Do not
    call this externally.
    """
    # TODO(kbr): currently the master_dicts that are created by
    # get_master_dict_with_dynamic_tests are over-specialized to a
    # particular builder -- the "enable_swarming" flag paradoxically comes
    # from that builder, rather than from each individual builder and/or
    # the parent builder. This needs to be fixed so that there's exactly
    # one master_dict per waterfall.
    assert mastername not in self._db, (
        'Illegal attempt to add multiple master dictionaries for waterfall %s' %
        (mastername))
    self._db[mastername] = { 'master_dict': master_dict,
                             'test_spec': test_spec }

  def get_bot_config(self, mastername, buildername):
    return self._db[mastername]['master_dict'].get('builders', {}).get(
        buildername)

  def get_master_settings(self, mastername):
    return self._db[mastername]['master_dict'].get('settings', {})

  def bot_configs_matching_parent_buildername(
      self, mastername, parent_buildername):
    """A generator of all the (buildername, bot_config) tuples whose
    parent_buildername is the passed one on the given master.
    """
    for buildername, bot_config in self._db[mastername]['master_dict'].get(
        'builders', {}).iteritems():
      if bot_config.get('parent_buildername') == parent_buildername:
        yield buildername, bot_config

  def get_test_spec(self, mastername, buildername):
    return self._db[mastername]['test_spec'].get(buildername, {})