import hashlib
from decimal import Decimal, getcontext
import inspect
import os
from dotenv import load_dotenv
import requests

load_dotenv()


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
        "secret": os.getenv("CASHBOX_SECRET"),
        "amount": Decimal("1234.00"),
        "parcel_code": "02016bf49e59ab8",
    }
    hash1 = get_hash(data)
    print(hash1)

    response = requests.post(
        "https://api.doce.kg/payment/optima/",
        data={
            "amount": "1234.00",
            "operation_id": "123",
            "parcel_code": "02016bf49e59ab8",
            "sha1_hash": hash1,
        },
    )
    print(response.connection)
