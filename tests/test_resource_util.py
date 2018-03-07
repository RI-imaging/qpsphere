import pathlib
import shutil
import tempfile

from qpsphere import util


def copy_to_safe():
    """Move all binary files to a temporary folder"""
    # This does not require an internet connection if all
    # the files are already present in the cache or
    # resource directory.
    paths = util.download_binaries(package_dir=False)
    dtemp = tempfile.mkdtemp(prefix="qpsphere-resources_")
    for pp in paths:
        shutil.copy2(str(pp), dtemp)
    return pathlib.Path(dtemp)


def copy_restore(dtemp):
    """Restore all files to user cache dir and delete dtemp"""
    for pp in dtemp.iterdir():
        pp.rename(util.CACHE_PATH / pp.name)
    dtemp.rmdir()


def test_move_to_resources_and_priority():
    dtemp = copy_to_safe()
    # remove all files from package directory
    util.remove_binaries(package_dir=True)
    # test that resource directory contains no binaries
    nf = [pp for pp in util.RESCR_PATH.iterdir()]
    # only one file: "shipped_resources_go_here"
    assert len(nf) == 1
    # download binaries to package directory
    paths = util.download_binaries(package_dir=True)
    # test whether package directory contains binaries
    assert len(paths)
    # test whether binaries in package directroy get
    # highest priority
    paths2 = util.download_binaries(package_dir=False)
    for pp in paths2:
        assert pp == util.RESCR_PATH / pp.name
    # remove the files from the resource directory
    util.remove_binaries(package_dir=True)
    paths3 = util.download_binaries(package_dir=False)
    for pp in paths3:
        assert pp == util.CACHE_PATH / pp.name
    # populate resources dir and remove cache dir
    paths = util.download_binaries(package_dir=True)
    util.remove_binaries(package_dir=False)
    paths4 = util.download_binaries(package_dir=False)
    for pp in paths4:
        assert pp == util.RESCR_PATH / pp.name
    for pp in paths3:
        assert not pp.exists()
    # cleanup
    util.remove_binaries(package_dir=True)
    copy_restore(dtemp)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
