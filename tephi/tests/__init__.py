# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""
Provides testing capabilities and customisations specific to tephi.

.. note:: This module needs to control the matplotlib backend, so it
          **must** be imported before ``matplotlib.pyplot``.

By default, this module sets the matplotlib backend to "agg". But when
this module is imported it checks ``sys.argv`` for the flag "-d". If
found, it is removed from ``sys.argv`` and the matplotlib backend is
switched to "tkagg" to allow the interactive visual inspection of
graphical test results.

"""
import codecs
import collections
import io
import json
import os
import sys
import unittest

import filelock
import matplotlib
import numpy as np
import requests

from tephi import DATA_DIR


#: Basepath for test data.
_DATA_PATH = DATA_DIR

#: Basepath for test results.
_RESULT_PATH = os.path.join(os.path.dirname(__file__), "results")

#: Default perceptual hash size.
_HASH_SIZE = 16

#: Default maximum perceptual hash hamming distance.
_HAMMING_DISTANCE = 2

# Whether to display matplotlib output to the screen.
_DISPLAY_FIGURES = False

# Test images URL.
BASE_URL = "https://scitools.github.io/test-tephi-imagehash/images"


try:
    # Added a timeout to stop the call to requests.get hanging when running
    # on a platform which has restricted/no internet access.
    requests.get("https://github.com/SciTools/tephi", timeout=5.0)
    INET_AVAILABLE = True
except requests.exceptions.ConnectionError:
    INET_AVAILABLE = False


skip_inet = unittest.skipIf(
    not INET_AVAILABLE,
    ('Test(s) require an "internet connection", which is not available.'),
)


if "-d" in sys.argv:
    sys.argv.remove("-d")
    matplotlib.use("tkagg")
    _DISPLAY_FIGURES = True
else:
    matplotlib.use("agg")

# Imported now so that matplotlib.use can work
import matplotlib.pyplot as plt


def get_data_path(relative_path):
    """
    Returns the absolute path to a data file when given the relative path
    as a string, or sequence of strings.

    """
    if isinstance(relative_path, (list, tuple)):
        relative_path = os.path.join(*relative_path)
    return os.path.abspath(os.path.join(_DATA_PATH, relative_path))


def get_result_path(relative_path):
    """
    Returns the absolute path to a result file when given the relative path
    as a string, or sequence of strings.

    """
    if isinstance(relative_path, (list, tuple)):
        relative_path = os.path.join(*relative_path)
    return os.path.abspath(os.path.join(_RESULT_PATH, relative_path))


class TephiTest(unittest.TestCase):
    """
    A subclass of unittest.TestCase which provides testing functionality
    specific to tephi.

    """

    _assertion_counts = collections.defaultdict(int)

    def _unique_id(self):
        """
        Returns the unique ID for the current assertion.

        The ID is composed of two parts: a unique ID for the current test
        (which is itself composed of the module, class, and test names), and
        a sequential counter (specific to the current test) that is incremented
        on each call.

        For example, calls from a "test_tx" routine followed by a "test_ty"
        routine might result in::
            test_plot.TestContourf.test_tx.0
            test_plot.TestContourf.test_tx.1
            test_plot.TestContourf.test_tx.2
            test_plot.TestContourf.test_ty.0

        """
        # Obtain a consistent ID for the current test.

        # NB. unittest.TestCase.id() returns different values depending on
        # whether the test has been run explicitly, or via test discovery.
        # For example:
        #   python tests/test_brand.py
        #       => '__main__.TestBranding.test_combo'
        #   python -m unittest discover
        #       => 'tephi.tests.test_brand.TestBranding.test_combo'
        bits = self.id().split(".")[-3:]
        if bits[0] == "__main__":
            file_name = os.path.basename(sys.modules["__main__"].__file__)
            bits[0] = os.path.splitext(file_name)[0]
        test_id = ".".join(bits)

        # Derive the sequential assertion ID within the test
        assertion_id = self._assertion_counts[test_id]
        self._assertion_counts[test_id] += 1

        return "{}.{}".format(test_id, assertion_id)

    def assertArrayEqual(self, a, b):
        return np.testing.assert_array_equal(a, b)

    def assertArrayAlmostEqual(self, a, b, *args, **kwargs):
        return np.testing.assert_array_almost_equal(a, b, *args, **kwargs)


class GraphicsTest(TephiTest):
    def tearDown(self):
        # If a plotting test bombs out it can leave the current figure in an
        # odd state, so we make sure it's been disposed of.
        plt.close()

    def check_graphic(self):
        """
        Check the hash of the current matplotlib figure matches the expected
        image hash for the current graphic test.

        To create missing image test results, set the TEPHI_TEST_CREATE_MISSING
        environment variable before running the tests. This will result in new
        and appropriately "<hash>.png" image files being generated in the image
        output directory, and the imagerepo.json file being updated.

        """
        import imagehash
        from PIL import Image

        dev_mode = os.environ.get("TEPHI_TEST_CREATE_MISSING")
        unique_id = self._unique_id()
        repo_fname = os.path.join(_RESULT_PATH, "imagerepo.json")
        repo = {}
        if os.path.isfile(repo_fname):
            with open(repo_fname, "rb") as fi:
                repo = json.load(codecs.getreader("utf-8")(fi))

        try:
            #: The path where the images generated by the tests should go.
            image_output_directory = os.path.join(
                os.path.dirname(__file__), "result_image_comparison"
            )
            if not os.access(image_output_directory, os.W_OK):
                if not os.access(os.getcwd(), os.W_OK):
                    raise IOError(
                        "Write access to a local disk is required "
                        "to run image tests.  Run the tests from a "
                        "current working directory you have write "
                        "access to to avoid this issue."
                    )
                else:
                    image_output_directory = os.path.join(
                        os.getcwd(), "tephi_image_test_output"
                    )
            result_fname = os.path.join(
                image_output_directory, "result-" + unique_id + ".png"
            )

            if not os.path.isdir(image_output_directory):
                # Handle race-condition where the directories are
                # created sometime between the check above and the
                # creation attempt below.
                try:
                    os.makedirs(image_output_directory)
                except OSError as err:
                    # Don't care about "File exists"
                    if err.errno != 17:
                        raise

            def _create_missing():
                fname = f"{phash}.png"
                uri = os.path.join(BASE_URL, fname)
                hash_fname = os.path.join(image_output_directory, fname)
                uris = repo.setdefault(unique_id, [])
                uris.append(uri)
                print(f"Creating image file: {hash_fname}")
                figure.savefig(hash_fname)
                msg = "Creating imagerepo entry: {} -> {}"
                print(msg.format(unique_id, uri))
                lock = filelock.FileLock(
                    os.path.join(_RESULT_PATH, "imagerepo.lock")
                )
                # The imagerepo.json file is a critical resource, so ensure
                # thread safe read/write behaviour via platform independent
                # file locking.
                with lock.acquire(timeout=600):
                    with open(repo_fname, "wb") as fo:
                        json.dump(
                            repo,
                            codecs.getwriter("utf-8")(fo),
                            indent=4,
                            sort_keys=True,
                        )

            # Calculate the test result perceptual image hash.
            buffer = io.BytesIO()
            figure = plt.gcf()
            figure.savefig(buffer, format="png")
            buffer.seek(0)
            phash = imagehash.phash(Image.open(buffer), hash_size=_HASH_SIZE)

            if unique_id not in repo:
                if dev_mode:
                    _create_missing()
                else:
                    figure.savefig(result_fname)
                    emsg = "Missing image test result: {}."
                    raise AssertionError(emsg.format(unique_id))
            else:
                uris = repo[unique_id]
                # Extract the hex basename strings from the uris.
                hexes = [
                    os.path.splitext(os.path.basename(uri))[0] for uri in uris
                ]
                # Create the expected perceptual image hashes from the uris.
                to_hash = imagehash.hex_to_hash
                expected = [to_hash(uri_hex) for uri_hex in hexes]

                # Calculate hamming distance vector for the result hash.
                distances = [e - phash for e in expected]

                if np.all([hd > _HAMMING_DISTANCE for hd in distances]):
                    if dev_mode:
                        _create_missing()
                    else:
                        figure.savefig(result_fname)
                        msg = (
                            "Bad phash {} with hamming distance {} "
                            "for test {}."
                        )
                        msg = msg.format(phash, distances, unique_id)
                        if _DISPLAY_FIGURES:
                            emsg = "Image comparison would have failed: {}"
                            print(emsg.format(msg))
                        else:
                            emsg = "Image comparison failed: {}"
                            raise AssertionError(emsg.format(msg))

            if _DISPLAY_FIGURES:
                plt.show()

        finally:
            plt.close()
