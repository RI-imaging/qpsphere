"""Fetch BHFIELD binaries from GitHub"""
import contextlib
import hashlib
import os
import pathlib
from pkg_resources import resource_filename
import platform
import stat
import urllib

import appdirs

CACHE_DIR = appdirs.AppDirs(appname="python-qpsphere").user_cache_dir
RESRC_DIR = resource_filename("qpsphere", "resources")


EXE_STD = "bhfield-std.exe"
EXE_ARP = "bhfield-arp.exe"

DL_REPO = "https://github.com/RI-imaging/QPI-binaries/raw/" \
          + "d2af4117917ade389958e105d36446830b404fe7" \
          + "/BHFIELD"

BHFIELD_MD5 = {"Windows": {
    "bhfield-std.exe": "673415a9d49cc4ae0bdcd2da7b78802a",
    "bhfield-arp.exe": "75d4b592a000944c947b7133996c9a4c",
},
    "Linux": {
    "bhfield-std.exe": "5141ca8101023b35288f1eeef9ab6ae5",
    "bhfield-arp.exe": "843a802dc822251f8a4b4505f2152619",
},
}


class BinaryNotAvailableError(BaseException):
    """Raised if the BHFIELD binary is not available for the current platform
    """
    pass


class BinaryMD5SumCheckError(BaseException):
    """Raised when the downloaded binary does not have the correct md5sum
    """
    pass


def download_binary(url, dest, md5, retries=3):
    print("qpimage: Downloading '{}', please wait.".format(dest.name))
    for rr in range(retries):
        if dest.exists():
            os.remove(str(dest))
        try:
            urlretrieve(url, dest)
        except BaseException:
            print("qpimage: Download of {} failed ({}/{})".format(url,
                                                                  rr + 1,
                                                                  retries))
            continue
        else:
            break
    else:
        # Let the user see the error message
        urlretrieve(url, dest)

    # verify binary
    if md5sum(dest) != md5:
        msg = "MD5 sum of {} does not match {}!".format(dest, md5)
        raise BinaryMD5SumCheckError(msg)


def get_download_root():
    plat = platform.system()
    if plat == "Windows":
        path = "{}/{}".format(DL_REPO.strip("/"), "bin_win")
    elif plat == "Linux":
        path = "{}/{}".format(DL_REPO.strip("/"), "bin_linux")
    else:
        msg = "BHFIELD currently unavailable for platform '{}'!".format(plat)
        raise BinaryNotAvailableError(msg)
    return path


def get_binary(arp=False):
    plat = platform.system()
    dl_root = get_download_root()
    if arp:
        exe = EXE_ARP
    else:
        exe = EXE_STD

    # check if file is in resources directory
    res_path = pathlib.Path(RESRC_DIR) / exe
    if res_path.exists():
        ret_binary = res_path
    else:
        # download from GitHub
        ret_binary = pathlib.Path(CACHE_DIR) / exe
        url = "{}/{}".format(dl_root, exe)
        md5 = BHFIELD_MD5[plat][exe]

        if (not ret_binary.exists() or
                not md5sum(ret_binary) == md5):

            download_binary(url=url, dest=ret_binary, md5=md5)

    # make sure file is executable
    st = ret_binary.stat()
    ret_binary.chmod(st.st_mode | stat.S_IEXEC)
    return ret_binary


def get_binaries():
    """Download and return paths of all platform-specific binaries"""
    paths = []
    for arp in [False, True]:
        paths.append(get_binary(arp=arp))
    return paths


def md5sum(binary, blocksize=65536):
    hasher = hashlib.md5()
    with binary.open(mode="rb") as fd:
        buf = fd.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fd.read(blocksize)
    return hasher.hexdigest()


def urlretrieve(url, dest):
    # create destination directory
    dest.parent.mkdir(parents=True, exist_ok=True)
    # begin download
    with dest.open(mode="wb") as out_file:
        with contextlib.closing(urllib.request.urlopen(str(url))) as fp:
            block_size = 1024 * 8
            while True:
                block = fp.read(block_size)
                if not block:
                    break
                out_file.write(block)
