# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from main import gitiles_poller


def Update(config, c):
  libyuv_repo_url = config.Main.git_server_url + '/libyuv/libyuv'
  poller = gitiles_poller.GitilesPoller(libyuv_repo_url)
  c['change_source'].append(poller)
