#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

""" Creates a zip file of a build and upload it to google storage.

This will be used by the ASAN/TSAN security tests uploaded to ClusterFuzz.

To archive files on Google Storage, set the 'gs_bucket' key in the
--factory-properties to 'gs://<bucket-name>'. To control access to archives,
set the 'gs_acl' key to the desired canned-acl (e.g. 'public-read', see
https://developers.google.com/storage/docs/accesscontrol#extension for other
supported canned-acl values). If no 'gs_acl' key is set, the bucket's default
object ACL will be applied (see
https://developers.google.com/storage/docs/accesscontrol#defaultobjects).

"""

import optparse
import os
import re
import stat
import sys

from common import chromium_utils
from common.chromium_utils import GS_COMMIT_POSITION_NUMBER_KEY, \
                                  GS_COMMIT_POSITION_KEY, \
                                  GS_GIT_COMMIT_KEY
from subordinate import build_directory
from subordinate import subordinate_utils

class StagingError(Exception):
  pass


def ShouldPackageFile(filename, target):
  # Disable 'unused argument' warning for 'target' | pylint: disable=W0613
  """Returns true if the file should be a part of the resulting archive."""
  if chromium_utils.IsMac():
    file_filter = r'^.+\.(a)$'
  elif chromium_utils.IsLinux():
    file_filter = r'^.+\.(o|a|d)$'
  elif chromium_utils.IsWindows():
    file_filter = r'^.+\.(obj|lib|pch|exp)$'
  else:
    raise NotImplementedError('%s is not supported.' % sys.platform)
  if re.match(file_filter, filename):
    return False

  # Skip files that we don't care about. Mostly directories.
  things_to_skip = chromium_utils.FileExclusions()

  if filename in things_to_skip:
    return False

  return True


def GetBuildSortKey(options, primary_project):
  """Returns: (str) the build sort key for the specified project.

  Attempts to identify the build sort key for a given project. If
  'primary_project' is None or if there is no sort key for the specified
  primary project, the checkout-wide sort key will be used.

  Raises:
    chromium_utils.NoIdentifiedRevision: if the checkout-wide sort key could not
        be resolved.
  """
  if primary_project:
    try:
      return chromium_utils.GetBuildSortKey(options, project=primary_project)
    except chromium_utils.NoIdentifiedRevision:
      pass
  return chromium_utils.GetBuildSortKey(options)


def GetGitCommit(options, primary_project):
  """Returns: (str/None) the git commit hash for a given project.

  Attempts to identify the git commit hash for a given project. If
  'primary_project' is None, or if there is no git commit hash for the specified
  primary project, the checkout-wide commit hash will be used.

  If none of the candidate configurations are present, 'None' will be returned.
  """
  projects = []
  if primary_project:
    projects += [primary_project]
  projects += [None]

  for project in projects:
    try:
      return chromium_utils.GetGitCommit(options, project=project)
    except chromium_utils.NoIdentifiedRevision:
      pass
  return None


def archive(options, args):
  # Disable 'unused argument' warning for 'args' | pylint: disable=W0613
  build_dir = build_directory.GetBuildOutputDirectory()
  src_dir = os.path.abspath(os.path.dirname(build_dir))
  build_dir = os.path.join(build_dir, options.target)

  revision_dir = (options.revision_dir or
                  options.factory_properties.get('revision_dir'))
  primary_project = chromium_utils.GetPrimaryProject(options)

  build_sortkey_branch, build_sortkey_value = GetBuildSortKey(
      options,
      primary_project)
  build_git_commit = GetGitCommit(options, primary_project)

  staging_dir = subordinate_utils.GetStagingDir(src_dir)
  chromium_utils.MakeParentDirectoriesWorldReadable(staging_dir)

  print 'Full Staging in %s' % staging_dir
  print 'Build Directory %s' % build_dir

  # Build the list of files to archive.
  zip_file_list = [f for f in os.listdir(build_dir)
                   if ShouldPackageFile(f, options.target)]

  if options.cf_archive_subdir_suffix is None:
    subdir_suffix = options.factory_properties.get(
        'cf_archive_subdir_suffix', '')
  else:
    subdir_suffix = options.cf_archive_subdir_suffix

  pieces = [chromium_utils.PlatformName(), options.target.lower()]
  if subdir_suffix:
    pieces.append(subdir_suffix)
  subdir = '-'.join(pieces)

  # Components like v8 get a <name>-v8-component-<revision> infix.
  component = ''
  if revision_dir:
    component = '-%s-component' % revision_dir

  prefix = (options.cf_archive_name or
            options.factory_properties.get('cf_archive_name', 'cf_archive'))
  sortkey_path = chromium_utils.GetSortableUploadPathForSortKey(
      build_sortkey_branch, build_sortkey_value)
  zip_file_name = '%s-%s-%s%s-%s' % (prefix,
                                     chromium_utils.PlatformName(),
                                     options.target.lower(),
                                     component,
                                     sortkey_path)

  (zip_dir, zip_file) = chromium_utils.MakeZip(staging_dir,
                                               zip_file_name,
                                               zip_file_list,
                                               build_dir,
                                               raise_error=True)
  chromium_utils.RemoveDirectory(zip_dir)
  if not os.path.exists(zip_file):
    raise StagingError('Failed to make zip package %s' % zip_file)
  chromium_utils.MakeWorldReadable(zip_file)

  # Report the size of the zip file to help catch when it gets too big.
  zip_size = os.stat(zip_file)[stat.ST_SIZE]
  print 'Zip file is %ld bytes' % zip_size

  gs_bucket = (options.gs_bucket or
               options.factory_properties.get('gs_bucket', None))
  gs_acl = options.gs_acl or options.factory_properties.get('gs_acl', None)

  gs_metadata = {
      GS_COMMIT_POSITION_NUMBER_KEY: build_sortkey_value,
  }
  if build_sortkey_branch:
    gs_metadata[GS_COMMIT_POSITION_KEY] = chromium_utils.BuildCommitPosition(
        build_sortkey_branch, build_sortkey_value)
  if build_git_commit:
    gs_metadata[GS_GIT_COMMIT_KEY] = build_git_commit

  status = subordinate_utils.GSUtilCopyFile(zip_file, gs_bucket, subdir=subdir,
                                      gs_acl=gs_acl, metadata=gs_metadata)
  if status:
    raise StagingError('Failed to upload %s to %s. Error %d' % (zip_file,
                                                                gs_bucket,
                                                                status))
  else:
    # Delete the file, it is not needed anymore.
    os.remove(zip_file)

  return status


def main(argv):
  option_parser = optparse.OptionParser()
  option_parser.add_option('--target', default='Release',
                           help='build target to archive (Debug or Release)')
  option_parser.add_option('--build-dir', help='ignored')
  option_parser.add_option('--cf_archive_name',
                           help='prefix of the archive zip file')
  option_parser.add_option('--cf_archive_subdir_suffix',
                           help='suffix of the archive directory')
  option_parser.add_option('--gs_acl', help='ACLs to be used on upload')
  option_parser.add_option('--gs_bucket',
                           help='the google storage bucket name')
  option_parser.add_option('--revision_dir',
                           help=('component builds: if set, use directory '
                                 'revision instead of chromium revision and '
                                 'add "-component" to the archive name'))

  chromium_utils.AddPropertiesOptions(option_parser)

  options, args = option_parser.parse_args(argv)
  return archive(options, args)

if '__main__' == __name__:
  sys.exit(main(sys.argv))
