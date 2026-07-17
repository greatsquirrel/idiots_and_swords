#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор изображений карт v2 — Мечи и Идиоты
2x resolution for crisp rendering in TTS
"""

from PIL import Image, ImageDraw, ImageFont
import os
import re
import numpy as np

SCALE = 2
CARD_W, CARD_H = 300 * SCALE, 420 * SCALE
HALF = CARD_H // 2
TITLE_W, TITLE_H = 200 * SCALE, 105 * SCALE
TRAUMA_SIZE = 200 * SCALE

OUTPUT_DIR = r"D:\mod the tts\tts_mod\card_images"
TITLES_DIR = r"D:\mod the tts\tts_mod\title_images"
BACK_DIR = r"D:\mod the tts\tts_mod\back_images"

TYPE_STRIPE = {
    'Атака':  (200, 50, 50),
    'Защита': (50, 70, 200),
    'Приём':  (50, 160, 70),
}
TYPE_BODY = {
    'Атака':  (245, 225, 225),
    'Защита': (225, 225, 245),
    'Приём':  (225, 245, 225),
}

FORMAT_WORDS = {
    'ПРОБИТИЕ': {'fill': (220, 40, 40),  'stroke': (60, 0, 0)},
    'ПРОБ':     {'fill': (220, 40, 40),  'stroke': (60, 0, 0)},
    'ЗАЩ':      {'fill': (40, 80, 220),  'stroke': (0, 0, 60)},
    'ОТМЗАЩ':   {'fill': (220, 200, 40), 'stroke': (60, 40, 0)},
    'УСИЛ':     {'fill': (140, 50, 180), 'stroke': (40, 0, 60)},
    'Атака':    {'fill': (220, 80, 80),  'stroke': (60, 0, 0)},
    'Защита':   {'fill': (80, 100, 220), 'stroke': (0, 0, 60)},
    'Приём':    {'fill': (80, 180, 80),  'stroke': (0, 40, 0)},
}
_SORTED_FW = sorted(FORMAT_WORDS.keys(), key=len, reverse=True)

STRIP_KW = {'Атака', 'Защита', 'Приём', 'Главная'}

# (категория, текст_стороны_A, текст_стороны_B_or_None)
CARDS = {
    'Удар':            ('Базовая', 'Атака', None),
    'Сокрушение':      ('Базовая', 'Атака. Когда эта карта должна отмениться, вместо этого сбросьте карту', None),
    'Блок':            ('Базовая', 'Защита', 'Восстановите усилие'),
    'Парирование':     ('Базовая', 'Главная. Защита. Если отменили, переверните эту карту.', 'Атака 1'),
    'Уклонение':       ('Базовая', 'Приём. Сбросьте эту карту и выбранную карту из вражеской серии. Вытяните новые взамен.', None),
    'Финт':            ('Базовая', 'Приём. Скопируйте эффект карты атаки или защиты из вашей серии.', None),
    'Отход':           ('Базовая', 'Приём. Ваш рыцарь не получает в этот ход больше 1 ранения', 'Приём. Статус. В начале хода вы можете получить +1 к серии и сбросить эту карту.'),
    'Чары':            ('Особая', 'Атака', 'Защита'),
    'Концентрация':    ('Особая', 'Защита. Восстановите усилие', None),
    'Подлость':        ('Особая', 'Атака. Сбросьте усилие врага', None),
    'Допинг':          ('Особая', 'Приём. Сбросьте эту карту. Вытяните две карты.', None),
    'Барьер':          ('Особая', 'Защита. Применяется дважды.', None),
    'Вспышка':         ('Особая', 'Приём. Статус. Соперник может активировать эту карту, чтобы получить Защита.', None),
    'Укол':            ('Особая', 'Атака. Если ранили врага, замешайте усталость в его колоду.', None),
    'Казнь':           ('Особая', 'Атака. Если враг получил вторую травму, он отъехал.', None),
    'Подсечка':        ('Особая', 'Атака. Если ранили врага, он сбрасывает верхнюю карту из колоды.', None),
    'Комбо':           ('Особая', 'Главная. Атака. Можете потратить усилие, чтобы перевернуть.', 'Атака. Наносит ранение дважды.'),
    'Уход в тень':     ('Особая', 'Защита. Можете потратить усилие, чтобы вытянуть карту.', None),
    'Насмешка':        ('Особая', 'Приём. Отмените защиту врага.', None),
    'Засада':          ('Особая', 'Атака. Отмените приём врага. Делается вне очереди.', None),
    'Размашистый удар':('Особая', 'Атака. Нанесите ранение оруженосцу врага.', None),
    'Подражание':      ('Особая', 'Приём. Выложите вытяните карту из колоды соперника.', None),
    'Ярость':          ('Особая', 'Атака. Если у вас есть травма, применяется дважды', None),
    'Проклятие':       ('Особая', 'Приём. Статус. Если вы ранили врага, ваш рыцарь получает ранение.', None),
    'Выстрел':         ('Особая', 'Атака. Отмените атаку.', None),
    'Пируэт':          ('Особая', 'Главная. Атака. Если эту карту отменяют, вместо этого переверните её.', 'Приём. Не отменяется. Вытяните ещё одну карту.'),
    'Милость божья':   ('Уникальная', 'Защита. Сбросьте травму с рыцаря. Эту карту нельзя брать из сброса.', None),
    'Укус':            ('Уникальная', 'Атака. Не отменяется', None),
    'Удар Грааля':     ('Уникальная', 'Атака. Вытяните карту. Если это усталость, выкиньте её из колоды.', None),
    'Шторм':           ('Уникальная', 'Приём. Статус. Вы можете активировать эту карту, чтобы получить Атака.', None),
    'Подчинение':      ('Уникальная', 'Приём. Активируйте карту вражеской серии как свою.', None),
    'Сила леса':       ('Уникальная', 'Защита. Статус. Отмените ранение и сбросьте эту карту.', None),
    'Осушение':        ('Уникальная', 'Атака. Если нанесли ранение, снимите одно ранение у себя.', None),
    'Временной сдвиг': ('Уникальная', 'Приём. Вы и враг замешиваете серии в свои колоды. Ход начинается заново', 'Приём. Замешайте эту карту в колоду, вытяните карту.'),
    'Взрыв':           ('Уникальная', 'Атака. Применяется дважды. Все ранения по врагу наносятся так же его оруженосцу', None),
    'Усталость':       ('Усталость', 'Замешивается при перемешивании. Сбрасывает 1 карту сверху', None),
}

TWO_SIDED = {'Блок', 'Парирование', 'Чары', 'Отход', 'Комбо', 'Пируэт', 'Временной сдвиг'}

TITLES = {
    'Легендарный':      'Когда вы выбираете\nоруженосца, выберите\nодного из четырёх',
    'Божественный':     'Положите в колоду\n1 Милость божья',
    'Вострый':          'Если в серии нет\nкарты Атаки,\nвытяните карту.',
    'Гигантский':       'Первая карта\nв серии\nне отменяется',
    'Магический':       'Положите в колоду\n2 Чары\nи 2 Концентрации',
    'Сверхзвуковой':    'Положите в колоду\n2 Допинга',
    'Противотанковый':  'После выкладывания\nсерии можете\nотменить одну\nзащиту врага',
    'Электрический':    'Нанося травму,\nвы раните\nоруженосца врага',
    'Огненный':         'Положите в колоду\n2 Взрыва',
    'Разумный':         '+2 усилия',
    'Ужасный':          'Добавляя усталость\nв колоду, враг\nдобавляет на 1\nбольше',
    'Псионический':     'Положите в колоду\n2 Подчинения',
    'Хронотургический': 'Положите в колоду\n1 Временной сдвиг',
    'Короля':           'Вы можете иметь\nдвух оруженосцев\nсразу',
    'Артура':           'Положите в колоду\n3 Удара Грааля',
    'Титана':           'Рыцарь отъезжает\nтолько получив\nтретью травму.',
    'Ужасов':           'В начале боя\nзамешайте 2\nусталости\nв колоду врага',
    'Ангела':           'Положите\n3 Вспышки\nв колоду',
    'Джинна':           'Сбросьте титул\nв начале любого боя.\nВозьмите 2 награды\nиз пула наград',
    'Зевса':            'Положите в колоду\n2 Шторма',
    'Мастера':          'Карты, взятые\nиз сброса,\nкладутся сверху\nколоды',
    'Лича':             'Карта усталости\nв серии врага\nсчитается Атакой\nот вас',
    'Хитреца':          'Выложив серию,\nвы сразу можете\nпоменять одну\nкарту в ней.',
}

TRAUMAS = {
    'Сломанное ребро':  {'desc': '-1 К следующей\nсерии',           'color': (80, 50, 50)},
    'Грусть':           {'desc': 'Сбросьте две\nверхние карты',     'color': (50, 50, 80)},
    'Головокружение':   {'desc': '-1 усилие мозгов\n(макс. и текущее)', 'color': (60, 60, 50)},
    'Обида':            {'desc': '+1 к следующей\nсерии врага',     'color': (70, 50, 60)},
    'Истощение':        {'desc': 'Замешайте 2\nкарты усталости\nв колоду', 'color': (90, 85, 80)},
    'Пьянство':         {'desc': 'связанное с\nмеждудрачьем',       'color': (70, 60, 40)},
    'Рукоприкладство':  {'desc': 'Нанесите 1\nранение\nоруженосцу', 'color': (85, 55, 55)},
}


def _get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("arialbd.ttf", size)
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()


def _draw_noise_rect(img, x0, y0, w, h, base_color, sigma=8):
    arr = np.full((h, w, 3), base_color, dtype=np.int16)
    noise = np.random.normal(0, sigma, (h, w, 3)).astype(np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    bg = Image.fromarray(arr, 'RGB')
    img.paste(bg, (x0, y0))


def _text_w(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def _get_side_type(text):
    for kw in ('Атака', 'Защита', 'Приём'):
        if text.startswith(kw):
            return kw
    if text.startswith('Главная.'):
        rest = text[len('Главная.'):].lstrip()
        for kw in ('Атака', 'Защита', 'Приём'):
            if rest.startswith(kw):
                return kw
    return None


def _parse_text(text):
    parts = [p.strip() for p in text.split('.')]
    keywords = []
    effect = []
    for p in parts:
        if not p:
            continue
        clean = p.rstrip('.')
        if clean in STRIP_KW:
            keywords.append(clean)
        elif re.match(r'^(Атака|Защита|Приём)\s+\d+$', clean):
            keywords.append(clean)
        elif clean == 'Статус':
            keywords.append(clean)
        else:
            effect.append(p)
    return keywords, '. '.join(effect).strip('. ')


def _wrap(text, font, max_w):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test = ' '.join(cur + [w])
        if _text_w(test, font) <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(' '.join(cur))
            cur = [w]
    if cur:
        lines.append(' '.join(cur))
    return lines


def _find_first_kw(text):
    best_pos = len(text)
    best_kw = None
    for kw in _SORTED_FW:
        pos = text.find(kw)
        if pos != -1 and pos < best_pos:
            best_pos = pos
            best_kw = kw
    return best_kw, best_pos


def _calc_colored_w(text, font):
    kw, pos = _find_first_kw(text)
    if kw is None:
        return _text_w(text, font)
    w = 0
    if pos > 0:
        w += _text_w(text[:pos], font)
    w += _text_w(kw, font)
    if pos + len(kw) < len(text):
        w += _calc_colored_w(text[pos + len(kw):], font)
    return w


def _draw_outlined(draw, text, x, y, font, fill=(255,255,255), outline=(0,0,0), width=2):
    for dx in range(-width, width+1):
        for dy in range(-width, width+1):
            if dx or dy:
                draw.text((x+dx, y+dy), text, fill=outline, font=font)
    draw.text((x, y), text, fill=fill, font=font)


def _draw_colored(draw, text, x, y, font, stroke=(0,0,0)):
    kw, pos = _find_first_kw(text)
    if kw is None:
        _draw_outlined(draw, text, x, y, font, (255,255,255), (0,0,0), 2)
        return
    if pos > 0:
        _draw_outlined(draw, text[:pos], x, y, font, (255,255,255), (0,0,0), 2)
        x += _text_w(text[:pos], font)
    info = FORMAT_WORDS[kw]
    for dx in range(-2 * SCALE, 2 * SCALE + 1):
        for dy in range(-2 * SCALE, 2 * SCALE + 1):
            if dx * dx + dy * dy <= (3 * SCALE) * (3 * SCALE):
                draw.text((x + dx, y + dy), kw, fill=info['stroke'], font=font)
    draw.text((x, y), kw, fill=info['fill'], font=font)
    x += _text_w(kw, font)
    if pos + len(kw) < len(text):
        _draw_colored(draw, text[pos + len(kw):], x, y, font, stroke)


def _has_colored(text):
    return _find_first_kw(text)[0] is not None


def _draw_text_block(draw, text, x, y, w, font, stroke=(0,0,0)):
    lines = _wrap(text, font, w)
    line_h = font.size + 6 * SCALE
    for i, line in enumerate(lines):
        if _has_colored(line):
            cw = _calc_colored_w(line, font)
            lx = x + (w - cw) // 2
            _draw_colored(draw, line, lx, y + i * line_h, font)
        else:
            tw = _text_w(line, font)
            lx = x + (w - tw) // 2
            _draw_outlined(draw, line, lx, y + i * line_h, font, (255,255,255), (0,0,0), 2)
    return len(lines) * line_h


def _draw_icon(draw, icon_type, cx, cy, size, color):
    s = size // 2
    if icon_type == 'Атака':
        draw.line([(cx - s, cy + s), (cx, cy - s)], fill=color, width=3 * SCALE)
        draw.line([(cx, cy - s), (cx + s, cy + s)], fill=color, width=3 * SCALE)
        draw.line([(cx - s, cy - s // 2), (cx + s, cy - s // 2)], fill=color, width=2 * SCALE)
    elif icon_type == 'Защита':
        pts = [
            (cx, cy - s),
            (cx + s, cy - s // 3),
            (cx + int(s * 0.6), cy + s // 2),
            (cx, cy + s),
            (cx - int(s * 0.6), cy + s // 2),
            (cx - s, cy - s // 3),
        ]
        draw.polygon(pts, fill=color, outline=color)
    elif icon_type == 'Приём':
        draw.rectangle([cx - s // 3, cy - s, cx + s // 3, cy], fill=color, outline=color)
        draw.rectangle([cx - s // 3, cy, cx + s // 2, cy + s // 3], fill=color, outline=color)


def _draw_main_lines(draw, x, y, h):
    gap = 8 * SCALE
    lw = 4 * SCALE
    for offset in (0, gap):
        lx = x + offset
        draw.line([(lx, y), (lx, y + h)], fill=(0, 0, 0), width=lw + 4)
    for offset in (0, gap):
        lx = x + offset
        draw.line([(lx, y), (lx, y + h)], fill=(255, 200, 0), width=lw)


def _draw_activation(draw, cx, cy, r=14):
    r = r * SCALE
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 200, 40), outline=(180, 160, 30), width=2 * SCALE)
    fnt = _get_font(16 * SCALE)
    draw.text((cx, cy), 'А', fill=(0, 0, 0), font=fnt, anchor='mm')


def _render_half(img, draw, name, text, x0, y0, w, h, is_top, default_type='Атака'):
    kws, effect = _parse_text(text)
    stype = _get_side_type(text) or default_type
    stripe_color = TYPE_STRIPE.get(stype, (128, 128, 128))
    body_color = TYPE_BODY.get(stype, (230, 230, 230))

    stripe_h = 48 * SCALE
    if is_top:
        sy = y0
        by = y0 + stripe_h
        bh = h - stripe_h
    else:
        sy = y0
        by = y0 + stripe_h
        bh = h - stripe_h

    _draw_noise_rect(img, x0, by, w, bh, body_color, sigma=8)

    draw.rectangle([x0, sy, x0 + w, sy + stripe_h], fill=stripe_color)

    font_name = _get_font(20 * SCALE, bold=True)
    font_effect = _get_font(18 * SCALE)

    tw = _text_w(name, font_name)
    nx = x0 + (w - tw) // 2
    ny = sy + (stripe_h - 18 * SCALE) // 2
    _draw_outlined(draw, name, nx, ny, font_name, (255,255,255), (0,0,0), 2 * SCALE)

    _draw_icon(draw, stype, x0 + w - 26 * SCALE, sy + stripe_h // 2, 20 * SCALE, (255,255,255))

    if 'Главная' in kws:
        line_h = bh - 20 * SCALE
        line_y = by + 10 * SCALE
        if is_top:
            _draw_main_lines(draw, x0 + 10 * SCALE, line_y, line_h)
        else:
            _draw_main_lines(draw, x0 + w - 22 * SCALE, line_y, line_h)

    if effect:
        pad = 14 * SCALE
        _draw_text_block(draw, effect, x0 + pad, by + 10 * SCALE, w - pad * 2, font_effect, stripe_color)

    if 'Не отменяется' in text:
        fnt = _get_font(11 * SCALE)
        draw.text((x0 + w - 20 * SCALE, by + bh - 16 * SCALE), '\u2191', fill=(120, 40, 40), font=fnt)


def create_single_card(name, text):
    img = Image.new('RGB', (CARD_W, CARD_H), (240, 240, 240))
    draw = ImageDraw.Draw(img)

    kws, effect = _parse_text(text)
    stype = _get_side_type(text) or 'Атака'
    stripe_color = TYPE_STRIPE.get(stype, (128, 128, 128))
    body_color = TYPE_BODY.get(stype, (230, 230, 230))

    _draw_noise_rect(img, 0, 68 * SCALE, CARD_W, CARD_H - 68 * SCALE, body_color, sigma=8)
    draw.rectangle([0, 0, CARD_W, 68 * SCALE], fill=stripe_color)
    draw.rectangle([3 * SCALE, 3 * SCALE, CARD_W - 4 * SCALE, CARD_H - 4 * SCALE], outline=stripe_color, width=3 * SCALE)

    font_name = _get_font(26 * SCALE, bold=True)
    font_effect = _get_font(20 * SCALE)

    tw = _text_w(name, font_name)
    nx = (CARD_W - tw) // 2
    ny = 10 * SCALE
    _draw_outlined(draw, name, nx, ny, font_name, (255,255,255), (0,0,0), 2 * SCALE)

    _draw_icon(draw, stype, CARD_W - 32 * SCALE, 34 * SCALE, 24 * SCALE, (255,255,255))

    if effect:
        pad = 20 * SCALE
        _draw_text_block(draw, effect, pad, 88 * SCALE, CARD_W - pad * 2, font_effect, stripe_color)

    if 'Не отменяется' in text:
        fnt = _get_font(11 * SCALE)
        draw.text((CARD_W - 22 * SCALE, CARD_H - 20 * SCALE), '\u2191', fill=(120, 40, 40), font=fnt)

    return img


def create_double_card(name, text_a, text_b):
    img = Image.new('RGB', (CARD_W, CARD_H), (200, 200, 200))
    draw = ImageDraw.Draw(img)

    _render_half(img, draw, name, text_a, 0, 0, CARD_W, HALF, is_top=True)

    default_b = _get_side_type(text_a) or 'Атака'
    lower = Image.new('RGB', (CARD_W, HALF), (200, 200, 200))
    draw_lower = ImageDraw.Draw(lower)
    _render_half(lower, draw_lower, name, text_b, 0, 0, CARD_W, HALF, is_top=False, default_type=default_b)
    lower = lower.rotate(180)
    img.paste(lower, (0, HALF))

    draw.line([(0, HALF - 1), (CARD_W, HALF - 1)], fill=(100, 100, 100), width=2 * SCALE)

    return img


def create_fatigue_card():
    img = Image.new('RGB', (CARD_W, CARD_H), (90, 85, 80))
    draw = ImageDraw.Draw(img)
    draw.rectangle([4 * SCALE, 4 * SCALE, CARD_W - 5 * SCALE, CARD_H - 5 * SCALE], outline=(140, 130, 120), width=3 * SCALE)

    draw.rectangle([10 * SCALE, 10 * SCALE, CARD_W - 10 * SCALE, 75 * SCALE], fill=(60, 55, 50))
    font_title = _get_font(28 * SCALE, bold=True)
    tw = _text_w('УСТАЛОСТЬ', font_title)
    draw.text(((CARD_W - tw) // 2, 20 * SCALE), 'УСТАЛОСТЬ', fill=(200, 190, 170), font=font_title)

    cx, cy = CARD_W // 2, CARD_H // 2 - 10 * SCALE
    bw, bh = 60 * SCALE, 160 * SCALE
    draw.rectangle([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2],
                   fill=(140, 40, 40), outline=(180, 60, 60), width=2 * SCALE)
    draw.rectangle([cx - bh // 2, cy - bw // 2, cx + bh // 2, cy + bw // 2],
                   fill=(140, 40, 40), outline=(180, 60, 60), width=2 * SCALE)

    font_desc = _get_font(14 * SCALE)
    lines = ['Замешивается', 'при перемешивании', 'Сбрасывает 1 карту сверху']
    y_start = CARD_H - 120 * SCALE
    for i, line in enumerate(lines):
        tw = _text_w(line, font_desc)
        draw.text(((CARD_W - tw) // 2, y_start + i * 22 * SCALE), line, fill=(180, 170, 160), font=font_desc)

    return img


def create_title_card(name, description):
    img = Image.new('RGB', (TITLE_W, TITLE_H), (200, 170, 50))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2 * SCALE, 2 * SCALE, TITLE_W - 3 * SCALE, TITLE_H - 3 * SCALE], outline=(150, 120, 30), width=2 * SCALE)

    font_name = _get_font(14 * SCALE, bold=True)
    font_desc = _get_font(11 * SCALE)

    tw = _text_w(name, font_name)
    nx = (TITLE_W - tw) // 2
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                draw.text((nx + dx, 4 * SCALE + dy), name, fill=(20, 20, 20), font=font_name)
    draw.text((nx, 4 * SCALE), name, fill=(255, 255, 255), font=font_name)

    lines = description.split('\n')
    y_start = 26 * SCALE
    for i, line in enumerate(lines):
        tw = _text_w(line, font_desc)
        draw.text(((TITLE_W - tw) // 2, y_start + i * 16 * SCALE), line, fill=(40, 30, 10), font=font_desc)

    return img


def create_trauma_card(name, desc, color):
    img = Image.new('RGB', (TRAUMA_SIZE, TRAUMA_SIZE), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([3 * SCALE, 3 * SCALE, TRAUMA_SIZE - 4 * SCALE, TRAUMA_SIZE - 4 * SCALE], outline=(140, 40, 40), width=2 * SCALE)

    font_name = _get_font(18 * SCALE, bold=True)
    font_desc = _get_font(14 * SCALE)

    tw = _text_w(name, font_name)
    draw.text(((TRAUMA_SIZE - tw) // 2, 15 * SCALE), name, fill=(220, 180, 180), font=font_name)

    draw.line([(20 * SCALE, 45 * SCALE), (TRAUMA_SIZE - 20 * SCALE, 45 * SCALE)], fill=(140, 60, 60), width=1 * SCALE)

    lines = desc.split('\n')
    line_h = 20 * SCALE
    total_h = len(lines) * line_h
    y_start = (TRAUMA_SIZE - total_h) // 2 + 15 * SCALE
    for i, line in enumerate(lines):
        tw = _text_w(line, font_desc)
        draw.text(((TRAUMA_SIZE - tw) // 2, y_start + i * line_h), line, fill=(200, 200, 200), font=font_desc)

    return img


def create_card_back():
    w, h = CARD_W, CARD_H
    bg = (30, 25, 45)
    gold = (180, 150, 60)
    img = Image.new('RGB', (w, h), bg)
    draw = ImageDraw.Draw(img)

    step = 30 * SCALE
    for y_step in range(0, h, step):
        for x_step in range(0, w, step):
            c = tuple(min(255, c + 15) for c in bg)
            draw.polygon([(x_step + step // 2, y_step), (x_step + step, y_step + step // 2),
                          (x_step + step // 2, y_step + step), (x_step, y_step + step // 2)], outline=c)

    draw.rectangle([5 * SCALE, 5 * SCALE, w - 6 * SCALE, h - 6 * SCALE], outline=gold, width=3 * SCALE)
    draw.rectangle([10 * SCALE, 10 * SCALE, w - 11 * SCALE, h - 11 * SCALE], outline=gold, width=2 * SCALE)

    cx, cy = w // 2, 155 * SCALE
    s = SCALE
    shield_pts = [
        (cx, cy - 70 * s), (cx + 60 * s, cy - 45 * s), (cx + 50 * s, cy + 40 * s),
        (cx, cy + 70 * s), (cx - 50 * s, cy + 40 * s), (cx - 60 * s, cy - 45 * s),
    ]
    draw.polygon(shield_pts, fill=(120, 25, 25), outline=gold, width=2 * SCALE)

    draw.line([(cx, cy - 55 * s), (cx, cy + 50 * s)], fill=(200, 190, 170), width=4 * SCALE)
    draw.polygon([(cx - 5 * s, cy + 50 * s), (cx + 5 * s, cy + 50 * s), (cx, cy + 62 * s)], fill=(200, 190, 170))
    draw.ellipse([cx - 6 * s, cy - 62 * s, cx + 6 * s, cy - 50 * s], fill=gold, outline=gold)
    draw.line([(cx - 25 * s, cy - 20 * s), (cx + 25 * s, cy - 20 * s)], fill=gold, width=4 * SCALE)
    draw.rectangle([cx - 3 * s, cy - 20 * s, cx + 3 * s, cy + 10 * s], fill=(100, 70, 30))

    font = _get_font(26 * SCALE, bold=True)
    label = '\u041c\u0415\u0427\u0418 \u0418 \u0418\u0414\u0418\u041e\u0422\u042b'
    tw = _text_w(label, font)
    draw.text(((w - tw) / 2, 310 * SCALE), label, fill=gold, font=font)

    return img


def create_trauma_back():
    img = Image.new('RGB', (TRAUMA_SIZE, TRAUMA_SIZE), (40, 20, 20))
    draw = ImageDraw.Draw(img)
    draw.rectangle([3 * SCALE, 3 * SCALE, TRAUMA_SIZE - 4 * SCALE, TRAUMA_SIZE - 4 * SCALE], outline=(120, 40, 40), width=2 * SCALE)

    cx, cy = TRAUMA_SIZE // 2, TRAUMA_SIZE // 2
    bw, bh = 30 * SCALE, 80 * SCALE
    draw.rectangle([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2],
                   fill=(140, 40, 40), outline=(180, 60, 60), width=2 * SCALE)
    draw.rectangle([cx - bh // 2, cy - bw // 2, cx + bh // 2, cy + bw // 2],
                   fill=(140, 40, 40), outline=(180, 60, 60), width=2 * SCALE)

    font = _get_font(14 * SCALE)
    tw = _text_w('ТРАВМА', font)
    draw.text(((TRAUMA_SIZE - tw) // 2, TRAUMA_SIZE - 30 * SCALE), 'ТРАВМА', fill=(160, 80, 80), font=font)

    return img


ASCII_MAP = {
    'Удар': 'udar', 'Сокрушение': 'sokrushenie', 'Блок': 'blok',
    'Парирование': 'parirovanie', 'Уклонение': 'uklonenie', 'Финт': 'fint',
    'Отход': 'otkhod', 'Чары': 'chary', 'Концентрация': 'kontsentratsiya',
    'Подлость': 'podlost', 'Допинг': 'doping', 'Барьер': 'barer',
    'Вспышка': 'vspyshka', 'Укол': 'ukol', 'Казнь': 'kazn',
    'Подсечка': 'podsechka', 'Комбо': 'kombo', 'Уход в тень': 'ukhod_v_ten',
    'Насмешка': 'nasmeshka', 'Засада': 'zasada', 'Милость божья': 'milost_bozhya',
    'Укус': 'ukus', 'Удар Грааля': 'udar_graalya', 'Шторм': 'shtorm',
    'Подчинение': 'podchinene', 'Усталость': 'ustalost',
    'Размашистый удар': 'razmashisty_udar', 'Подражание': 'podrazhanie',
    'Ярость': 'yarost', 'Проклятие': 'proklyatie', 'Выстрел': 'vystrel',
    'Пируэт': 'piruet', 'Сила леса': 'sila_lesa', 'Осушение': 'osushenie',
    'Временной сдвиг': 'vremennoy_sdvig', 'Взрыв': 'vzryv',
    'Легендарный': 'legendarny', 'Божественный': 'bozhestvenny',
    'Вострый': 'vostry', 'Гигантский': 'gigantsky', 'Магический': 'magichesky',
    'Сверхзвуковой': 'sverkhzvukovoy', 'Противотанковый': 'protivotankovy',
    'Электрический': 'elektrichesky', 'Огненный': 'ognenny',
    'Разумный': 'razumny', 'Ужасный': 'uzhasny', 'Псионический': 'psionichesky',
    'Хронотургический': 'khronoturgichesky', 'Короля': 'korolya',
    'Артура': 'artura', 'Титана': 'titana', 'Ужасов': 'uzhasov',
    'Ангела': 'angela', 'Джинна': 'dzhinna', 'Зевса': 'zevsa',
    'Мастера': 'mastera', 'Лича': 'licha', 'Хитреца': 'khitretsa',
    'Сломанное ребро': 'slomannoe_rebro', 'Грусть': 'grust',
    'Головокружение': 'golovokrujene', 'Обида': 'obida',
    'Пьянство': 'pyanstvo', 'Истощение': 'ischerpanie',
    'Рукоприкладство': 'rukoprikladstvo',
}


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TITLES_DIR, exist_ok=True)
    os.makedirs(BACK_DIR, exist_ok=True)

    for name, (cat, text_a, text_b) in CARDS.items():
        if name == 'Усталость':
            img = create_fatigue_card()
        elif name in TWO_SIDED:
            img = create_double_card(name, text_a, text_b)
        else:
            img = create_single_card(name, text_a)
        img.save(os.path.join(OUTPUT_DIR, f'{ASCII_MAP[name]}.png'))
        print(f'  {name}.png')

    for name, desc in TITLES.items():
        img = create_title_card(name, desc)
        img.save(os.path.join(TITLES_DIR, f'{ASCII_MAP[name]}.png'))
        print(f'  {name}.png (титул)')

    for name, info in TRAUMAS.items():
        img = create_trauma_card(name, info['desc'], info['color'])
        img.save(os.path.join(OUTPUT_DIR, f'{ASCII_MAP[name]}.png'))
        print(f'  {name}.png (травма)')

    img = create_trauma_back()
    img.save(os.path.join(BACK_DIR, 'back_trauma.png'))
    print('  back_trauma.png')

    img = create_card_back()
    img.save(os.path.join(BACK_DIR, 'card_back.png'))
    print('  card_back.png')

    print(f'\nКарт: {len(CARDS)}, Титулов: {len(TITLES)}, Травм: {len(TRAUMAS)}')


if __name__ == '__main__':
    main()
