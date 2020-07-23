# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""ActiveMain definition."""

from config_bootstrap import Main

class ChromiumOS(Main.ChromiumOSBase):
  project_name = 'ChromiumOS'
  main_port = 8082
  subordinate_port = 8182
  main_port_alt = 8282
  buildbot_url = 'http://build.chromium.org/p/chromiumos/'
