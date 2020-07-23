# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""ActiveMain definition."""

from config_bootstrap import Main

class ChromiumChromiumOS(Main.Main1):
  project_name = 'Chromium ChromiumOS'
  main_port = 8052
  subordinate_port = 8152
  main_port_alt = 8252
  alternate_tree_closing_notification_recipients = [
      'chromeos-build-failures@google.com']
  alternate_tree_status_url = 'https://chromiumos-status.appspot.com'
  buildbot_url = 'http://build.chromium.org/p/chromium.chromiumos/'
