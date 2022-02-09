from account.models import Region, City, District

from uuid import uuid4


def get_parcel_code(direction: dict) -> str:
    city = direction.get('city')
    code = city.region.code + city.code
    if district := direction.get('district'):
        code += district.code
    code += str(uuid4())[:15-len(code)]
    return code
    
