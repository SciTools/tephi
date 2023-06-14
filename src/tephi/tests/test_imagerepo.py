# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""
Test that imagerepo.json reconciles with the images registered in the
test-tephi-imagehash repository.

"""
# Import tephi tests first so that some things can be initialised before
# importing anything else
import tephi.tests as tests

import codecs
import itertools
import json
import os
import pytest

import requests


IMAGE_MANIFEST = (
    "https://raw.githubusercontent.com/SciTools/"
    "test-tephi-imagehash/gh-pages/image_manifest.txt"
)


@tests.requires_inet
class TestImageRepoJSON:
    def test(self):
        response = requests.get(IMAGE_MANIFEST)

        emsg = 'Failed to download "image_manifest.txt"'
        assert response.status_code == requests.codes.ok, emsg

        image_manifest = response.content.decode("utf-8")
        image_manifest = [line.strip() for line in image_manifest.split("\n")]
        image_manifest_uris = set(
            os.path.join(tests.BASE_URL, fname) for fname in image_manifest
        )

        imagerepo_fname = os.path.join(
            os.path.dirname(__file__), "results", "imagerepo.json"
        )
        with open(imagerepo_fname, "rb") as fi:
            imagerepo = json.load(codecs.getreader("utf-8")(fi))

        # "imagerepo" maps key: list-of-uris. Put all the uris in one big set.
        tests_uris = set(itertools.chain.from_iterable(imagerepo.values()))

        missing = list(tests_uris - image_manifest_uris)
        count = len(missing)
        if count:
            emsg = (
                '"imagerepo.json" references {} image URIs that are not '
                'listed in "{}":\n\t'
            )
            emsg = emsg.format(count, IMAGE_MANIFEST)
            emsg += "\t".join(uri for uri in missing)
            pytest.fail(emsg)
