# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

DEPS = [
  'depot_tools/bot_update',
  'depot_tools/gclient',
  'recipe_engine/properties',
]


def RunSteps(api):
  api.gclient.set_config('luci_py')
  api.bot_update.ensure_checkout(force=True)
  # TODO(tandrii): trigger tests without PRESUBMIT.py .


def GenTests(api):
  yield (
    api.test('luci_py') +
    api.properties.git_scheduled(
        buildername='luci-py-linux64',
        buildnumber=123,
        mainname='chromium.infra',
        repository='https://chromium.googlesource.com/external/github.com/luci/luci-py',
    )
  )
