import appdirs
import pathlib
from pkg_resources import resource_filename
import shutil

from .models import _bhfield

#: User's cache directory
CACHE_PATH = pathlib.Path(
    appdirs.AppDirs(appname="python-qpsphere").user_cache_dir)
#: Qpsphere package `resources` directory.
RESCR_PATH = pathlib.Path(resource_filename("qpsphere", "resources"))


def download_binaries(package_dir=False):
    """Download all binaries for the current platform

    Parameters
    ----------
    package_dir: bool
        If set to `True`, the binaries will be downloaded to the
        `resources` directory of the qpsphere package instead of
        to the users application data directory. Note that this
        might require administrative rights if qpsphere is installed
        in a system directory.

    Returns
    -------
    paths: list of pathlib.Path
        List of paths to binaries. This will always return binaries in
        the `resources` directory of the qpsphere package (if binaries
        are present there), in disregard of the parameter `package_dir`.
    """
    # bhfield
    # make sure the binary is available on the system
    paths = _bhfield.fetch.get_binaries()

    if package_dir:
        # Copy the binaries to the `resources` directory
        # of qpsphere.
        pdir = RESCR_PATH
        outpaths = []
        for pp in paths:
            target = pdir / pp.name
            if not target.exists():
                shutil.copy(str(pp), str(target))
            outpaths.append(target)
    else:
        outpaths = paths

    return outpaths


def remove_binaries(package_dir=False):
    """Remove all binaries for the current platform

    Parameters
    ----------
    package_dir: bool
        If True, remove all binaries from the `resources`
        directory of the qpsphere package. If False,
        remove all binaries from the user's cache directory.
    """
    paths = []

    if package_dir:
        pdir = RESCR_PATH
    else:
        pdir = CACHE_PATH

    for pp in pdir.iterdir():
        if pp.name != "shipped_resources_go_here":
            paths.append(pp)

    for pp in paths:
        pp.unlink()
