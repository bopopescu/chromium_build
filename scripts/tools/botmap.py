#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Dumps a list of known subordinates, along with their OS and main."""

import os
import sys
path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(path)

from tools import list_subordinates


def main():
  list_subordinates.Main(['--botmap', '-x', 'all'])


if __name__ == '__main__':
  main()
