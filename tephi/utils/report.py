# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""Platform and package dependency reporting."""

import os
from subprocess import check_output, CalledProcessError

import scooby


class CondaInfo:
    """
    Internal helper class to provision conda and conda environment
    metadata.

    """

    def __init__(self):
        self._path = None

    @property
    def version(self):
        result = "Unknown"
        if self._path is not None:
            with open(os.devnull, "w") as null:
                command = ["conda", "--version"]
                try:
                    result = check_output(command, stderr=null)
                    result = result.decode("utf-8").split(" ")[1].strip()
                except CalledProcessError:
                    pass
        return result

    @property
    def name(self):
        result = "Unknown"
        if self._path is not None:
            result = os.environ.get("CONDA_DEFAULT_ENV", "base")
        return result

    @property
    def packages(self):
        result = "Unknown"
        if self._path is not None:
            with open(os.devnull, "w") as null:
                command = ["conda", "list", "-n", self.name, "--explicit"]
                try:
                    result = check_output(command, stderr=null)
                    lines = result.decode("utf-8").split("\n")
                    lines = sorted(
                        [
                            line
                            for line in lines
                            if not (
                                line.startswith("#") or line.startswith("@")
                            )
                            and line
                        ]
                    )
                    result = "\n\t{}".format("\n\t".join(lines))
                except CalledProcessError:
                    pass
        return result

    def get_info(self):
        self._path = os.environ.get("CONDA_EXE", None)
        return (
            (self.version, "Conda Version"),
            (self.name, "Conda Environment"),
            (self.packages, "Conda Packages"),
        )


class Report(scooby.Report):
    """
    Generate a :class:`scooby.Report` of platform and package dependencies.

    Parameters
    ----------
    additional : list of ModuleType, list of str, optional
        List of packages or package names to add to output information.
    ncol : int, optional
        Number of package-columns in HTML table. Has no effect in text-version
        (default is 3).
    text_width : int, optional
        The text width for non-HTML display modes (default is 80).
    sort : bool, optional
        Sort the packages when the report is shown (default is False).
    conda : bool, optional
        Gather information about conda (default is False).

    """

    def __init__(
        self, additional=None, ncol=3, text_width=80, sort=False, conda=False
    ):
        # Mandatory packages.
        core = ["tephi", "matplotlib", "numpy", "scipy"]

        # Gather conda information.
        if conda:
            extra_meta = CondaInfo().get_info()
        else:
            extra_meta = None

        super().__init__(
            additional=additional,
            core=core,
            ncol=ncol,
            text_width=text_width,
            sort=sort,
            extra_meta=extra_meta,
        )
