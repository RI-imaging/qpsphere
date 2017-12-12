from qpsphere.models import _bhfield as bh


def test_get_binary():
    path1 = bh.fetch.get_binary(arp=False)
    path2 = bh.fetch.get_binary(arp=True)
    assert path1.exists()
    assert path2.exists()


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
