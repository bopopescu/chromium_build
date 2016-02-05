# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import contextlib

DEPS = [
  'depot_tools/gclient',
  'depot_tools/git',
  'file',
  'gsutil',
  'recipe_engine/path',
  'recipe_engine/platform',
  'recipe_engine/properties',
  'recipe_engine/step',
  'zip',
]

# TODO(eseidel): This should be flutter_infra, not mojo_infra.
BUCKET_NAME = 'mojo_infra'

def GetCloudPath(api, path):
  # TODO(eseidel): Is 'revision' the right way to get the git hash?
  return 'flutter/%s/%s' % (api.properties.get('revision'), path)


# TODO(eseidel): This belongs as api.zip.ZipPackage.add_files
def AddFiles(pkg, relative_paths):
  for path in relative_paths:
    pkg.add_file(pkg.root.join(path))


def Build(api, config, *targets):
  checkout = api.path['checkout']
  build_dir = checkout.join('out/%s' % config)
  ninja_args = ['ninja', '-C', build_dir]
  ninja_args.extend(targets)
  api.step('build %s' % config, ninja_args)


def RunGN(api, *args):
  checkout = api.path['checkout']
  gn_cmd = [checkout.join('sky/tools/gn')]
  gn_cmd.extend(args)
  api.step('gn %s' % ' '.join(args), gn_cmd)


# TODO(eseidel): Would be nice to have this on api.path or api.file.
@contextlib.contextmanager
def MakeTempDir(api):
  try:
    temp_dir = api.path.mkdtemp('tmp')
    yield temp_dir
  finally:
    api.file.rmtree('temp dir', temp_dir)


def AnalyzeDartUI(api):
  RunGN(api, '--debug')
  Build(api, 'Debug', 'generate_dart_ui')

  checkout = api.path['checkout']
  api.step('analyze dart_ui', ['/bin/sh', 'travis/analyze.sh'], cwd=checkout)


def BuildLinuxAndroid(api):
  RunGN(api, '--release', '--android', '--enable-firebase', '--enable-gcm')
  Build(api, 'android_Release', 'apks/SkyShell.apk', 'flutter.mojo',
      'sky/services/gcm', 'sky/services/firebase')

  with MakeTempDir(api) as tmp_dir:
    local_zip = tmp_dir.join('artifacts.zip')
    remote_zip = GetCloudPath(api, 'android-arm/artifacts.zip')
    checkout = api.path['checkout']
    pkg = api.zip.make_package(checkout, local_zip)

    AddFiles(pkg, [
      'build/android/ant/chromium-debug.keystore',
      'out/android_Release/apks/SkyShell.apk',
      'out/android_Release/flutter.mojo',
      # Unclear if this is the right way to work around draconian 80c rule:
      'out/android_Release/gen/sky/shell/shell/shell/libs/armeabi-v7a/' +
      'libsky_shell.so',
      'out/android_Release/icudtl.dat',
    ])

    # TODO(mpcomplete): stop bundling classes.dex once
    # https://github.com/flutter/flutter/pull/1263 lands.
    AddFiles(pkg, [
      'out/android_Release/gen/sky/shell/shell/classes.dex.jar',
      'out/android_Release/gen/sky/shell/shell/classes.dex',
    ])

    pkg.zip('Zip Android Artifacts')
    api.gsutil.upload(local_zip, BUCKET_NAME, remote_zip)


  def UploadService(name):
    def Upload(from_path, to_path):
      api.gsutil.upload(from_path, BUCKET_NAME, GetCloudPath(api, to_path))

    def ServicesOut(path):
      return checkout.join('out/android_Release/gen/sky/services/%s' % path)

    dex_jar = '%s/%s_lib.dex.jar' % (name, name)
    interfaces_jar = '%s/interfaces_java.dex.jar' % (name)
    Upload(ServicesOut(dex_jar), dex_jar)
    Upload(ServicesOut(interfaces_jar), interfaces_jar)

  UploadService('gcm')
  UploadService('firebase')


def BuildLinux(api):
  RunGN(api, '--release')
  Build(api, 'Release')

  with MakeTempDir(api) as temp_dir:
    local_zip = temp_dir.join('artifacts.zip')
    remote_zip = GetCloudPath(api, 'linux-x64/artifacts.zip')
    pkg = api.zip.make_package(api.path['checkout'], local_zip)
    AddFiles(pkg, [
      'out/Release/flutter.mojo',
      'out/Release/icudtl.dat',
      'out/Release/sky_shell',
      'out/Release/sky_snapshot',
    ])

    pkg.zip('Zip Linux Artifacts')
    api.gsutil.upload(local_zip, BUCKET_NAME, remote_zip)


def BuildMac(api):
  RunGN(api, '--release')
  Build(api, 'Release', 'sky_snapshot')

  with MakeTempDir(api) as temp_dir:
    local_zip = temp_dir.join('artifacts.zip')
    remote_zip = GetCloudPath(api, 'darwin-x64/artifacts.zip')
    pkg = api.zip.make_package(api.path['checkout'], local_zip)
    pkg.add_file(pkg.root.join('out/Release/sky_snapshot'))
    pkg.zip('Zip Artifacts')
    api.gsutil.upload(pkg.output, BUCKET_NAME, remote_zip)


def GenerateXcodeProject(api):
  checkout = api.path['checkout']
  out_dir = checkout.join('out')

  RunGN(api, '--release', '--ios', '--simulator')
  Build(api, 'ios_sim_Release')

  RunGN(api, '--release', '--ios')
  Build(api, 'ios_Release')

  # Merge build artifacts
  deploy_dir = out_dir.join('FlutterXcode')
  api.file.makedirs('mkdir', deploy_dir)
  api.file.copytree('copy sim', checkout.join('ios_sim_Release/Flutter'),
      deploy_dir)
  api.file.copytree('copy sim', checkout.join('ios_Release/Flutter'),
      deploy_dir)
  flutter_zip = out_dir.join('FlutterXcode.zip')
  api.zip.directory('make FlutterXcode.zip', deploy_dir.join('Flutter'),
    flutter_zip)

  cloud_path =  GetCloudPath(api, 'ios/FlutterXcode.zip')
  api.gsutil.upload(flutter_zip, 'flutter_infra', cloud_path)


def GetCheckout(api):
  src_cfg = api.gclient.make_config(GIT_MODE=True)
  soln = src_cfg.solutions.add()
  soln.name = 'src'
  soln.url = 'https://chromium.googlesource.com/external/github.com/flutter/engine'
  # TODO(eseidel): What does parent_got_revision_mapping do?  Do I care?
  src_cfg.parent_got_revision_mapping['parent_got_revision'] = 'got_revision'
  api.gclient.c = src_cfg
  api.gclient.checkout()
  # Do I need to call gclient.sync(src_cfg)?
  api.gclient.runhooks()


def RunSteps(api):
  GetCheckout(api)

  checkout = api.path['checkout']
  dart_bin = checkout.join('third_party', 'dart-sdk', 'dart-sdk', 'bin')
  env = { 'PATH': api.path.pathsep.join((str(dart_bin), '%(PATH)s')) }

  # The context adds dart to the path, only needed for the analyze step for now.
  with api.step.context({'env': env}):
    AnalyzeDartUI(api)

    if api.platform.is_linux:
      BuildLinux(api)
      BuildLinuxAndroid(api)

    if api.platform.is_mac:
      BuildMac(api)
      GenerateXcodeProject(api)


def GenTests(api):
  yield api.test('linux') + api.platform('linux', 64)
  yield api.test('mac') + api.platform('mac', 64)