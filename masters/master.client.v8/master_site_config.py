# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""ActiveMain definition."""

from config_bootstrap import Main

class V8(Main.Main3):
  base_app_url = 'https://v8-status.appspot.com'
  tree_status_url = base_app_url + '/status'
  store_revisions_url = base_app_url + '/revisions'
  last_good_url = base_app_url + '/lkgr'
  project_name = 'V8'
  main_port = 8036
  subordinate_port = 8136
  main_port_alt = 8236
  project_url = 'http://v8.googlecode.com'
  buildbot_url = 'http://build.chromium.org/p/client.v8/'
  service_account_file = 'service-account-v8.json'