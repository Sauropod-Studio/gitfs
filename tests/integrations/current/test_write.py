# Copyright 2015 Justus Perlwitz
# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import collections
import os
import pytest
import shutil
import string
import time

from tests.integrations.base import BaseTest, pull, gitfs_log


class TestWriteCurrentView(BaseTest):
    def test_delete_directory_with_space_within_name(self, gitfs_log):
        directory = "%s/new directory" % self.current_path

        with gitfs_log("SyncWorker: Set push_successful"):
            os.makedirs(directory)
        with pull(self.sh):
            # check if directory exists or not
            directory_path = "%s/new directory" % self.repo_path
            assert os.path.exists(directory_path)

            # check for .keep file
            keep_path = "%s/new directory/.keep" % self.repo_path
            assert os.path.exists(keep_path)

            self.assert_new_commit()
            self.assert_commit_message("Create the /new directory directory")

        with gitfs_log("SyncWorker: Set push_successful"):
            shutil.rmtree("%s/new directory/" % self.current_path)

        with pull(self.sh):
            self.assert_new_commit()

        assert os.path.exists(directory) is False

    def test_delete_a_directory(self, gitfs_log):
        path = "%s/a_directory/another_dir/" % self.current_path
        with gitfs_log("SyncWorker: Set push_successful"):
            os.makedirs(path)

        with pull(self.sh):
            self.assert_new_commit()

        with gitfs_log("SyncWorker: Set push_successful"):
            shutil.rmtree("%s/a_directory/" % self.current_path)

        with pull(self.sh):
            self.assert_commit_message("Update 2 items")
            self.assert_new_commit()

        assert os.path.exists(path) is False

    def test_rename_directory(self, gitfs_log):
        old_dir = "%s/a_directory/" % self.current_path
        new_dir = "%s/some_directory/" % self.current_path
        with gitfs_log("SyncWorker: Set push_successful"):
            os.makedirs(old_dir)

        with pull(self.sh):
            self.assert_new_commit()

        with gitfs_log("SyncWorker: Set push_successful"):
            os.rename(old_dir, new_dir)

        with pull(self.sh):
            self.assert_new_commit()

        assert os.path.isdir(new_dir) is not False
        assert os.path.exists(old_dir) is False

    def test_link_a_file(self, gitfs_log):
        filename = "%s/link_file" % self.current_path
        link_name = "%s/new_link" % self.current_path

        with open(filename, "w") as f:
            f.write("some content")

        with gitfs_log("SyncWorker: Set push_successful"):
            os.link(filename, link_name)

        with pull(self.sh):
            self.assert_commit_message("Update 2 items")

        is_link = os.path.isfile(link_name)
        assert is_link is not False

    def test_write_a_file(self, gitfs_log):
        content = "Just a small file"
        filename = "%s/new_file" % self.current_path

        with gitfs_log("SyncWorker: Set push_successful"):
            with open(filename, "w") as f:
                f.write(content)

        # check if the write was done correctly
        with open(filename) as f:
            assert f.read() == content

        # check if a commit was made
        with pull(self.sh):
            self.assert_new_commit()
            self.assert_commit_message("Update /new_file")

    def test_create_a_directory(self, gitfs_log):
        directory = "%s/new_directory" % self.current_path
        with gitfs_log("SyncWorker: Set push_successful"):
            os.makedirs(directory)

        with pull(self.sh):
            # check if directory exists or not
            directory_path = "%s/new_directory" % self.repo_path
            assert os.path.exists(directory_path)

            # check for .keep file
            keep_path = "%s/new_directory/.keep" % self.repo_path
            assert os.path.exists(keep_path)

            self.assert_new_commit()
            self.assert_commit_message("Create the /new_directory directory")

    def test_write_in_keep_file(self):
        directory = "%s/new_directory" % self.current_path

        with pytest.raises(IOError):
            with open("%s/.keep" % directory, 'w') as f:
                f.write("some content")

    def test_create_embedded_directory(self, gitfs_log):
        directory = "%s/directory/embedded-directory" % self.current_path
        with gitfs_log("SyncWorker: Set push_successful"):
            os.makedirs(directory)

        with pull(self.sh):
            # check if directory exists or not
            directory_path = "%s/directory/embedded-directory" % self.repo_path
            assert os.path.exists(directory_path)

            # check the existence of the .keep files
            keep_files = [
                "%s/directory/.keep" % self.repo_path,
                "%s/directory/embedded-directory/.keep" % self.repo_path
            ]
            for keep_file in keep_files:
                assert os.path.exists(keep_file)

            self.assert_new_commit()
            commit_msg = "Update 2 items"
            self.assert_commit_message(commit_msg)

    def test_create_directory_inside_an_already_existing_directory(self, gitfs_log):
        directory = "%s/directory/new-embedded-directory" % self.current_path

        with gitfs_log("SyncWorker: Set push_successful"):
            os.makedirs(directory)

        with pull(self.sh):
            # check if directory exists or not
            directory_path = "%s/directory/new-embedded-directory" % self.repo_path
            assert os.path.exists(directory_path)

            # check the existence of the .keep files
            keep_files = [
                "%s/directory/.keep" % self.repo_path,
                "%s/directory/new-embedded-directory/.keep" % self.repo_path
            ]
            for keep_file in keep_files:
                assert os.path.exists(keep_file)

            self.assert_new_commit()
            commit_msg = "Create the /directory/new-embedded-directory directory"
            self.assert_commit_message(commit_msg)

    def test_create_embedded_directory_on_multiple_levels(self, gitfs_log):
        directory = "%s/a/b/c" % self.current_path

        with gitfs_log("SyncWorker: Set push_successful"):
            os.makedirs(directory)

        with pull(self.sh):
            # check if directory exists or not
            directory_path = "%s/a/b/c" % self.repo_path
            assert os.path.exists(directory_path)

            # check the existence of the .keep files
            keep_files = [
                "%s/a/.keep" % self.repo_path,
                "%s/a/b/.keep" % self.repo_path,
                "%s/a/b/c/.keep" % self.repo_path,
            ]
            for keep_file in keep_files:
                assert os.path.exists(keep_file)

            self.assert_new_commit()
            commit_msg = "Update %s items" % len(keep_files)
            self.assert_commit_message(commit_msg)

    def test_create_embedded_directory_big_depth(self, gitfs_log):
        path = ""
        for letter in string.ascii_lowercase:
            path = os.path.join(path, letter)

        with gitfs_log("SyncWorker: Set push_successful"):
            os.makedirs(os.path.join(self.current_path, path))

        with pull(self.sh):
            # check if directory exists or not
            directory_path = os.path.join(self.repo_path, path)
            assert os.path.exists(directory_path)

            # build the paths for the keep files
            keep_files = []
            path = self.repo_path
            for letter in string.letters:
                path = os.path.join(path, letter)
                path_with_keep = os.path.join(path, '.keep')
                keep_files.append(path_with_keep)

            # check the existence of the .keep files
            for keep_file in keep_files:
                assert os.path.exists(keep_file)

    def test_chmod_valid_mode(self, gitfs_log):
        filename = "%s/testing" % self.current_path
        with gitfs_log("SyncWorker: Set push_successful"):
            os.chmod(
                filename,
                0o755,
            )

        with pull(self.sh):
            # check if the right mode was set
            stats = os.stat(filename)
            assert stats.st_mode == 0o100755

            self.assert_new_commit()
            self.assert_commit_message("Chmod to 0755 on /testing")

    def test_chmod_invalid_mode(self):
        filename = "%s/testing" % self.current_path

        with pytest.raises(OSError):
            os.chmod(
                filename,
                0o777,
            )

    def test_rename(self, gitfs_log):
        old_filename = "%s/testing" % self.current_path
        new_filename = "%s/new_testing" % self.current_path

        with gitfs_log("SyncWorker: Set push_successful"):
            os.rename(old_filename, new_filename)

        with pull(self.sh):
            # check for new file
            assert os.path.exists(new_filename)

            self.assert_new_commit()
            self.assert_commit_message("Rename /testing to /new_testing")

    def test_fsync(self, gitfs_log):
        filename = "%s/me" % self.current_path
        content = "test fsync"

        with gitfs_log("SyncWorker: Set push_successful"):
            with open(filename, "w") as f:
                f.write(content)
                os.fsync(f.fileno())

        with pull(self.sh):
            self.assert_new_commit()
            self.assert_commit_message("Update 1 items")

    def test_create(self, gitfs_log):
        filename = "%s/new_empty_file" % self.current_path
        with gitfs_log("SyncWorker: Set push_successful"):
            open(filename, "a").close()

        with pull(self.sh):
            self.assert_new_commit()
            self.assert_commit_message("Created /new_empty_file")

    def test_symbolic_link(self, gitfs_log):
        target = "me"
        name = "%s/links" % self.current_path
        with gitfs_log("SyncWorker: Set push_successful"):
            os.symlink(target, name)

        with pull(self.sh):
            # check if link exists
            assert os.path.exists(name)

            self.assert_new_commit()
            self.assert_commit_message("Create symlink to %s for "
                                       "/links" % (target))

    def test_edit_file(self, gitfs_log):
        content = "first part"
        continuation = "second part"
        filename = "%s/some_file" % self.current_path

        with gitfs_log("SyncWorker: Set push_successful"):
            with open(filename, "w") as f:
                f.write(content)

        with pull(self.sh):
            with open(filename) as f:
                assert f.read() == content

            self.assert_new_commit()

        with pull(self.sh):
            self.assert_commit_message("Update /some_file")

            with gitfs_log("SyncWorker: Set push_successful"):
                with open(filename, "w") as f:
                    f.write(continuation)

        with pull(self.sh):
            with open(filename) as f:
                assert f.read() == continuation

            self.assert_new_commit()

        with pull(self.sh):
            self.assert_commit_message("Update /some_file")

    def test_create_multiple_files(self, gitfs_log):
        content = "Just a small file"
        no_of_files = 10
        filename = "%s/new_file" % self.current_path

        with gitfs_log("SyncWorker: Set push_successful"):
            for i in range(no_of_files):
                with open(filename + str(i), "w") as f:
                    f.write(content)

        with pull(self.sh):
            for i in range(no_of_files):
                with open(filename + str(i)) as f:
                    assert f.read() == content

            self.assert_new_commit()

        with pull(self.sh):
            self.assert_commit_message("Update %d items" % no_of_files)

    def test_delete_file(self, gitfs_log):
        filename = "%s/deletable_file" % self.current_path

        with gitfs_log("SyncWorker: Set push_successful"):
            with open(filename, "w") as f:
                f.write("some content")

        with pull(self.sh):
            self.assert_new_commit()
            self.assert_commit_message("Update /deletable_file")

        with gitfs_log("SyncWorker: Set push_successful"):
            os.remove(filename)

        with pull(self.sh):
            assert not os.path.exists(filename)
            self.assert_commit_message("Deleted /deletable_file")
