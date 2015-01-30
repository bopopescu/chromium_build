#!/usr/bin/python
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Switch to the given Xcode version.

Usage:
  ./find_xcode.py -j /tmp/out.json -v 6.0.1

  Finds Xcode 6.0.1 and switches to it. Writes a summary to /tmp/out.json
  that includes the Xcode installations that were installed, the Xcode
  installations that matched the specified version, the Xcode version at
  the start of this script, and the Xcode version at the end of this script.

  e.g. {
    "installations": {
      "/Applications/Xcode5.app": "5.1.1 (5B1008)",
      "/Applications/Xcode6.app": "6.0 (6A313)",
      "/Applications/Xcode6.0.1.app": "6.0.1 (6A317)",
      "/Applications/Xcode6.1.app": "6.1 (6A1046a)",
    },
    "matches": {
      "/Applications/Xcode6.0.1.app": "6.0.1 (6A317)",
    },
    "previous version": {
      "path": "/Application/Xcode5.app",
      "version": "5.1.1",
      "build": "(5B1008)",
    },
    "current version": {
      "path": "/Applications/Xcode6.0.1.app",
      "version": "6.0.1",
      "build": "6A317",
    }
  }
"""

import argparse
import json
import os
import sys

import utils


def get_xcodebuild_path(xcode_app):
  """Returns the path to xcodebuild under the given Xcode app.

  Args:
    xcode_app: The name of an .app folder in /Applications.
      e.g. Xcode.app

  Returns:
    The absolute path to the xcodebuild binary under the given Xcode app.
  """
  return os.path.join(
    '/',
    'Applications',
    xcode_app,
    'Contents',
    'Developer',
    'usr',
    'bin',
    'xcodebuild',
  )


def get_xcode_version(xcodebuild):
  """Returns the Xcode version and build version.

  Args:
    xcodebuild: The absolute path to the xcodebuild binary.

  Returns:
    A tuple of (version string, build version string).
      e.g. ("6.0.1", "6A317")
  """
  # Sample output:
  # Xcode 6.0.1
  # Build version 6A317
  version_output = utils.call(xcodebuild, '-version').stdout

  return version_output[0].split(' ')[-1], version_output[1].split(' ')[-1]


def get_current_xcode_info():
  """Returns the current Xcode path, version, and build number.

  Returns:
    A dict with 'path', 'version', and 'build' keys.
      'path': The absolute path to the Xcode installation.
      'version': The Xcode version.
      'build': The Xcode build version.
  """
  version, build_version = get_xcode_version('xcodebuild')

  return {
    'path': utils.call('xcode-select', '--print-path').stdout[0],
    'version': version,
    'build': build_version,
  }


def main(args):
  """Finds and switches to the given Xcode version."""
  xcode_info = {
    'installations': {
    },
    'matches': {
    },
    'previous version': {
    },
    'current version': {
    }
  }

  xcode_info['previous version'] = get_current_xcode_info()

  switched = False

  for app in os.listdir(os.path.join('/', 'Applications')):
    if app.startswith('Xcode'):
      installation_path = os.path.join('/', 'Applications', app)
      xcodebuild = get_xcodebuild_path(app)

      if os.path.exists(xcodebuild):
        version, build_version = get_xcode_version(xcodebuild)

        xcode_info['installations'][installation_path] = "%s (%s)" % (
          version,
          build_version,
        )

        if version == args.version:
          xcode_info['matches'][installation_path] = "%s (%s)" % (
            version,
            build_version,
          )

          # If this is the first match, switch to it.
          if not switched:
            utils.call(
              'sudo',
              'xcode-select',
              '-switch',
              os.path.join('/', 'Applications', app),
            )

            switched = True

  xcode_info['current version'] = get_current_xcode_info()

  with open(args.json_file, 'w') as json_file:
    json.dump(xcode_info, json_file)

  return 0 if switched else 1


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '-j',
    '--json-file',
    help='Location to write a JSON summary.',
    metavar='file',
    required=True,
    type=str,
  )
  parser.add_argument(
    '-v',
    '--version',
    help='Xcode version to find and switch to.',
    metavar='ver',
    required=True,
    type=str,
  )

  sys.exit(main(parser.parse_args()))