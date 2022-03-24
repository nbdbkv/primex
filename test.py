import hashlib
from decimal import Decimal, getcontext


def get_hash(data: dict) -> str:
    data = [i[1] for i in sorted(data.items())]
    obj_str = "&".join(map(str, data))
    print(obj_str)
    hash1 = hashlib.sha1(bytes(obj_str, "utf-8"))
    pbhash = hash1.hexdigest()
    return pbhash


if __name__ == "__main__":
    getcontext().prec = 2
    data = {
        "operation_id": 123,
        "secret": "804c7624029744988d892b163fdd0362",
        "amount": Decimal("1234.00"),
        "parcel_code": "string",
    }
    hash1 = get_hash(data)
    print(hash1)
