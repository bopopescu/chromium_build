# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# This file was generated from
# scripts/tools/buildbot_tool_templates/master_site_config.py
# by "../../build/scripts/tools/buildbot-tool gen .".
# DO NOT EDIT BY HAND!


"""ActiveMaster definition."""

from config_bootstrap import Master

class ChromiumGoma(Master.Master1):
  project_name = 'ChromiumGoma'
  master_port = 20104
  slave_port = 30104
  master_port_alt = 25104
  buildbot_url = 'https://build.chromium.org/p/chromium.goma/'
  buildbucket_bucket = None
  service_account_file = None
