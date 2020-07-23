# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""ActiveMain definition."""

from config_bootstrap import Main

class ChromiumGPU(Main.Main1):
  project_name = 'Chromium GPU'
  main_port = 8051
  subordinate_port = 8151
  main_port_alt = 8251
  tree_closing_notification_recipients = [
    'chrome-gpu-build-failures@google.com']
  buildbot_url = 'http://build.chromium.org/p/chromium.gpu/'
