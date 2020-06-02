# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""pytest configuration"""

import matplotlib.pyplot as plt
import pytest


@pytest.fixture
def close_plot():
    """
    This fixture closes the matplotlib plot for a graphical test.

    """
    yield
    plt.close()


@pytest.fixture
def nodeid(request):
    """
    This fixture returns the unique test name.

    """
    root = request.fspath.basename.split(".")[0]
    klass = request.cls.__name__
    func = request.node.name
    return f"{root}.{klass}.{func}"
