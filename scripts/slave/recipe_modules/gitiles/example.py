# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

DEPS = [
  'gitiles',
  'properties',
]


def GenSteps(api):
  url = 'https://chromium.googlesource.com/chromium/src'
  for ref in api.gitiles.refs(url):
    api.gitiles.log(url, ref)
  api.gitiles.commit_log(url, api.properties['commit_log_hash'])
  api.gitiles.download_file(url, 'OWNERS')


def GenTests(api):
  yield (
    api.test('basic')
    + api.properties(
      commit_log_hash=api.gitiles.make_hash('commit'),
    )
    + api.step_data('refs', api.gitiles.make_refs_test_data(
      'HEAD',
      'refs/heads/A',
      'refs/tags/B',
    ))
    + api.step_data(
      'log: HEAD',
      api.gitiles.make_log_test_data('HEAD'),
    )
    + api.step_data(
      'log: refs/heads/A',
      api.gitiles.make_log_test_data('A'),
    )
    + api.step_data(
      'log: refs/tags/B',
      api.gitiles.make_log_test_data('B')
    )
    + api.step_data(
      'commit log: %s' % (api.gitiles.make_hash('commit')),
      api.gitiles.make_commit_test_data('commit', 'C')
    )
    + api.step_data(
      'Gitiles fetch OWNERS',
      api.gitiles.make_encoded_file('foobar')
    )
  )
