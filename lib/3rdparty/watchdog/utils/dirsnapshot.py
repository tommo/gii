#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Yesudeep Mangalapilly <yesudeep@gmail.com>
# Copyright 2012 Google, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
:module: watchdog.utils.dirsnapshot
:synopsis: Directory snapshots and comparison.
:author: yesudeep@google.com (Yesudeep Mangalapilly)

.. ADMONITION:: Where are the moved events? They "disappeared"

        This implementation does not take partition boundaries
        into consideration. It will only work when the directory
        tree is entirely on the same file system. More specifically,
        any part of the code that depends on inode numbers can
        break if partition boundaries are crossed. In these cases,
        the snapshot diff will represent file/directory movement as
        created and deleted events.

        Windows does not have any concept of ``inodes``, which prevents
        this snapshotter from determining file or directory renames/movement
        on it. The snapshotter does not try to handle this on Windows.
        File or directory movement will show up as creation and deletion
        events.

        Please do not use this on a virtual file system mapped to
        a network share.

Classes
-------
.. autoclass:: DirectorySnapshot
   :members:
   :show-inheritance:

.. autoclass:: DirectorySnapshotDiff
   :members:
   :show-inheritance:

"""

import os
import sys
import stat
import itertools

from pathtools.path import walk as path_walk, absolute_path
from watchdog.utils import platform


class DirectorySnapshotDiff(object):
    """
    Compares two directory snapshots and creates an object that represents
    the difference between the two snapshots.

    :param ref:
        The reference directory snapshot.
    :type ref:
        :class:`DirectorySnapshot`
    :param snapshot:
        The directory snapshot which will be compared
        with the reference snapshot.
    :type snapshot:
        :class:`DirectorySnapshot`
    """
    
    def __init__(self, ref, snapshot):
        created = snapshot.paths - ref.paths
        deleted = ref.paths - snapshot.paths
        
        # check that all unchanged paths have the same inode
        for path in ref.paths & snapshot.paths:
            if ref.inode(path) != snapshot.inode(path):
                created.add(path)
                deleted.add(path)
        
        # find moved paths
        moved = set()
        for path in set(deleted):
            inode = ref.inode(path)
            new_path = snapshot.path(inode)
            if new_path:
                # file is not deleted but moved
                deleted.remove(path)
                moved.add((path, new_path))
        
        for path in set(created):
            inode = snapshot.inode(path)
            old_path = ref.path(inode)
            if old_path:
                created.remove(path)
                moved.add((old_path, path))
        
        # find modified paths
        # first check paths that have not moved
        modified = set()
        for path in ref.paths & snapshot.paths:
            if ref.inode(path) == snapshot.inode(path):
                if ref.mtime(path) != snapshot.mtime(path):
                    modified.add(path)
        
        for (old_path, new_path) in moved:
            if ref.mtime(old_path) != snapshot.mtime(new_path):
                modified.add(old_path)
        
        self._dirs_created = [path for path in created if snapshot.isdir(path)]
        self._dirs_deleted = [path for path in deleted if ref.isdir(path)]
        self._dirs_modified = [path for path in modified if ref.isdir(path)]
        self._dirs_moved = [(frm, to) for (frm, to) in moved if ref.isdir(frm)]
        
        self._files_created = list(created - set(self._dirs_created))
        self._files_deleted = list(deleted - set(self._dirs_deleted))
        self._files_modified = list(modified - set(self._dirs_modified))
        self._files_moved = list(moved - set(self._dirs_moved))
    
    @property
    def files_created(self):
        """List of files that were created."""
        return self._files_created

    @property
    def files_deleted(self):
        """List of files that were deleted."""
        return self._files_deleted

    @property
    def files_modified(self):
        """List of files that were modified."""
        return self._files_modified

    @property
    def files_moved(self):
        """
        List of files that were moved.

        Each event is a two-tuple the first item of which is the path
        that has been renamed to the second item in the tuple.
        """
        return self._files_moved

    @property
    def dirs_modified(self):
        """
        List of directories that were modified.
        """
        return self._dirs_modified

    @property
    def dirs_moved(self):
        """
        List of directories that were moved.

        Each event is a two-tuple the first item of which is the path
        that has been renamed to the second item in the tuple.
        """
        return self._dirs_moved

    @property
    def dirs_deleted(self):
        """
        List of directories that were deleted.
        """
        return self._dirs_deleted

    @property
    def dirs_created(self):
        """
        List of directories that were created.
        """
        return self._dirs_created

class DirectorySnapshot(object):
    """
    A snapshot of stat information of files in a directory.

    :param path:
        The directory path for which a snapshot should be taken.
    :type path:
        ``str``
    :param recursive:
        ``True`` if the entired directory tree should be included in the
        snapshot; ``False`` otherwise.
    :type recursive:
        ``bool``
    :param walker_callback:
        .. deprecated:: 0.7.2
        
        A function with the signature ``walker_callback(path, stat_info)``
        which will be called for every entry in the directory tree.
    """
    
    def __init__(self, path, recursive=True, walker_callback=(lambda p, s: None)):
        from watchdog.utils import stat
        statf = stat
        walker = path_walk
        self._stat_info = {}
        self._inode_to_path = {}
        
        stat_info = statf(path)
        self._stat_info[path] = stat_info
        self._inode_to_path[stat_info.st_ino] = self.path
        
        for root, directories, files in walker(path, recursive):
            for directory_name in directories:
                try:
                    directory_path = os.path.join(root, directory_name)
                    stat_info = statf(directory_path)
                    self._stat_info[directory_path] = stat_info
                    self._inode_to_path[stat_info.st_ino] = directory_path
                    walker_callback(directory_path, stat_info)
                except OSError:
                    continue

            for file_name in files:
                try:
                    file_path = os.path.join(root, file_name)
                    stat_info = statf(file_path)
                    self._stat_info[file_path] = stat_info
                    self._inode_to_path[stat_info.st_ino] = file_path
                    walker_callback(file_path, stat_info)
                except OSError:
                    continue
    
    @property
    def paths(self):
        """
        Set of file/directory paths in the snapshot.
        """
        return set(self._stat_info.keys())
    
    def path(self, inode):
        """
        Returns path for inode. None if inode is unknown to this snapshot.
        """
        return self._inode_to_path.get(inode)
    
    def inode(self, path):
        """
        Returns inode for path.
        """
        return self._stat_info[path].st_ino
    
    def isdir(self, path):
        return stat.S_ISDIR(self._stat_info[path].st_mode)
    
    def mtime(self, path):
        return self._stat_info[path].st_mtime
    
    def __sub__(self, previous_dirsnap):
        """Allow subtracting a DirectorySnapshot object instance from
        another.

        :returns:
            A :class:`DirectorySnapshotDiff` object.
        """
        return DirectorySnapshotDiff(previous_dirsnap, self)
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return str(self._stat_info)
    
    
    ### deprecated methods ###
    
    @property
    def stat_snapshot(self):
        """
        .. deprecated:: 0.7.2
           Use :func:`inode`, :func:`isdir` and :func:`mtime` instead.
        
        Returns a dictionary of stat information with file paths being keys.
        """
        return self._stat_info

    def stat_info(self, path):
        """
        .. deprecated:: 0.7.2
           Use :func:`inode`, :func:`isdir` and :func:`mtime` instead.
        
        Returns a stat information object for the specified path from
        the snapshot.

        :param path:
            The path for which stat information should be obtained
            from a snapshot.
        """
        return self._stat_info[path]

    def path_for_inode(self, inode):
        """
        .. deprecated:: 0.7.2
           Use :func:`path` instead.
        
        Determines the path that an inode represents in a snapshot.

        :param inode:
            inode number.
        """
        return self._inode_to_path[inode]

    def has_inode(self, inode):
        """
        .. deprecated:: 0.7.2
           Use :func:`inode` instead.
        
        Determines if the inode exists.

        :param inode:
            inode number.
        """
        return inode in self._inode_to_path

    def stat_info_for_inode(self, inode):
        """
        .. deprecated:: 0.7.2
        
        Determines stat information for a given inode.

        :param inode:
            inode number.
        """
        return self.stat_info(self.path_for_inode(inode))
