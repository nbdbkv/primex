import hashlib
from decimal import Decimal, getcontext
import inspect


def get_hash(data: dict) -> str:
    data = [i[1] for i in sorted(data.items())]
    obj_str = "&".join(map(str, data))
    print(obj_str)
    hash1 = hashlib.sha1(bytes(obj_str, "utf-8"))
    pbhash = hash1.hexdigest()
    return pbhash


if __name__ == "__main__":
    data = {
        "operation_id": "123",
        "secret": "804c7624029744988d892b163fdd0362",
        "amount": Decimal("1234.00"),
        "parcel_code": "0202014ce049999",
    }
    hash1 = get_hash(data)
    print(hash1)

    def hel(x):
        return x

    print(inspect.getargspec(hel))
