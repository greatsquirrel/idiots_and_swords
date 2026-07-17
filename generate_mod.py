#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор TTS save файла — Мечи и Идиоты v2
"""

import json
import uuid
import os

ALL_CARDS = {
    'Удар':            {'id': 1,  'desc': 'Атака'},
    'Сокрушение':      {'id': 2,  'desc': 'Атака. Когда эта карта должна отмениться, вместо этого сбросьте карту'},
    'Блок':            {'id': 3,  'desc': 'Защита / Восстановите усилие'},
    'Парирование':     {'id': 4,  'desc': 'Главная. Защита. Если отменили, переверните эту карту. / Атака 1'},
    'Уклонение':       {'id': 5,  'desc': 'Приём. Сбросьте эту карту и выбранную карту из вражеской серии. Вытяните новые взамен.'},
    'Финт':            {'id': 6,  'desc': 'Приём. Скопируйте эффект карты атаки или защиты из вашей серии.'},
    'Отход':           {'id': 7,  'desc': 'Приём. Ваш рыцарь не получает в этот ход больше 1 ранения / Статус.'},
    'Чары':            {'id': 8,  'desc': 'Атака / Защита'},
    'Концентрация':    {'id': 9,  'desc': 'Защита. Восстановите усилие'},
    'Подлость':        {'id': 10, 'desc': 'Атака. Сбросьте усилие врага'},
    'Допинг':          {'id': 11, 'desc': 'Приём. Сбросьте эту карту. Вытяните две карты.'},
    'Барьер':          {'id': 12, 'desc': 'Защита. Применяется дважды.'},
    'Вспышка':         {'id': 13, 'desc': 'Приём. Статус. Соперник может активировать эту карту, чтобы получить Защита.'},
    'Укол':            {'id': 14, 'desc': 'Атака. Если ранили врага, замешайте усталость в его колоду.'},
    'Казнь':           {'id': 15, 'desc': 'Атака. Если враг получил вторую травму, он отъехал.'},
    'Подсечка':        {'id': 16, 'desc': 'Атака. Если ранили врага, он сбрасывает верхнюю карту из колоды.'},
    'Комбо':           {'id': 17, 'desc': 'Главная. Атака. Можете потратить усилие, чтобы перевернуть. / Атака. Наносит ранение дважды.'},
    'Уход в тень':     {'id': 18, 'desc': 'Защита. Можете потратить усилие, чтобы вытянуть карту.'},
    'Насмешка':        {'id': 19, 'desc': 'Приём. Отмените защиту врага.'},
    'Засада':          {'id': 31, 'desc': 'Атака. Отмените приём врага. Делается вне очереди.'},
    'Размашистый удар':{'id': 32, 'desc': 'Атака. Нанесите ранение оруженосцу врага.'},
    'Подражание':      {'id': 33, 'desc': 'Приём. Выложите вытяните карту из колоды соперника.'},
    'Ярость':          {'id': 34, 'desc': 'Атака. Если у вас есть травма, применяется дважды'},
    'Проклятие':       {'id': 35, 'desc': 'Приём. Статус. Если вы ранили врага, ваш рыцарь получает ранение.'},
    'Выстрел':         {'id': 36, 'desc': 'Атака. Отмените атаку.'},
    'Пируэт':          {'id': 37, 'desc': 'Главная. Атака. Если эту карту отменяют, вместо этого переверните её. / Приём. Не отменяется. Вытяните ещё одну карту.'},
    'Милость божья':   {'id': 20, 'desc': 'Защита. Сбросьте травму с рыцаря. Эту карту нельзя брать из сброса.'},
    'Укус':            {'id': 21, 'desc': 'Атака. Не отменяется'},
    'Удар Грааля':     {'id': 22, 'desc': 'Атака. Вытяните карту. Если это усталость, выкиньте её из колоды.'},
    'Шторм':           {'id': 23, 'desc': 'Приём. Статус. Вы можете активировать эту карту, чтобы получить Атака.'},
    'Подчинение':      {'id': 24, 'desc': 'Приём. Активируйте карту вражеской серии как свою.'},
    'Сила леса':       {'id': 38, 'desc': 'Защита. Статус. Отмените ранение и сбросьте эту карту.'},
    'Осушение':        {'id': 39, 'desc': 'Атака. Если нанесли ранение, снимите одно ранение у себя.'},
    'Временной сдвиг': {'id': 40, 'desc': 'Приём. Вы и враг замешиваете серии в свои колоды. Ход начинается заново / Замешайте эту карту в колоду, вытяните карту.'},
    'Взрыв':           {'id': 41, 'desc': 'Атака. Применяется дважды. Все ранения по врагу наносятся так же его оруженосцу'},
    'Усталость':       {'id': 25, 'desc': 'Замешивается при перемешивании. Сбрасывает 1 карту сверху'},
    'Меч':             {'id': 26, 'desc': 'Абилка: За 1 УСИЛ отмените ПРОБ или ОТМЗАЩ соперника'},
    'Лук':             {'id': 27, 'desc': 'Абилка: Если ваш ПРОБ отменяется — вы получаете ЗАЩ'},
    'Секира':          {'id': 28, 'desc': 'Абилка: За 2 УСИЛ отмените карту приёма соперника'},
    'Копьё':           {'id': 29, 'desc': 'Абилка: В начале каждой серии сыграйте приём вне очереди'},
    'Палица':          {'id': 30, 'desc': 'Абилка: Нанеся ранение, за 1 УСИЛ заставьте цель сбросить карту'},
}

TITLES = {
    'Легендарный':      {'id': 42, 'desc': 'Когда вы выбираете оруженосца, выберите одного из четырёх'},
    'Божественный':     {'id': 43, 'desc': 'Положите в колоду 1 Милость божья'},
    'Вострый':          {'id': 44, 'desc': 'Если в серии нет карты Атаки, вытяните карту.'},
    'Гигантский':       {'id': 45, 'desc': 'Первая карта в серии не отменяется'},
    'Магический':       {'id': 46, 'desc': 'Положите в колоду 2 Чары и 2 Концентрации'},
    'Сверхзвуковой':    {'id': 47, 'desc': 'Положите в колоду 2 Допинга'},
    'Противотанковый':  {'id': 48, 'desc': 'После выкладывания серии можете отменить одну защиту врага'},
    'Электрический':    {'id': 49, 'desc': 'Нанося травму, вы раните оруженосца врага'},
    'Огненный':         {'id': 50, 'desc': 'Положите в колоду 2 Взрыва'},
    'Разумный':         {'id': 51, 'desc': '+2 усилия'},
    'Ужасный':          {'id': 52, 'desc': 'Добавляя усталость в колоду, враг добавляет на 1 больше'},
    'Псионический':     {'id': 53, 'desc': 'Положите в колоду 2 Подчинения'},
    'Хронотургический': {'id': 54, 'desc': 'Положите в колоду 1 Временной сдвиг'},
    'Короля':           {'id': 55, 'desc': 'Вы можете иметь двух оруженосцев сразу'},
    'Артура':           {'id': 56, 'desc': 'Положите в колоду 3 Удара Грааля'},
    'Титана':           {'id': 57, 'desc': 'Рыцарь отъезжает только получив третью травму.'},
    'Ужасов':           {'id': 58, 'desc': 'В начале боя замешайте 2 усталости в колоду врага'},
    'Ангела':           {'id': 59, 'desc': 'Положите 3 Вспышки в колоду'},
    'Джинна':           {'id': 60, 'desc': 'Сбросьте титул в начале любого боя. Возьмите 2 награды из пула наград'},
    'Зевса':            {'id': 61, 'desc': 'Положите 2 Шторма в колоду'},
    'Мастера':          {'id': 62, 'desc': 'Карты, взятые из сброса, кладутся сверху колоды'},
    'Лича':             {'id': 63, 'desc': 'Карта усталости в серии врага считается Атакой от вас'},
    'Хитреца':          {'id': 64, 'desc': 'Выложив серию, вы сразу можете поменять одну карту в ней.'},
}

IDIOTS = {
    'Детина':                {'id': 70, 'cost': 1, 'knight': 'Впервые за бой получая травму, сразу сбросьте её.', 'squire': 'Кладите на 1 усталость меньше в колоду.'},
    'Голубокровка':          {'id': 71, 'cost': 3, 'knight': 'Делая выводы, кладите карту на верх своей колоды.', 'squire': 'За 1 усилие положите карту под низ колоды, вместо сброса.'},
    'Буквоед':               {'id': 72, 'cost': 4, 'knight': 'нет', 'squire': '+1 усилие'},
    'Похититель кур':        {'id': 73, 'cost': 2, 'knight': 'Положите 2 Подражания в колоду.', 'squire': 'Положите 1 Отход в колоду.'},
    'Большун':               {'id': 74, 'cost': 2, 'knight': 'Первая ваша травма не приносит эффекта.', 'squire': 'Положите 1 Блок в колоду.'},
    'Чароплюй':              {'id': 75, 'cost': 3, 'knight': 'Положите 2 Чары в колоду.', 'squire': 'Положите 1 Концентрацию в колоду.'},
    'Герой из провинции':    {'id': 76, 'cost': 3, 'knight': 'Когда у вас две травмы, вы получаете +1 к серии', 'squire': 'Если рыцарь должен отъехать, вместо него отъезжает Герой.'},
    'Монашка':               {'id': 77, 'cost': 3, 'knight': 'Положите 2 Концентрации в колоду', 'squire': '+1 усилие'},
    'Зверюга':               {'id': 78, 'cost': 1, 'knight': 'Положите 2 Укуса в колоду.', 'squire': 'нет'},
    'Начинающий злодей':     {'id': 79, 'cost': 3, 'knight': 'Когда вы впервые за бой ранены, замешайте усталость врагу', 'squire': 'Положите 1 Подлость в колоду'},
    'Пьянчуга':              {'id': 80, 'cost': 2, 'knight': 'Положите 2 Допинга в колоду', 'squire': 'Один раз за бой вы можете отменить сброс ваших карт в ходу'},
    'Нагадатель':            {'id': 81, 'cost': 2, 'knight': 'Выкладывая серию, тяните на 1 карту больше. После выберите одну карту и замешайте её обратно.', 'squire': 'Получая травму, выбирайте 1 из двух.'},
    'Любитель кустов':       {'id': 82, 'cost': 3, 'knight': 'Положите 1 Сила леса в колоду.', 'squire': 'Положите 1 Засаду в колоду.'},
    'Карга':                 {'id': 83, 'cost': 1, 'knight': 'Положите 2 Проклятия в колоду.', 'squire': 'Соперник кладёт на 1 усталость больше, когда утомляется'},
    'Царёк':                 {'id': 84, 'cost': 2, 'knight': 'Первая ваша травма за бой переносится на оруженосца', 'squire': 'Когда становится рыцарем, может выбрать одного из трёх оруженосцев.'},
    '5риключатель':          {'id': 85, 'cost': 3, 'knight': '(чё-то на улучшение междрачного взамодействия в обмен на травму)', 'squire': 'Когда становится рыцарем, отправьте верхнего оруженосца в зал бесславья.'},
    'Готяночка':             {'id': 86, 'cost': 3, 'knight': 'Положите 1 Проклятие и 1 Укол в колоду.', 'squire': 'Когда становится рыцарем, выбирает оруженосца из зала бесславья'},
    'Мстюн':                 {'id': 87, 'cost': 3, 'knight': 'Положите 2 Ярости в колоду.', 'squire': 'Когда становится рыцарем, убивает оруженосца соперника. Он может сразу выбрать нового.'},
}

BASIC_CARDS = {
    'Удар': 8, 'Сокрушение': 4, 'Блок': 4, 'Парирование': 2,
    'Уклонение': 2, 'Финт': 2, 'Отход': 2,
}

NONBASIC_CARDS = {
    'Чары': 4, 'Концентрация': 4, 'Подлость': 4, 'Допинг': 4,
    'Барьер': 4, 'Вспышка': 4, 'Укол': 4, 'Казнь': 2,
    'Подсечка': 4, 'Комбо': 4, 'Уход в тень': 4, 'Насмешка': 4,
    'Засада': 3, 'Размашистый удар': 2, 'Подражание': 2,
    'Ярость': 2, 'Проклятие': 2, 'Выстрел': 2, 'Пируэт': 2,
}

UNIQUE_CARDS = {
    'Милость божья': 2, 'Укус': 2, 'Удар Грааля': 1, 'Шторм': 2,
    'Подчинение': 2, 'Сила леса': 1, 'Осушение': 2,
    'Временной сдвиг': 1, 'Взрыв': 1,
}

WEAPONS = {
    'Меч':    {'cards': {'Удар': 3, 'Сокрушение': 1, 'Блок': 2, 'Парирование': 2, 'Финт': 1, 'Уклонение': 1}},
    'Лук':    {'cards': {'Удар': 5, 'Уклонение': 2, 'Финт': 1, 'Отход': 2}},
    'Секира': {'cards': {'Удар': 3, 'Сокрушение': 3, 'Блок': 3, 'Уклонение': 1}},
    'Копьё':  {'cards': {'Удар': 3, 'Сокрушение': 2, 'Блок': 2, 'Уклонение': 1, 'Отход': 2}},
    'Палица': {'cards': {'Удар': 4, 'Сокрушение': 2, 'Блок': 2, 'Уклонение': 1, 'Отход': 1}},
}

TRAUMAS = {
    'Сломанное ребро':  {'id': 65, 'desc': '-1 К следующей серии'},
    'Грусть':           {'id': 66, 'desc': 'Сбросьте две верхние карты'},
    'Головокружение':   {'id': 67, 'desc': '-1 усилие мозгов (максимальное и текущее)'},
    'Обида':            {'id': 68, 'desc': '+1 к следующей серии врага'},
    'Истощение':        {'id': 69, 'desc': 'Замешайте 2 карты усталости в колоду'},
    'Пьянство':         {'id': 70, 'desc': 'связанное с междудрачьем'},
    'Рукоприкладство':  {'id': 71, 'desc': 'Нанесите 1 ранение оруженосцу'},
}

GITHUB_RAW = "https://raw.githubusercontent.com/greatsquirrel/idiots_and_swords/main"
CARD_IMAGES_DIR = GITHUB_RAW + "/card_images"
TITLE_IMAGES_DIR = GITHUB_RAW + "/title_images"
BACK_DIR = GITHUB_RAW + "/back_images"

V = "?v=7"

CARD_BACK = BACK_DIR + "/card_back.png" + V
TITLE_BACK = BACK_DIR + "/title_back.png" + V

WEAPON_BACKS = {
    'Меч':    BACK_DIR + "/back_mech.png" + V,
    'Лук':    BACK_DIR + "/back_luk.png" + V,
    'Секира': BACK_DIR + "/back_sekira.png" + V,
    'Копьё':  BACK_DIR + "/back_kopyo.png" + V,
    'Палица': BACK_DIR + "/back_palitsa.png" + V,
}

IDIOT_BACK = BACK_DIR + "/back_idiot.png" + V
TRAUMA_BACK = BACK_DIR + "/back_trauma.png" + V

ASCII_MAP = {
    'Удар': 'udar', 'Сокрушение': 'sokrushenie', 'Блок': 'blok',
    'Парирование': 'parirovanie', 'Уклонение': 'uklonenie', 'Финт': 'fint',
    'Отход': 'otkhod', 'Чары': 'chary', 'Концентрация': 'kontsentratsiya',
    'Подлость': 'podlost', 'Допинг': 'doping', 'Барьер': 'barer',
    'Вспышка': 'vspyshka', 'Укол': 'ukol', 'Казнь': 'kazn',
    'Подсечка': 'podsechka', 'Комбо': 'kombo', 'Уход в тень': 'ukhod_v_ten',
    'Насмешка': 'nasmeshka', 'Засада': 'zasada',
    'Размашистый удар': 'razmashisty_udar', 'Подражание': 'podrazhanie',
    'Ярость': 'yarost', 'Проклятие': 'proklyatie', 'Выстрел': 'vystrel',
    'Пируэт': 'piruet',
    'Милость божья': 'milost_bozhya', 'Укус': 'ukus',
    'Удар Грааля': 'udar_graalya', 'Шторм': 'shtorm', 'Подчинение': 'podchinene',
    'Сила леса': 'sila_lesa', 'Осушение': 'osushenie',
    'Временной сдвиг': 'vremennoy_sdvig', 'Взрыв': 'vzryv',
    'Усталость': 'ustalost', 'Меч': 'mech', 'Лук': 'luk', 'Секира': 'sekira',
    'Копьё': 'kopyo', 'Палица': 'palitsa',
    'Легендарный': 'legendarny', 'Божественный': 'bozhestvenny',
    'Вострый': 'vostry', 'Гигантский': 'gigantsky', 'Магический': 'magichesky',
    'Сверхзвуковой': 'sverkhzvukovoy', 'Противотанковый': 'protivotankovy',
    'Электрический': 'elektrichesky', 'Огненный': 'ognenny',
    'Разумный': 'razumny', 'Ужасный': 'uzhasny', 'Псионический': 'psionichesky',
    'Хронотургический': 'khronoturgichesky', 'Короля': 'korolya',
    'Артура': 'artura', 'Титана': 'titana', 'Ужасов': 'uzhasov',
    'Ангела': 'angela', 'Джинна': 'dzhinna', 'Зевса': 'zevsa',
    'Мастера': 'mastera', 'Лича': 'licha', 'Хитреца': 'khitretsa',
    'Детина': 'detina', 'Голубокровка': 'golubokrovka', 'Буквоед': 'bukvoed',
    'Похититель кур': 'pohititel_kur', 'Большун': 'bolshun',
    'Чароплюй': 'charoplyuy', 'Герой из провинции': 'geroy_provincii',
    'Монашка': 'monashka', 'Зверюга': 'zveryuga',
    'Начинающий злодей': 'nachinayushchiy_zlodey', 'Пьянчуга': 'punchuga',
    'Нагадатель': 'nagadatel', 'Любитель кустов': 'lyubitel_kustov',
    'Карга': 'karga', 'Царёк': 'tsarek',
    '5риключатель': 'pyatikluchatel', 'Готяночка': 'golyanochka', 'Мстюн': 'mstyun',
    'Сломанное ребро': 'slomannoe_rebro', 'Грусть': 'grust',
    'Головокружение': 'golovokrujene', 'Обида': 'obida',
    'Пьянство': 'pyanstvo', 'Истощение': 'ischerpanie',
    'Рукоприкладство': 'rukoprikladstvo',
}


def make_guid():
    return uuid.uuid4().hex[:12].upper()


def make_card_image_url(card_name):
    ascii_name = ASCII_MAP.get(card_name, card_name)
    return f"{CARD_IMAGES_DIR}/{ascii_name}.png{V}"


def make_title_image_url(title_name):
    ascii_name = ASCII_MAP.get(title_name, title_name)
    return f"{TITLE_IMAGES_DIR}/{ascii_name}.png{V}"


def make_card(card_name, card_id):
    info = ALL_CARDS.get(card_name, {'desc': ''})
    return {
        'GUID': make_guid(),
        'Name': 'Card',
        'CardID': card_id,
        'Nickname': card_name,
        'Description': info.get('desc', ''),
        'XML': '',
        'LuaScript': '',
        'Transform': {}
    }


def make_title_card(title_name, title_id):
    info = TITLES.get(title_name, {'desc': ''})
    return {
        'GUID': make_guid(),
        'Name': 'Card',
        'CardID': title_id,
        'Nickname': title_name,
        'Description': info.get('desc', ''),
        'XML': '',
        'LuaScript': '',
        'Transform': {}
    }


def make_deck(nickname, cards_dict, position, description='', scale=1, back_url=None, weapon_backs=None, bottom_cards=None):
    contained = []
    deck_ids = []
    custom_deck = {}
    bottom_contained = []
    bottom_deck_ids = []

    if back_url is None:
        back_url = CARD_BACK
    if bottom_cards is None:
        bottom_cards = []

    for card_name, count in cards_dict.items():
        info = ALL_CARDS.get(card_name)
        if not info:
            continue

        base_id = info['id']
        deck_key = str(base_id)
        card_id = base_id * 100

        if deck_key not in custom_deck:
            face_url = make_card_image_url(card_name)
            if weapon_backs and card_name in weapon_backs:
                card_back = weapon_backs[card_name]
            else:
                card_back = back_url
            custom_deck[deck_key] = {
                'FaceURL': face_url,
                'BackURL': card_back,
                'NumWidth': 1,
                'NumHeight': 1,
                'BackIsHidden': True,
                'UniqueBack': False
            }

        card_obj = make_card(card_name, card_id)
        if card_name in bottom_cards:
            for _ in range(count):
                bottom_contained.append(card_obj)
                bottom_deck_ids.append(card_id)
        else:
            for _ in range(count):
                contained.append(card_obj)
                deck_ids.append(card_id)

    bottom_contained.extend(contained)
    bottom_deck_ids.extend(deck_ids)
    contained = bottom_contained
    deck_ids = bottom_deck_ids

    return {
        'GUID': make_guid(),
        'Name': 'DeckCustom',
        'IsHidden': True,
        'Transform': {
            'posX': position[0], 'posY': position[1], 'posZ': position[2],
            'rotX': 0, 'rotY': 180, 'rotZ': 180,
            'scaleX': scale, 'scaleY': scale, 'scaleZ': scale
        },
        'Nickname': nickname,
        'Description': description,
        'CustomDeck': custom_deck,
        'DeckIDs': deck_ids,
        'ContainedObjects': contained
    }


def make_title_deck(nickname, titles_dict, position, description=''):
    contained = []
    deck_ids = []
    custom_deck = {}

    for title_name, count in titles_dict.items():
        info = TITLES.get(title_name)
        if not info:
            continue

        base_id = info['id']
        deck_key = str(base_id)
        title_id = base_id * 100

        if deck_key not in custom_deck:
            face_url = make_title_image_url(title_name)
            custom_deck[deck_key] = {
                'FaceURL': face_url,
                'BackURL': TITLE_BACK,
                'NumWidth': 1,
                'NumHeight': 1,
                'BackIsHidden': True,
                'UniqueBack': False
            }

        for _ in range(count):
            contained.append(make_title_card(title_name, title_id))
            deck_ids.append(title_id)

    return {
        'GUID': make_guid(),
        'Name': 'DeckCustom',
        'IsHidden': True,
        'Transform': {
            'posX': position[0], 'posY': position[1], 'posZ': position[2],
            'rotX': 0, 'rotY': 180, 'rotZ': 180,
            'scaleX': 0.28, 'scaleY': 0.28, 'scaleZ': 0.28
        },
        'Nickname': nickname,
        'Description': description,
        'CustomDeck': custom_deck,
        'DeckIDs': deck_ids,
        'ContainedObjects': contained
    }


def make_idiot_deck(nickname, position, description=''):
    contained = []
    deck_ids = []
    custom_deck = {}

    for idiot_name, info in IDIOTS.items():
        base_id = info['id']
        deck_key = str(base_id)
        idiot_id = base_id * 100

        if deck_key not in custom_deck:
            ascii_name = ASCII_MAP.get(idiot_name, idiot_name)
            face_url = f"{CARD_IMAGES_DIR}/{ascii_name}.png{V}"
            custom_deck[deck_key] = {
                'FaceURL': face_url,
                'BackURL': IDIOT_BACK,
                'NumWidth': 1,
                'NumHeight': 1,
                'BackIsHidden': True,
                'UniqueBack': False
            }

        desc = f"Оруженосец: {info['squire']}\nРыцарь: {info['knight']}"
        contained.append({
            'GUID': make_guid(),
            'Name': 'Card',
            'CardID': idiot_id,
            'Nickname': idiot_name,
            'Description': desc,
            'XML': '',
            'LuaScript': '',
            'Transform': {}
        })
        deck_ids.append(idiot_id)

    return {
        'GUID': make_guid(),
        'Name': 'DeckCustom',
        'IsHidden': True,
        'Transform': {
            'posX': position[0], 'posY': position[1], 'posZ': position[2],
            'rotX': 0, 'rotY': 180, 'rotZ': 180,
            'scaleX': 1, 'scaleY': 1, 'scaleZ': 1
        },
        'Nickname': nickname,
        'Description': description,
        'CustomDeck': custom_deck,
        'DeckIDs': deck_ids,
        'ContainedObjects': contained
    }


def make_trauma_deck(nickname, position, description=''):
    contained = []
    deck_ids = []
    custom_deck = {}

    for trauma_name, info in TRAUMAS.items():
        base_id = info['id']
        deck_key = str(base_id)
        trauma_id = base_id * 100

        if deck_key not in custom_deck:
            ascii_name = ASCII_MAP.get(trauma_name, trauma_name)
            face_url = f"{CARD_IMAGES_DIR}/{ascii_name}.png{V}"
            custom_deck[deck_key] = {
                'FaceURL': face_url,
                'BackURL': TRAUMA_BACK,
                'NumWidth': 1,
                'NumHeight': 1,
                'BackIsHidden': True,
                'UniqueBack': False
            }

        contained.append({
            'GUID': make_guid(),
            'Name': 'Card',
            'CardID': trauma_id,
            'Nickname': trauma_name,
            'Description': info['desc'],
            'XML': '',
            'LuaScript': '',
            'Transform': {}
        })
        deck_ids.append(trauma_id)

    return {
        'GUID': make_guid(),
        'Name': 'DeckCustom',
        'IsHidden': True,
        'Transform': {
            'posX': position[0], 'posY': position[1], 'posZ': position[2],
            'rotX': 0, 'rotY': 180, 'rotZ': 180,
            'scaleX': 0.7, 'scaleY': 0.7, 'scaleZ': 0.7
        },
        'Nickname': nickname,
        'Description': description,
        'CustomDeck': custom_deck,
        'DeckIDs': deck_ids,
        'ContainedObjects': contained
    }


def generate_mod():
    print("Генерация TTS мода v8...")

    objects = []

    objects.append(make_deck(
        'Базовые карты', BASIC_CARDS, [-2, 1, 0],
        'Удар, Сокрушение, Блок, Парирование, Уклонение, Финт, Отход'
    ))

    objects.append(make_deck(
        'Небазовые карты', NONBASIC_CARDS, [0, 1, 0],
        'Чары, Концентрация, Подлость, Допинг, Барьер и др.'
    ))

    objects.append(make_deck(
        'Уникальные карты', UNIQUE_CARDS, [2, 1, 0],
        'Милость божья, Укус, Удар Грааля, Шторм, Подчинение и др.'
    ))

    objects.append(make_deck(
        'Колода усталости', {'Усталость': 10}, [4, 1, 0],
        'Замешивается при перемешивании'
    ))

    weapon_positions = [
        [-5, 1, -3], [-5, 1, -1], [-5, 1, 1], [-5, 1, 3], [-5, 1, 5]
    ]
    for i, (weapon_name, weapon_info) in enumerate(WEAPONS.items()):
        pos = weapon_positions[i % len(weapon_positions)]
        cards_with_title = dict(weapon_info['cards'])
        cards_with_title[weapon_name] = 1
        wb = {weapon_name: WEAPON_BACKS.get(weapon_name, CARD_BACK)}
        objects.append(make_deck(
            f'Оружие: {weapon_name}', cards_with_title, pos,
            f'Стартовая колода: {weapon_name}',
            weapon_backs=wb, bottom_cards=[weapon_name]
        ))

    title_cards = {name: 1 for name in TITLES.keys()}
    objects.append(make_title_deck('Титулы', title_cards, [0, 1, 6], 'Префиксы и постфиксы'))

    objects.append(make_idiot_deck('Идиоты', [0, 1, 8], 'Оруженосец / Рыцарь — переверните карту'))

    objects.append(make_trauma_deck('Травмы', [6, 1, 0], 'Сломанное ребро, Грусть, Головокружение, Обида, Пьянство, Рукоприкладство'))

    token_face = BACK_DIR + "/token_slabak.png" + V
    objects.append({
        'GUID': make_guid(),
        'Name': 'CustomToken',
        'Transform': {
            'posX': 0, 'posY': 1, 'posZ': -2,
            'rotX': 0, 'rotY': 180, 'rotZ': 180,
            'scaleX': 1.5, 'scaleY': 1, 'scaleZ': 1.5
        },
        'Nickname': 'Жетон слабака',
        'Description': 'Сбросьте жетон чтобы сбросить 1 травму.',
        'CustomToken': {
            'FaceURL': token_face,
            'BackURL': token_face,
            'BackIsHidden': True
        },
        'States': {}
    })

    lua_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Lua', 'Global.lua')
    global_lua = ''
    if os.path.exists(lua_path):
        with open(lua_path, 'r', encoding='utf-8') as f:
            global_lua = f.read()

    save_data = {
        'SaveName': 'Мечи и Идиоты',
        'GameMode': 'None',
        'ObjectStates': objects,
        'LuaScript': global_lua,
        'LuaScriptState': ''
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mod.save')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f'Сохранено: {output_path}')
    print(f'Объектов: {len(objects)}')
    return output_path


if __name__ == '__main__':
    generate_mod()
