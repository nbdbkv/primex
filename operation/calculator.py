def calculatePrice(weight, hight, lenght, width, volume, townLocation, areaLocation, envelop):
    price = 0
    if hight <= 20 and lenght <= 20 and width <= 20:
        if weight <= 1:
            if townLocation == 'Ош' or townLocation == 'Жалал Абад':
                price = 200
            else:
                price = 250
        if weight > 1:
            if townLocation == 'Ош' or townLocation == 'Жалал Абад':
                price = 200 + ((weight - 1) * 12)
            else:
                price = 250 + ((weight - 1) * 12)

    elif hight <= 30 and lenght <= 30 and width <= 30:
        if weight <= 5:
            if townLocation == 'Ош' or townLocation == 'Жалал Абад':
                price = 250
            else:
                price = 280
        if weight > 5:
            if townLocation == 'Ош' or townLocation == 'Жалал Абад':
                price = 250 + ((weight - 5) * 12)
            else:
                price = 280 + ((weight - 5) * 12)
    if envelop != 'NULL':
        price += envelopePrice(townLocation, areaLocation,  envelop)
    return price

def envelopePrice(location, arealocation, envelope):
    price = 0
    if envelope == 'c5':
        if location == 'Ош' or location=='Жалал Абад' or arealocation == 'Шамалды Сай':
            price = 150
        else:
            price = 200
    if envelope == 'c4':
        if location == 'Ош' or location == 'Жалал Абад':
            price = 200
        else:
            price = 250
    if envelope == 'c3':
        if location == 'Ош' or location == 'Жалал Абад':
            price = 250
        else:
            price = 280
    return price


