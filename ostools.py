#******************************************************************************
# * Copyright (c) 2019, XtremeDV. All rights reserved.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
# * Author: Jude Zhang, Email: zhajio.1988@gmail.com
# *******************************************************************************
# Copyright (c) 2014-2018, Lars Asplund lars.anders.asplund@gmail.com
"""
Provides operating systems dependent functionality that can be easily
stubbed for testing
"""

from __future__ import print_function

import time
import subprocess
import threading
import psutil
import shutil
import sys
import signal
try:
    # Python 3.x
    from queue import Queue, Empty
except ImportError:
    # Python 2.7
    from Queue import Queue, Empty  # pylint: disable=import-error

from os.path import exists, getmtime, dirname, relpath, splitdrive
import os
import io

import logging
LOGGER = logging.getLogger(__name__)

class ProgramStatus(object):
    """
    Maintain global program status to support graceful shutdown
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._shutting_down = False

    @property
    def is_shutting_down(self):
        with self._lock:  # pylint: disable=not-context-manager
            return self._shutting_down

    def check_for_shutdown(self):
        if self.is_shutting_down:
            raise KeyboardInterrupt

    def shutdown(self):
        with self._lock:  # pylint: disable=not-context-manager
            LOGGER.debug("ProgramStatus.shutdown")
            self._shutting_down = True

    def reset(self):
        with self._lock:  # pylint: disable=not-context-manager
            self._shutting_down = False


PROGRAM_STATUS = ProgramStatus()


class InterruptableQueue(object):
    """
    A Queue which can be interrupted
    """

    def __init__(self):
        self._queue = Queue()

    def get(self):
        """
        Get a value from the queue
        """
        while True:
            PROGRAM_STATUS.check_for_shutdown()
            try:
                return self._queue.get(timeout=0.1)
            except Empty:
                pass

    def put(self, value):
        self._queue.put(value)

    def empty(self):
        return self._queue.empty()


class Process(object):
    """
    A simple process interface which supports asynchronously consuming the stdout and stderr
    of the process while it is running.
    """

    class NonZeroExitCode(Exception):
        pass

    def __init__(self, cmd, cwd=None, env=None):
        self._cmd = cmd
        self._cwd = cwd

        # Create process with new process group
        # Sending a signal to a process group will send it to all children
        # Hopefully this way no orphaned processes will be left behind
        self._process = subprocess.Popen(
            self._cmd,
            cwd=self._cwd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True,
            bufsize=0,
            # Create new process group on POSIX, setpgrp does not exist on Windows
            #preexec_fn=os.setsid)
            preexec_fn=os.setpgrp)  # pylint: disable=no-member
        LOGGER.debug("Started process with pid=%i: '%s'", self._process.pid, (" ".join(self._cwd)))

        self._queue = InterruptableQueue()
        self._reader = AsynchronousFileReader(self._process.stdout, self._queue)
        self._reader.start()

    def write(self, *args, **kwargs):
        """ Write to stdin """
        if not self._process.stdin.closed:
            self._process.stdin.write(*args, **kwargs)

    def writeline(self, line):
        """ Write a line to stdin """
        if not self._process.stdin.closed:
            self._process.stdin.write(line + "\n")
            self._process.stdin.flush()

    def next_line(self):
        """
        Return either the next line or the exit code
        """

        if not self._reader.eof():
            # Show what we received from standard output.
            msg = self._queue.get()

            if msg is not None:
                return msg

        retcode = self.wait()
        return retcode

    def wait(self):
        """
        Wait while without completely blocking to avoid
        deadlock when shutting down
        """
        while self._process.poll() is None:
            PROGRAM_STATUS.check_for_shutdown()
            time.sleep(0.05)
            LOGGER.debug("Waiting for process with pid=%i to stop", self._process.pid)
        return self._process.returncode

    def is_alive(self):
        """
        Returns true if alive
        """
        return self._process.poll() is None

    def consume_output(self, callback=print):
        """
        Consume the output of the process.
        The output is interpreted as UTF-8 text.

        @param callback Called for each line of output
        @raises Process.NonZeroExitCode when the process does not exit with code zero
        """

        def default_callback(*args, **kwargs):
            pass

        if not callback:
            callback = default_callback

        while not self._reader.eof():
            line = self._queue.get()
            if line is None:
                break
            if callback(line) is not None:
                return

        retcode = None
        while retcode is None:
            retcode = self.wait()
            if retcode != 0:
                raise Process.NonZeroExitCode

    def terminate(self):
        """
        Terminate the process
        """
        if self._process.poll() is None:
            process = psutil.Process(self._process.pid)
            proc_list = process.children(recursive=True)
            #proc_list.reverse()
            for proc in proc_list:
                proc.kill()
            process.kill()

        # Let's be tidy and join the threads we've started.
        if self._process.poll() is None:
            LOGGER.debug("Terminating process with pid=%i", self._process.pid)
            self._process.terminate()

        if self._process.poll() is None:
            time.sleep(0.05)

        if self._process.poll() is None:
            LOGGER.debug("Killing process with pid=%i", self._process.pid)
            self._process.kill()

        if self._process.poll() is None:
            LOGGER.debug("Waiting for process with pid=%i", self._process.pid)
            self.wait()

        LOGGER.debug("Process with pid=%i terminated with code=%i",
                     self._process.pid,
                     self._process.returncode)

        self._reader.join()
        self._process.stdout.close()
        self._process.stdin.close()

    def __del__(self):
        try:
            self.terminate()
        except KeyboardInterrupt:
            LOGGER.debug("Process.__del__: Ignoring KeyboardInterrupt")

class AsynchronousFileReader(threading.Thread):
    """
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    """

    def __init__(self, fd, queue, encoding="utf-8"):
        threading.Thread.__init__(self)

        # If Python 3 change encoding of TextIOWrapper to utf-8 ignoring decode errors
        if isinstance(fd, io.TextIOWrapper):
            fd = io.TextIOWrapper(fd.buffer, encoding=encoding, errors="ignore")

        self._fd = fd
        self._queue = queue
        self._encoding = encoding

    def run(self):
        """The body of the thread: read lines and put them on the queue."""
        for line in iter(self._fd.readline, ""):
            if PROGRAM_STATUS.is_shutting_down:
                break

            # Convert string into utf-8 if necessary
            if sys.version_info.major == 2:
                string = line[:-1].decode(encoding=self._encoding, errors="ignore")
            else:
                string = line[:-1]

            self._queue.put(string)
        self._queue.put(None)

    def eof(self):
        """Check whether there is no more content to expect."""
        return not self.is_alive() and self._queue.empty()


def read_file(file_name, encoding="utf-8", newline=None):
    """ To stub during testing """
    try:
        with io.open(file_name, "r", encoding=encoding, newline=newline) as file_to_read:
            data = file_to_read.read()
    except UnicodeDecodeError:
        LOGGER.warning("Could not decode file %s using encoding %s, ignoring encoding errors",
                       file_name, encoding)
        with io.open(file_name, "r", encoding=encoding, errors="ignore", newline=newline) as file_to_read:
            data = file_to_read.read()

    return data

def write_file(file_name, contents, encoding="utf-8"):
    """ To stub during testing """

    path = dirname(file_name)
    if path == "":
        path = "."

    if not file_exists(path):
        os.makedirs(path)

    with io.open(file_name, "wb") as file_to_write:
        file_to_write.write(contents.encode(encoding=encoding))


def file_exists(file_name):
    """ To stub during testing """
    return exists(file_name)


def get_modification_time(file_name):
    """ To stub during testing """
    return getmtime(file_name)


def get_time():
    """ To stub during testing """
    return time.time()


def renew_path(path):
    """
    Ensure path directory exists and is empty
    """
    if exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def simplify_path(path):
    """
    Return relative path towards current working directory
    unless it is a separate Windows drive
    """
    cwd = os.getcwd()
    drive_cwd = splitdrive(cwd)[0]
    drive_path = splitdrive(path)[0]
    if drive_path == drive_cwd:
        return relpath(path, cwd)

    return path
