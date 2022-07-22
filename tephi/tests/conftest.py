# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""pytest configuration"""

import matplotlib.pyplot as plt
import pytest


@pytest.fixture
def close_plot():
    """This fixture closes the current matplotlib plot associated with the graphical test."""
    yield
    plt.close()


@pytest.fixture
def nodeid(request):
    """This fixture returns the unique test name for the method.

    Constructs the nodeid, which is composed of the test module name,
    class name, and method name.

    Parameters
    ----------
    request : fixture
        pytest built-in fixture providing information of the requesting
        test function.

    Returns
    -------
    str
        The test nodeid consisting of the module, class and test name.

    """
    root = request.fspath.basename.split(".")[0]
    klass = request.cls.__name__
    func = request.node.name
    return ".".join([root, klass, func])
