from ctypes import cdll
import ctypes.util


VersionUnknown = 0
VersionEqual = 1
VersionLess = 2
VersionGreater = 4
VersionFuzzy = 8


# Try to load libapk with different strategies
libapk = None
for lib_name in ['libapk.so.2.14.0', 'libapk.so', 'apk']:
    try:
        libapk = cdll.LoadLibrary(lib_name)
        break
    except OSError:
        pass

# Try using ctypes.util.find_library as fallback
if libapk is None:
    lib_path = ctypes.util.find_library('apk')
    if lib_path:
        libapk = cdll.LoadLibrary(lib_path)

if libapk is None:
    raise OSError(
        "Could not load libapk. Make sure apk-tools is installed and "
        "libapk.so is available in the library path."
    )


def do_compare(ver1: str, ver2: str, ops: int):
    return (libapk.apk_version_compare(ver1.encode('ascii'), ver2.encode('ascii')) & ops) == ops


def do_compare_fuzzy(ver1: str, ver2: str, ops: int):
    return (libapk.apk_version_compare(ver1.encode('ascii'), ver2.encode('ascii')) & ops) != 0


class APKVersion:
    def __init__(self, version: str):
        self.version = version

    def __repr__(self):
        return f'<APKVersion {self.version}>'

    def __eq__(self, other):
        return do_compare(self.version, other.version, VersionEqual)

    def __ne__(self, other):
        return not do_compare(self.version, other.version, VersionEqual)

    def __lt__(self, other):
        return do_compare(self.version, other.version, VersionLess)

    def __le__(self, other):
        return do_compare_fuzzy(self.version, other.version, VersionLess | VersionEqual)

    def __gt__(self, other):
        return do_compare(self.version, other.version, VersionGreater)

    def __ge__(self, other):
        return do_compare_fuzzy(self.version, other.version, VersionGreater | VersionEqual)