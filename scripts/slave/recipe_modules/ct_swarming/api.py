# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


from recipe_engine import recipe_api



class CTSwarmingApi(recipe_api.RecipeApi):
  """Provides steps to run CT tasks on swarming bots."""

  CT_GS_BUCKET = 'cluster-telemetry'

  @property
  def downloads_dir(self):
    """Path to where artifacts should be downloaded from Google Storage."""
    return self.m.path['subordinate_build'].join('src', 'content', 'test', 'ct')

  @property
  def swarming_temp_dir(self):
    """Path where artifacts like isolate file and json output will be stored."""
    return self.m.path['subordinate_build'].join('swarming_temp_dir')

  @property
  def tasks_output_dir(self):
    """Directory where the outputs of the swarming tasks will be stored."""
    return self.swarming_temp_dir.join('outputs')

  def checkout_dependencies(self):
    """Checks out all repositories required for CT to run on swarming bots."""
    # Checkout chromium and swarming.
    self.m.chromium.set_config('chromium')
    self.m.gclient.set_config('chromium')
    self.m.bot_update.ensure_checkout(force=True)
    self.m.swarming_client.checkout()
    # Ensure swarming_client is compatible with what recipes expect.
    self.m.swarming.check_client_version()

  # TODO(rmistry): Remove once the Go binaries are moved to recipes or buildbot.
  def setup_go_isolate(self):
    """Generates and puts in place the isolate Go binary."""
    # Run 'gclient runhooks' on the chromium checkout to generate the binary.
    self.m.step('gclient runhooks', ['gclient', 'runhooks'],
                cwd=self.m.path['subordinate_build'].join('src'))
    # Copy binaries to the expected location.
    dest = self.m.path['subordinate_build'].join('luci-go')
    self.m.file.rmtree('Go binary dir', dest)
    self.m.file.copytree('Copy Go binary',
                         source=self.m.path['subordinate_build'].join(
                             'src', 'tools', 'luci-go'),
                         dest=dest)

  def download_CT_binary(self, ct_binary_name):
    """Downloads the specified CT binary from GS into the downloads_dir."""
    binary_dest = self.downloads_dir.join(ct_binary_name)
    self.m.gsutil.download(
        name="download %s" % ct_binary_name,
        bucket=self.CT_GS_BUCKET,
        source='swarming/binaries/%s' % ct_binary_name,
        dest=binary_dest)
    # Set executable bit on the binary.
    self.m.python.inline(
        name='Set executable bit on %s' % ct_binary_name,
        program='''
import os
import stat

os.chmod('%s', os.stat('%s').st_mode | stat.S_IEXEC)
''' % (str(binary_dest), str(binary_dest))
    )

  def download_page_artifacts(self, page_type, subordinate_num):
    """Downloads all the artifacts needed to run benchmarks on a page.

    The artifacts are downloaded into subdirectories in the downloads_dir.

    Args:
      page_type: str. The CT page type. Eg: 1k, 10k.
      subordinate_num: int. The number of the subordinate used to determine which GS
                 directory to download from. Eg: for the top 1k, subordinate1 will
                 contain webpages 1-10, subordinate2 will contain 11-20.
    """
    # Download page sets.
    page_sets_dir = self.downloads_dir.join('subordinate%s' % subordinate_num, 'page_sets')
    self.m.file.makedirs('page_sets dir', page_sets_dir)
    self.m.gsutil.download(
        bucket=self.CT_GS_BUCKET,
        source='swarming/page_sets/%s/subordinate%s/*' % (page_type, subordinate_num),
        dest=page_sets_dir)

    # Download archives.
    wpr_dir = page_sets_dir.join('data')
    self.m.file.makedirs('WPR dir', wpr_dir)
    self.m.gsutil.download(
        bucket=self.CT_GS_BUCKET,
        source='swarming/webpage_archives/%s/subordinate%s/*' % (page_type,
                                                           subordinate_num),
        dest=wpr_dir)

  def download_skps(self, page_type, subordinate_num, skps_chromium_build, dest_dir):
    """Downloads SKPs corresponding to the specified page type, subordinate and build.

    The SKPs are downloaded into subdirectories in the downloads_dir.

    Args:
      page_type: str. The CT page type. Eg: 1k, 10k.
      subordinate_num: int. The number of the subordinate used to determine which GS
                 directory to download from. Eg: for the top 1k, subordinate1 will
                 contain SKPs from webpages 1-10, subordinate2 will contain 11-20.
      skps_chromium_build: str. The build the SKPs were captured from.
      dest_dir: path obj. The directory to download SKPs into.
    """
    skps_dir = dest_dir.join('subordinate%s' % subordinate_num)
    self.m.file.makedirs('SKPs dir', skps_dir)
    full_source = 'gs://%s/skps/%s/%s/subordinate%s' % (
        self.CT_GS_BUCKET, page_type, skps_chromium_build, subordinate_num)
    self.m.gsutil(['-m', 'rsync', '-d', '-r', full_source, skps_dir])

  def create_isolated_gen_json(self, isolate_path, base_dir, os_type,
                               subordinate_num, extra_variables):
    """Creates an isolated.gen.json file.

    Args:
      isolate_path: path obj. Path to the isolate file.
      base_dir: path obj. Dir that is the base of all paths in the isolate file.
      os_type: str. The OS type to use when archiving the isolate file.
               Eg: linux.
      subordinate_num: int. The subordinate we want to create isolated.gen.json file for.
      extra_variables: dict of str to str. The extra vars to pass to isolate.
                      Eg: {'SLAVE_NUM': '1', 'MASTER': 'ChromiumPerfFYI'}

    Returns:
      Path to the isolated.gen.json file.
    """
    self.m.file.makedirs('swarming tmp dir', self.swarming_temp_dir)
    isolated_path = self.swarming_temp_dir.join(
        'ct-task-%s.isolated' % subordinate_num)
    isolate_args = [
      '--isolate', isolate_path,
      '--isolated', isolated_path,
      '--config-variable', 'OS', os_type,
    ]
    for k, v in extra_variables.iteritems():
      isolate_args.extend(['--extra-variable', k, v])
    isolated_gen_dict = {
      'version': 1,
      'dir': base_dir,
      'args': isolate_args,
    }
    isolated_gen_json = self.swarming_temp_dir.join(
        'subordinate%s.isolated.gen.json' % subordinate_num)
    self.m.file.write(
        'Write subordinate%s.isolated.gen.json' % subordinate_num,
        isolated_gen_json,
        self.m.json.dumps(isolated_gen_dict, indent=4),
    )

  def batcharchive(self, num_subordinates, subordinate_start_num=1):
    """Calls batcharchive on the specified isolated.gen.json files.

    Args:
      num_subordinates: int. The number of subordinates we will batcharchive
                  isolated.gen.json files for.
      subordinate_start_num: int. Which subordinate number to start with. Optional.
    """
    self.m.isolate.isolate_tests(
        verbose=True,  # To avoid no output timeouts.
        build_dir=self.swarming_temp_dir,
        targets=[
            'subordinate%s' % num for num in xrange(subordinate_start_num, num_subordinates+1)])

  def trigger_swarming_tasks(self, swarm_hashes, task_name_prefix, dimensions):
    """Triggers swarming tasks using swarm hashes.

    Args:
      swarm_hashes: list of str. List of swarm hashes from the isolate server.
      task_name_prefix: The prefix to use when creating task_name.
      dimensions: dict of str to str. The dimensions to run the task on.
                  Eg: {'os': 'Ubuntu', 'gpu': '10de'}
    Returns:
      List of swarming.SwarmingTask instances.
    """
    swarming_tasks = []
    for task_num, swarm_hash in enumerate(swarm_hashes):
      swarming_task = self.m.swarming.task(
          title='%s-%s' % (task_name_prefix, task_num+1),
          isolated_hash=swarm_hash,
          task_output_dir=self.tasks_output_dir.join('subordinate%s' % (task_num+1)))
      swarming_task.dimensions = dimensions
      swarming_task.priority = 90
      swarming_task.expiration = 4*60*60
      swarming_tasks.append(swarming_task)
    self.m.swarming.trigger(swarming_tasks)
    return swarming_tasks

  def collect_swarming_task(self, swarming_task):
    """Collects the specified swarming task.

    Args:
      swarming_task: An instance of swarming.SwarmingTask.
    """
    return self.m.swarming.collect_task(swarming_task)

