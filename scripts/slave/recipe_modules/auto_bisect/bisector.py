import re

from . import depot_config

_DEPS_SHA_PATCH = """
diff --git DEPS.sha DEPS.sha
new file mode 100644
--- /dev/null
+++ DEPS.sha
@@ -0,0 +1 @@
+%(deps_sha)s
"""

    # Test-only properties.
        'dummy_regression_confidence')
  def make_deps_sha_file(self, deps_sha):
    """Make a diff patch that creates DEPS.sha.
    Args:
      deps_sha (str): The hex digest of a SHA1 hash of the diff that patches
        DEPS.

    Returns:
      A string containing a git diff.
    """
    return _DEPS_SHA_PATCH % {'deps_sha': deps_sha}

  def _git_intern_file(self, file_contents, cwd, commit_hash):
    """Writes a file to the git database and produces its git hash.
      file_contents (str): The contents of the file to be hashed and interned.
      cwd (recipe_config_types.Path): Path to the checkout whose repository the
        file is to be written to.
      commit_hash (str): An identifier for the step.

    Returns:
      A string containing the hash of the interned object.
    """
    cmd = 'hash-object -t blob -w --stdin'.split(' ')
    stdin = self.api.m.raw_io.input(file_contents)
    stdout = self.api.m.raw_io.output()
    step_name = 'Hashing modified DEPS file with revision ' + commit_hash
    step_result = self.api.m.git(*cmd, cwd=cwd, stdin=stdin, stdout=stdout,
                                 name=step_name)
    hash_string = step_result.stdout.splitlines()[0]
    try:
      if hash_string:
          int(hash_string, 16)
          return hash_string
    except ValueError:
      pass

    raise self.api.m.step.StepFailure('Git did not output a valid hash for the '
                                      'interned file.')

  def _gen_diff_patch(self, git_object_a, git_object_b, src_alias, dst_alias,
                      cwd, deps_rev):
    """Produces a git diff patch.

    Args:
      git_object_a (str): Tree-ish git object identifier.
      git_object_b (str): Another tree-ish git object identifier.
      src_alias (str): Label to replace the tree-ish identifier on
        the resulting diff patch. (git_object_a)
      dst_alias (str): Same as above for (git_object_b) 
      cwd (recipe_config_types.Path): Path to the checkout whose repo contains
        the objects to be compared.
      deps_rev (str): Deps revision to identify the patch generating step.

    Returns:
      A string containing the diff patch as produced by the 'git diff' command.
    """
    # The prefixes used in the command below are used to find and replace the
    # tree-ish git object id's on the diff output more easily.
    cmd = 'diff %s %s --src-prefix=IAMSRC: --dst-prefix=IAMDST:'
    cmd %= (git_object_a, git_object_b)
    cmd = cmd.split(' ')
    stdout = self.api.m.raw_io.output()
    step_name = 'Generating patch for %s to %s' % (git_object_a, deps_rev)
    step_result = self.api.m.git(*cmd, cwd=cwd, stdout=stdout, name=step_name)
    patch_text = step_result.stdout
    src_string = 'IAMSRC:' + git_object_a
    dst_string = 'IAMDST:' + git_object_b
    patch_text = patch_text.replace(src_string, src_alias)
    patch_text = patch_text.replace(dst_string, dst_alias)
    return patch_text

  def make_deps_patch(self, base_revision, base_file_contents,
                      depot, new_commit_hash):
    """Make a diff patch that updates a specific dependency revision.

    Args:
      base_revision (RevisionState): The revision for which the DEPS file is to
        be patched.
      base_file_contents (str): The contents of the original DEPS file.
      depot (str): The dependency to modify.
      new_commit_hash (str): The revision to put in place of the old one.

    Returns:
      A pair containing the git diff patch that updates DEPS, and the
      full text of the modified DEPS file, both as strings.
    """
    original_contents = str(base_file_contents)
    patched_contents = str(original_contents)

    # Modify DEPS
    deps_var = depot['deps_var']
    deps_item_regexp = re.compile(
        r'(?<=["\']%s["\']: ["\'])([a-fA-F0-9]+)(?=["\'])' % deps_var,
        re.MULTILINE)
    if not re.search(deps_item_regexp, original_contents):
      raise self.api.m.step.StepFailure('DEPS file does not contain entry for '
                                        + deps_var)
    patched_contents = re.sub(deps_item_regexp, new_commit_hash,
                              original_contents)

    interned_deps_hash = self._git_intern_file(patched_contents,
                                               self.api.m.path['checkout'],
                                               new_commit_hash)
    patch_text = self._gen_diff_patch(base_revision.commit_hash + ':DEPS',
                                      interned_deps_hash, 'DEPS', 'DEPS',
                                      cwd=self.api.m.path['checkout'],
                                      deps_rev=new_commit_hash)
    return patch_text, patched_contents

  def _get_rev_range_for_depot(self, depot_name, min_rev, max_rev,
                               base_revision):
    results = []
    depot = depot_config.DEPOT_DEPS_NAME[depot_name]
    depot_path = self.api.m.path['slave_build'].join(depot['src'])
    step_name = ('Expanding revision range for revision %s on depot %s'
                 % (max_rev, depot_name))
    step_result = self.api.m.git('log', '--format=%H', min_rev + '...' +
                                 max_rev, stdout=self.api.m.raw_io.output(),
                                 cwd=depot_path, name=step_name)
    # We skip the first revision in the list as it is max_rev
    new_revisions = step_result.stdout.splitlines()[1:]
    for revision in new_revisions:
      results.append(self.revision_class(None, self,
                                         base_revision=base_revision,
                                         deps_revision=revision,
                                         dependency_depot_name=depot_name,
                                         depot=depot))
    results.reverse()
    return results

  def _expand_revision_range(self):
    """Populates the revisions attribute.

    After running this method, self.revisions should contain all the chromium
    revisions between the good and bad revisions.
    self._update_revision_list_indexes()

  def _expand_deps_revisions(self, revision_to_expand):
    """Populates the revisions attribute with additional deps revisions.

    Inserts the revisions from the external repos in the appropriate place.

    Args:
      revision_to_expand: A revision where there is a deps change.

    Returns:
      A boolean indicating whether any revisions were inserted.
    """
    # TODO(robertocn): Review variable names in this function. They are
    # potentially confusing.
    assert revision_to_expand is not None
    try:
      min_revision = revision_to_expand.previous_revision
      max_revision = revision_to_expand
      min_revision.read_deps()  # Parses DEPS file and sets the .deps property.
      max_revision.read_deps()  # Ditto.
      for depot_name in depot_config.DEPOT_DEPS_NAME.keys():
        if depot_name in min_revision.deps and depot_name in max_revision.deps:
          dep_revision_min = min_revision.deps[depot_name]
          dep_revision_max = max_revision.deps[depot_name]
          if (dep_revision_min and dep_revision_max and
              dep_revision_min != dep_revision_max):
            rev_list = self._get_rev_range_for_depot(depot_name,
                                                     dep_revision_min,
                                                     dep_revision_max,
                                                     min_revision)
            new_revisions = self.revisions[:max_revision.list_index]
            new_revisions += rev_list
            new_revisions += self.revisions[max_revision.list_index:]
            self.revisions = new_revisions
            self._update_revision_list_indexes()
            return True
    except RuntimeError:
      warning_text = ('Could not expand dependency revisions for ' +
                      revision_to_expand.revision_string)
      if warning_text not in self.warnings:
        self.warnings.append(warning_text)
    return False


  def _update_revision_list_indexes(self):
    """Sets list_index, next and previous properties for each revision."""
    The change between the test results obtained for the given 'good' and
    'bad' revisions is expected to be considered a regression. The
    `improvement_direction` attribute is positive if a larger number is
    considered better, and negative if a smaller number is considered better.
        more_revisions = self._expand_deps_revisions(revision)
        return not more_revisions
      if revision.next_revision.deps_change():
        more_revisions = self._expand_deps_revisions(revision.next_revision)
        return not more_revisions