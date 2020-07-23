# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""An end-to-end test for recipe module `cipd`.

This actually installs cipd client and runs commands against it through cipd
recipe module. The test is end-to-end, which means that if cipd App Engine app
is down, this will fail.
"""

DEPS = [
  'depot_tools/bot_update',
  'cipd',
  'file',
  'depot_tools/gclient',
  'recipe_engine/json',
  'recipe_engine/path',
  'recipe_engine/platform',
  'recipe_engine/properties',
  'recipe_engine/python',
  'recipe_engine/raw_io',
  'recipe_engine/step',
  'depot_tools/tryserver'
]

# Credentials to register the cipd package.
REPO = 'https://chromium.googlesource.com/chrome/tools/build'
TEST_PACKAGE_PREFIX = 'infra/cipd_recipe_test'
# What directory will be packaged?
DIR_TO_PACKAGE = 'scripts/subordinate/recipe_modules/cipd'.split('/')


def RunSteps(api):
  if api.properties.get('dir_to_package'):
    inner(api)
  else:
    outer(api)


def outer(api):
  """Check out itself, maybe apply patch, and then run real itself."""
  api.gclient.set_config('build')
  step = api.bot_update.ensure_checkout(force=True, patch_root='build')

  properties = {}
  for attr in ['buildername', 'mainname', 'buildnumber', 'subordinatename']:
    properties[attr] = api.properties.get(attr)
  if api.tryserver.is_tryserver:
    assert not api.tryserver.is_gerrit_issue, 'Gerrit is not supported.'
    # TODO(tandrii): use property event.patchSet.ref for Gerrit case.
    # Assume Rietveld.
    properties['revision_tag'] = '%s/%s_%s' % (
        step.presentation.properties['got_revision'],
        api.properties['issue'], api.properties['patchset'])
  else:
    properties['revision_tag'] = step.presentation.properties['got_revision']
  properties['dir_to_package'] = str(api.path['checkout'].join(*DIR_TO_PACKAGE))

  # Recursive call to itself with extra property to ensure end of recursion.
  step = api.python(
      name='actual run',
      script=api.path['checkout'].join('scripts', 'tools', 'run_recipe.py'),
      args=[
        'infra/cipd_test',
        '--main-overrides-subordinate',
        '--properties-file',
        api.json.input(properties),
      ],
      allow_subannotations=True,
  )


def inner(api):
  """Actually performs the test in existing checkout."""
  api.cipd.install_client()
  assert api.cipd.get_executable()

  test_package = '%s/%s' % (TEST_PACKAGE_PREFIX, api.cipd.platform_suffix())
  test_package_file = api.path['subordinate_build'].join('test_package.cipd')
  step = api.cipd.build(api.properties['dir_to_package'],
                        test_package_file,
                        test_package, install_mode='copy')
  package_pin = step.json.output['result']
  instance_id = package_pin['instance_id']
  assert package_pin['package'] == test_package
  step.presentation.step_text = 'instance_id: %s' % package_pin['instance_id']

  # Path to a service account credentials to use to talk to CIPD backend.
  # Deployed by Puppet.
  if api.platform.is_win:
    creds = 'C:\\creds\\service_accounts\\service-account-cipd-builder.json'
  else:
    creds = '/creds/service_accounts/service-account-cipd-builder.json'
  api.cipd.set_service_account_credentials(creds)

  tags = {
    'revision': api.properties['revision_tag'],
    'git_repository': REPO,
    'buildbot_build': '%s/%s/%s' % (
        api.properties['mainname'],
        api.properties['buildername'],
        api.properties['buildnumber']
    ),
  }
  # Upload the test package.
  step = api.cipd.register(
      test_package, test_package_file,
      refs=['latest'],
      tags=tags,
  )
  assert step.json.output['result'] == package_pin
  # Set tags and refs.
  api.cipd.set_tag(test_package, instance_id, tags={'tag': 'cipd_test'})
  api.cipd.set_ref(test_package, instance_id, refs=['cipd_test'])

  step = api.cipd.search(test_package,
                         tag='revision:%s' % api.properties['revision_tag'])
  assert len(step.json.output['result']) == 1, 'there should be just 1 package'

  step = api.cipd.describe(
      test_package,
      version=step.json.output['result'][0]['instance_id'],
      test_data_refs=['latest'],
      test_data_tags=['%s:%s' % i for i in tags.iteritems()],
  )

  # Verify that tags are properly set. Note, there could be more tags!
  unset_tags = set('%s:%s' % i for i in tags.iteritems())
  for tag_info in step.json.output['result']['tags']:
    if tag_info['tag'] in unset_tags:
      unset_tags.remove(tag_info['tag'])
  assert not unset_tags

  # Install test package we've just uploaded by ref.
  cipd_root = api.path['subordinate_build'].join('cipd_test_package')
  api.cipd.ensure(cipd_root, {test_package: 'latest'})
  # Someone might have changed the latest ref in the meantime,
  # so install again by exact instance_id.
  step = api.cipd.ensure(cipd_root,
                         {test_package: package_pin['instance_id']})
  assert step.json.output['result'][0] == package_pin, (
      '\n%s\n!=\n%s\n' % (step.json.output['result'][0], package_pin))

  # Verify that we got same data back by building a new package from the
  # installation folder and compare hashes.
  # There is a .cipd folder there, so get rid of it first.
  # NOTE: this means we must have built package originally with
  # install_mode=copy.
  api.file.rmtree('.cipd package directory', cipd_root.join('.cipd'))
  step = api.cipd.build(cipd_root, test_package_file, test_package,
                        install_mode='copy')
  package_pin2 = step.json.output['result']
  assert package_pin2 == package_pin, (
      '\n%s\n!=\n%s\n' % (package_pin, package_pin2))


def GenTests(api):
  yield (
      api.test('cipd-latest-ok-inner') +
      api.properties.generic(
          mainname='chromium.infra',
          buildername='cipd-module-tester',
          revision_tag='deadbeaf',
          dir_to_package=(
            '[SLAVE_BUILD]/build/scripts/subordinate/recipe_modules/cipd'),
      )
  )
  yield (
      api.test('cipd-latest-ok-inner-win') +
      api.properties.generic(
          mainname='chromium.infra',
          buildername='cipd-module-tester',
          revision_tag='deadbeaf',
          dir_to_package=(
            '[SLAVE_BUILD]/build/scripts/subordinate/recipe_modules/cipd'),
      ) +
      api.platform.name('win')
  )
  yield (
      api.test('cipd-latest-ok-outer') +
      api.properties.generic(
          mainname='chromium.infra',
          buildername='cipd-module-tester',
      )
  )
  yield (
      api.test('cipd-latest-ok-outer-patch-rietveld') +
      api.properties.tryserver(
          mainname='chromium.infra',
          buildername='cipd-module-tester',
          patch_project='build',
      )
  )
