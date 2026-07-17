#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор карт Идиотов для Мечи и Идиоты v2
Карта разделена верх/низ: рыцарь | оруженосец
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"D:\mod the tts\tts_mod\card_images"
BACK_DIR = r"D:\mod the tts\tts_mod\back_images"

W, H = 300, 420
HALF = H // 2

IDIOTS = {
    'Детина': {
        'cost': 1, 'color': (100, 70, 50),
        'knight': 'Впервые за бой\nполучая травму,\nсразу сбросьте её.',
        'squire': 'Кладите на 1\nусталость меньше\nв колоду.',
    },
    'Голубокровка': {
        'cost': 3, 'color': (70, 110, 160),
        'knight': 'Делая выводы,\nкладите карту\nна верх своей\nколоды.',
        'squire': 'За 1 усилие\nположите карту\nпод низ колоды,\nвместо сброса.',
    },
    'Буквоед': {
        'cost': 4, 'color': (50, 90, 50),
        'knight': 'нет',
        'squire': '+1 усилие',
    },
    'Похититель кур': {
        'cost': 2, 'color': (160, 100, 50),
        'knight': 'Положите 2\nПодражания\nв колоду.',
        'squire': 'Положите 1\nОтход в колоду.',
    },
    'Большун': {
        'cost': 2, 'color': (100, 100, 100),
        'knight': 'Первая ваша\nтравма не приносит\nэффекта.',
        'squire': 'Положите 1\nБлок в колоду.',
    },
    'Чароплюй': {
        'cost': 3, 'color': (80, 90, 130),
        'knight': 'Положите 2\nЧары в колоду.',
        'squire': 'Положите 1\nКонцентрацию\nв колоду.',
    },
    'Герой из провинции': {
        'cost': 3, 'color': (60, 120, 60),
        'knight': 'Когда у вас\nдве травмы, вы\nполучаете +1\nк серии',
        'squire': 'Если рыцарь должен\nотъехать, вместо\nнего отъезжает\nГерой.',
    },
    'Монашка': {
        'cost': 3, 'color': (140, 130, 110),
        'knight': 'Положите 2\nКонцентрации\nв колоду',
        'squire': '+1 усилие',
    },
    'Зверюга': {
        'cost': 1, 'color': (90, 60, 40),
        'knight': 'Положите 2\nУкуса в колоду.',
        'squire': 'нет',
    },
    'Начинающий злодей': {
        'cost': 3, 'color': (130, 40, 40),
        'knight': 'Когда вы впервые\nза бой ранены,\nзамешайте\nусталость врагу',
        'squire': 'Положите 1\nПодлость\nв колоду',
    },
    'Пьянчуга': {
        'cost': 2, 'color': (170, 110, 40),
        'knight': 'Положите 2\nДопинга в колоду',
        'squire': 'Один раз за бой\nвы можете отменить\nсброс вашихкарт\nв ходу',
    },
    'Нагадатель': {
        'cost': 2, 'color': (50, 70, 120),
        'knight': 'Выкладывая серию,\nтяните на 1 карту\nбольше. После\nвыберите одну\nи замешайте\nобратно.',
        'squire': 'Получая травму,\nвыбирайте 1\nиз двух.',
    },
    'Любитель кустов': {
        'cost': 3, 'color': (50, 100, 70),
        'knight': 'Положите 1\nСила леса\nв колоду.',
        'squire': 'Положите 1\nЗасаду в колоду.',
    },
    'Карга': {
        'cost': 1, 'color': (80, 60, 40),
        'knight': 'Положите 2\nПроклятия\nв колоду.',
        'squire': 'Соперник кладёт\nна 1 усталость\nбольше, когда\nутомляется',
    },
    'Царёк': {
        'cost': 2, 'color': (120, 60, 140),
        'knight': 'Первая ваша\nтравма за бой\nпереносится\nна оруженосца',
        'squire': 'Когда становится\nрыцарем, может\nвыбрать одного\nиз трёх\nоруженосцев.',
    },
    '5риключатель': {
        'cost': 3, 'color': (100, 80, 120),
        'knight': '(улучшение\nмеждворчного\nвзаимодействия\nв обмен\nна травму)',
        'squire': 'Когда становится\nрыцарем, отправьте\nверхнего\nоруженосца\nв зал бесславья.',
    },
    'Готяночка': {
        'cost': 3, 'color': (130, 80, 100),
        'knight': 'Положите 1\nПроклятие и 1\nУкол в колоду.',
        'squire': 'Когда становится\nрыцарем, выбирает\nоруженосца\nиз зала\nбесславья',
    },
    'Мстюн': {
        'cost': 3, 'color': (150, 40, 40),
        'knight': 'Положите 2\nЯрости\nв колоду.',
        'squire': 'Когда становится\nрыцарем, убивает\nоруженосца\nсоперника.\nОн может сразу\nвыбрать нового.',
    },
}

