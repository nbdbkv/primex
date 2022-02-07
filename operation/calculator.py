def calculatePrice(weight, hight, lenght, width, townLocation, areaLocation, envelop):
    price = 0
    townLocation = townLocation.__str__()
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
    location = location.__str__()
    if envelope == 'c5':
        if location == 'Ош' or location == 'Жалал Абад' or arealocation == 'Шамалды Сай':
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

def deliveryTime(town, area):
    time = ''
    if town == 'Ош':
        time = osh(area)
    if town == 'Жалал Абад':
        time = jalalabad(area)
    if town == 'Баткен':
        time = batken(area)
    if town == 'Иссык Куль':
        time = yssyk_kyl(area)
    return time

def osh(areaLocation):
    time = ''
    if areaLocation == 'Даарот-Коргон':
        time = '36'
    else:
        time = '24'
    return time

def jalalabad(areaLocation):
    time = ''
    if areaLocation == 'Кербен' or areaLocation == 'Кок-Жангак'  or  areaLocation == 'Ала-Бука':
        time = '36'
    elif areaLocation == 'Ала Бука' or areaLocation == 'Чаткан':
        time = '24-48'
    else:
        time = '24'
    return time

def batken(areaLocation):
    time = ''
    if areaLocation == 'Исфана':
        time = '36-48'
    else:
        time = '36'

def yssyk_kyl(areaLocation):
    return '24'

def generateCode(town, area):
    towns = {
        'Бишкек':'01',
        'Ош':'02',
        'Баткен': '03',
        'Жалал Абад' : '04',
        'Нарын': '05',
        'Алай': '06'
    }
    areas = {
        'Октябрьский': '01' ,
        'Первомайский': '02',
        'Ленинский': '03',
        'Свердловский': '04',

        #OSH
        'ХБК-Ош район': '01',
        'Западный' : '02',
        'Ак-Тилек': '02',
        'Учар': '03',
        'Толойкон': '03',
        'Дом-Быта-Озгур' : '04',
        'Озгон': '06',

        #batken
        'Баткен' : '01',
        'Исфана': '02',
        'Сулукту': '03',
        'Кадамжай': '04',
        'Кызыл Кыя': '05',

        #Jalalabad
        'Жалал Абад' : '0001',
        'Жалал Абад': '0002',
        'Аксы-Кербен': '01',
        'Майлы-Суу': '0101',
        'Таш Комур': '0102',
        'Шамалды Сай': '0103',
        'Ала–Бука': '02',
        'Базар Коргон': '03',
        'Ноокен': '04',
        'КочкорАта':'0401',
        'Сузак': '05',
        'ТогузТоро': '06',
        'Казарман': '06',
        'Токтогул': '07',
        'Чаткал' : '08',
        'Каныш кыя': '08',

        #naryn
        'Нарын': '01',
        'Ак Талаа': '02',
        'Баетов': '03',
        'Ат Башы': '03',
        'Жумгал': '04',
        'Чаек': '04',
        'Кочкор': '05',

        #alay
        'Алай': '01',
        'Араван': '02',
        'Кара-Кулжа': '03',

    }
    code = ''

    return code