# Copyright (c) 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Functions specific to handle goma related info.
"""

import datetime
import getpass
import glob
import gzip
import json
import os
import re
import shutil
import socket
import sys
import tempfile

from common import chromium_utils
from subordinate import subordinate_utils

# The Google Cloud Storage bucket to store logs related to goma.
GOMA_LOG_GS_BUCKET = 'chrome-goma-log'

# Platform dependent location of run command.
PLATFORM_RUN_CMD = {
    # os.name: run_cmd to use.
    'nt': 'C:\\infra-python\\run.py',
    'posix': '/opt/infra-python/run.py',
}


def GetShortHostname():
  """Get this machine's short hostname in lower case."""
  return socket.gethostname().split('.')[0].lower()


def GetGomaTmpDirectory():
  """Get goma's temp directory."""
  candidates = ['GOMA_TMP_DIR', 'TEST_TMPDIR', 'TMPDIR', 'TMP']
  for candidate in candidates:
    value = os.environ.get(candidate)
    if value and os.path.isdir(value):
      return value
  return '/tmp'


def GetLatestGomaCompilerProxyInfo():
  """Get a filename of the latest goma comiler_proxy.INFO."""
  dirname = GetGomaTmpDirectory()
  info_pattern = os.path.join(dirname, 'compiler_proxy.*.INFO.*')
  candidates = glob.glob(info_pattern)
  if not candidates:
    return None
  return sorted(candidates, reverse=True)[0]


def UploadToGomaLogGS(file_path, gs_filename, text_to_append=None):
  """Upload a file to Google Cloud Storage (gs://chrome-goma-log).

  Note that the uploaded file would automatically be gzip compressed.

  Args:
    file_path: a path of a file to be uploaded.
    gs_filename: a name of a file in Google Storage.
    text_to_append: an addtional text to be added to a file in GS.

  Returns:
    a stored path name without the bucket name in GS.
  """
  hostname = GetShortHostname()
  today = datetime.datetime.utcnow().date()
  log_path = '%s/%s/%s.gz' % (
    today.strftime('%Y/%m/%d'), hostname, gs_filename)
  gs_path = 'gs://%s/%s' % (GOMA_LOG_GS_BUCKET, log_path)
  temp = tempfile.NamedTemporaryFile(delete=False)
  try:
    with temp as f_out:
      with gzip.GzipFile(fileobj=f_out) as gzipf_out:
        with open(file_path) as f_in:
          shutil.copyfileobj(f_in, gzipf_out)
        if text_to_append:
          gzipf_out.write(text_to_append)
    subordinate_utils.GSUtilCopy(temp.name, gs_path)
    print "Copied log file to %s" % gs_path
  finally:
    os.remove(temp.name)
  return log_path


def UploadGomaCompilerProxyInfo():
  """Upload goma compiler_proxy.INFO to Google Storage."""
  latest_info = GetLatestGomaCompilerProxyInfo()
  if not latest_info:
    print 'No compiler_proxy.INFO to upload'
    return
  # Since a filename of compiler_proxy.INFO is fairly unique,
  # we might be able to upload it as-is.
  log_path = UploadToGomaLogGS(latest_info, os.path.basename(latest_info))
  viewer_url = ('http://chromium-build-stats.appspot.com/compiler_proxy_log/'
                + log_path)
  print 'Visualization at %s' % viewer_url


def UploadNinjaLog(outdir, compiler, command, exit_status):
  """Upload .ninja_log to Google Cloud Storage (gs://chrome-goma-log),
  in the same folder with goma's compiler_proxy.INFO.

  Args:
    outdir: a directory that contains .ninja_log.
    compiler: compiler used for the build.
    command: command line.
    exit_status: ninja's exit status.
  """
  ninja_log_path = os.path.join(outdir, '.ninja_log')
  try:
    st = os.stat(ninja_log_path)
    mtime = datetime.datetime.fromtimestamp(st.st_mtime)
  except OSError, e:
    print e
    return

  cwd = os.getcwd()
  platform = chromium_utils.PlatformName()

  info = {'cmdline': command,
          'cwd': cwd,
          'platform': platform,
          'exit': exit_status,
          'argv': sys.argv,
          'env': {}}
  for k, v in os.environ.iteritems():
    info['env'][k] = v
  if compiler:
    info['compiler'] = compiler
  compiler_proxy_info = GetLatestGomaCompilerProxyInfo()
  if compiler_proxy_info:
    info['compiler_proxy_info'] = compiler_proxy_info

  username = getpass.getuser()
  hostname = GetShortHostname()
  pid = os.getpid()
  ninja_log_filename = 'ninja_log.%s.%s.%s.%d' % (
      hostname, username, mtime.strftime('%Y%m%d-%H%M%S'), pid)
  additional_text = '# end of ninja log\n' + json.dumps(info)
  log_path = UploadToGomaLogGS(
    ninja_log_path, ninja_log_filename, additional_text)
  viewer_url = 'http://chromium-build-stats.appspot.com/ninja_log/' + log_path
  print 'Visualization at %s' % viewer_url


def IsCompilerProxyKilledByFatalError():
  """Returns true if goma compiler_proxy is killed by CHECK or LOG(FATAL)."""
  info_file = GetLatestGomaCompilerProxyInfo()
  if not info_file:
    return False
  fatal_pattern = re.compile(r'^F\d{4} \d{2}:\d{2}:\d{2}\.\d{6} ')
  with open(info_file) as f:
    for line in f.readlines():
      if fatal_pattern.match(line):
        return True
  return False


def SendGomaStats(goma_stats_file, goma_crash_report, build_data_dir):
  """Send GomaStats monitoring event.

  Note: this function also removes goma_stats_file.
  """
  try:
    goma_options = []
    if goma_stats_file and os.path.exists(goma_stats_file):
      # send GomaStats.
      goma_options = [
          '--build-event-goma-stats-path',
          goma_stats_file,
      ]
    elif goma_crash_report and os.path.exists(goma_crash_report):
      # crash report.
      goma_options = [
          '--build-event-goma-error',
          'GOMA_ERROR_CRASHED',
          '--build-event-goma-crash-report-id-path',
          goma_crash_report,
      ]
    elif IsCompilerProxyKilledByFatalError():
      goma_options = [
          '--build-event-goma-error',
          'GOMA_ERROR_LOG_FATAL',
      ]
    else:
      # unknown error.
      goma_options = [
          '--build-event-goma-error',
          'GOMA_ERROR_UNKNOWN',
      ]
    run_cmd = PLATFORM_RUN_CMD.get(os.name)
    if not run_cmd:
      print 'Unknown os.name: %s' % os.name
      return
    send_monitoring_event_cmd = [
        sys.executable,
        run_cmd,
        'infra.tools.send_monitoring_event',
        '--event-mon-run-type', 'prod',
        '--build-event-type', 'BUILD',
        '--event-mon-timestamp-kind', 'POINT',
        '--event-logrequest-path',
        os.path.join(build_data_dir, 'log_request_proto')
    ] + goma_options
    cmd_filter = chromium_utils.FilterCapture()
    retcode = chromium_utils.RunCommand(
      send_monitoring_event_cmd,
      filter_obj=cmd_filter,
      max_time=30)
    if retcode:
      print('Execution of send_monitoring_event failed with code %s'
            % retcode)
      print '\n'.join(cmd_filter.text)
  except Exception, inst:  # safety net
    print('send_monitoring_event for goma failed: %s' % inst)
  finally:
    try:
      os.remove(goma_stats_file)
    except OSError:  # file does not exist, for ex.
      pass