ASCII_MAP = {
    'Детина': 'detina', 'Голубокровка': 'golubokrovka', 'Буквоед': 'bukvoed',
    'Похититель кур': 'pohititel_kur', 'Большун': 'bolshun',
    'Чароплюй': 'charoplyuy', 'Герой из провинции': 'geroy_provincii',
    'Монашка': 'monashka', 'Зверюга': 'zveryuga',
    'Начинающий злодей': 'nachinayushchiy_zlodey',
    'Пьянчуга': 'punchuga', 'Нагадатель': 'nagadatel',
    'Любитель кустов': 'lyubitel_kustov', 'Карга': 'karga',
    'Царёк': 'tsarek', '5риключатель': 'pyatikluchatel',
    'Готяночка': 'golyanochka', 'Мстюн': 'mstyun',
}


def _get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("arialbd.ttf", size)
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()


def _text_w(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def _draw_centered(draw, text, cx, y, font, fill, outline=None):
    tw = _text_w(text, font)
    x = cx - tw // 2
    if outline:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    draw.text((x + dx, y + dy), text, fill=outline, font=font)
    draw.text((x, y), text, fill=fill, font=font)


def create_idiot_face(name, info):
    img = Image.new('RGB', (W, H), (30, 30, 35))
    draw = ImageDraw.Draw(img)

    font_name = _get_font(18, bold=True)
    font_label = _get_font(14, bold=True)
    font_desc = _get_font(13)

    color = info['color']
    lighter = tuple(min(255, c + 40) for c in color)
    cx = W // 2

    # === ВЕРХ — РЫЦАРЬ ===
    draw.rectangle([0, 0, W, HALF - 1], fill=color)
    draw.rectangle([3, 3, W - 4, HALF - 4], outline=lighter, width=2)

    _draw_centered(draw, 'РЫЦАРЬ', cx, 8, font_label, lighter, (0, 0, 0))
    _draw_centered(draw, name, cx, 28, font_name, (255, 255, 255), (0, 0, 0))

    # Мозги
    cost = info['cost']
    brain_size = 12
    gap = 4
    total_w = cost * brain_size + (cost - 1) * gap
    x_start = (W - total_w) // 2
    y_brain = 53
    for i in range(cost):
        bx = x_start + i * (brain_size + gap)
        draw.ellipse([bx, y_brain, bx + brain_size, y_brain + brain_size],
                     fill=(220, 180, 60), outline=(180, 140, 30), width=1)
        draw.line([(bx + brain_size // 2, y_brain + 2),
                   (bx + brain_size // 2, y_brain + brain_size - 2)],
                  fill=(180, 140, 30), width=1)

    lines = info['knight'].split('\n')
    line_h = 16
    total_h = len(lines) * line_h
    y_start = HALF - 10 - total_h
    for i, line in enumerate(lines):
        tw = _text_w(line, font_desc)
        draw.text(((W - tw) // 2, y_start + i * line_h), line, fill=(255, 255, 255), font=font_desc)

    # === НИЗ — ОРУЖЕНОСЕЦ ===
    draw.rectangle([0, HALF, W, H - 3], fill=(30, 30, 35))
    draw.rectangle([3, HALF + 3, W - 4, H - 4], outline=lighter, width=2)

    squire_lines = info['squire'].split('\n')
    y_start = HALF + 15
    for i, line in enumerate(squire_lines):
        tw = _text_w(line, font_desc)
        draw.text(((W - tw) // 2, y_start + i * line_h), line, fill=(255, 255, 255), font=font_desc)

    _draw_centered(draw, name, cx, H - 48, font_name, (255, 255, 255), (0, 0, 0))
    _draw_centered(draw, 'ОРУЖЕНОСЕЦ', cx, H - 24, font_label, lighter, (0, 0, 0))

    lower = img.crop((0, HALF, W, H))
    lower = lower.rotate(180)
    img.paste(lower, (0, HALF))

    return img


def create_idiot_back():
    img = Image.new('RGB', (W, H), (45, 40, 50))
    draw = ImageDraw.Draw(img)

    for y in range(0, H, 25):
        for x in range(0, W, 25):
            c = (55, 50, 60) if (x // 25 + y // 25) % 2 == 0 else (45, 40, 50)
            draw.rectangle([x, y, x + 24, y + 24], fill=c)

    draw.rectangle([4, 4, W - 5, H - 5], outline=(100, 90, 110), width=3)
    draw.rectangle([8, 8, W - 9, H - 9], outline=(70, 65, 80), width=2)

    cx, cy = W // 2, H // 2 - 30
    font_face = _get_font(60)
    font_text = _get_font(28, bold=True)

    draw.text((cx - 50, cy - 40), '^', fill=(180, 170, 140), font=font_face)
    draw.text((cx + 20, cy - 40), '^', fill=(180, 170, 140), font=font_face)
    draw.text((cx - 25, cy + 20), '_', fill=(180, 170, 140), font=font_face)

    _draw_centered(draw, 'ИДИОТ', cx, H - 60, font_text, (120, 110, 130))

    return img


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(BACK_DIR, exist_ok=True)

    back = create_idiot_back()
    back.save(os.path.join(BACK_DIR, 'back_idiot.png'))
    print('Рубашка: back_idiot.png')

    for name, info in IDIOTS.items():
        img = create_idiot_face(name, info)
        ascii_name = ASCII_MAP[name]
        img.save(os.path.join(OUTPUT_DIR, f'{ascii_name}.png'))
        print(f'  {name}.png')

    print(f'\nИдиотов: {len(IDIOTS)}')


if __name__ == '__main__':
    main()
