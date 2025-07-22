import os
import re
import emoji
import base64
import random
import string
import sqlite3
from copy import copy
from io import BytesIO
from typing import Union
from db.emoji_gen import emojis_path
from PIL.ImageFont import FreeTypeFont
from PIL import Image, ImageFont, ImageDraw
from statistics import median as median_function


def get_fonts():
    paths = {}
    for path in os.listdir('fonts'):
        search = re.search(r'(.*?)-(.*)\.ttf', path)
        if search:
            paths[search.group(1)] = paths.get(search.group(1), {})
            paths[search.group(1)][search.group(2)] = f'fonts/{path}'
    return paths


class SQL:
    def __init__(self, database):
        def dict_factory(cursor, row):
            dictionary = {}
            for idx, col in enumerate(cursor.description):
                dictionary[col[0]] = row[idx]
            return dictionary
        self.connection = sqlite3.connect(database, timeout=100, check_same_thread=False)
        self.connection.execute('PRAGMA journal_mode = WAL;')
        self.connection.execute('PRAGMA synchronous = OFF;')
        self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def request(self, sql, fetchone=None):
        lock = True
        while lock is True:
            lock = False
            try:
                with self.connection:
                    self.cursor.execute(sql)
            except IndexError and Exception as error:
                for pattern in ('database is locked', 'no such table'):
                    if pattern in str(error):
                        lock = True
                if lock is False:
                    raise error
        result = self.cursor.fetchone() if fetchone else self.cursor.fetchall()
        return dict(result) if result and fetchone else result

    def get_emoji(self, text_emoji):
        query = f"SELECT data FROM emoji WHERE emoji LIKE '{text_emoji}%' ORDER BY length(emoji)"
        return self.request(query, fetchone=True)


font_paths = get_fonts()


def font(size: int, family: str = 'OpenSans', weight: str = 'Regular'):
    font_type = font_paths.get(family, font_paths.get('OpenSans'))
    return ImageFont.truetype(font_type.get(weight, font_type.get('Regular')), size)


def width(text: str, size: int, family: str = 'OpenSans', weight: str = 'Regular'):
    emojis = emoji.emoji_list(text)
    emoji_size = size + (size * 0.4)
    indent = int(emoji_size + emoji_size * 0.11) * len(emojis)
    text = emoji.replace_emoji(text, replace='') if emojis else text
    return FreeTypeFont.getbbox(font(size, family, weight), text)[2] + indent


def min_height(text: str, size: int, family: str = 'OpenSans', weight: str = 'Regular'):
    letter_heights = [FreeTypeFont.getbbox(font(size, family, weight), i, anchor='lt')[3] for i in list(text)]
    descender_heights = [FreeTypeFont.getbbox(font(size, family, weight), i, anchor='ls')[3] for i in list(text)]
    result = [element1 - element2 for (element1, element2) in zip(letter_heights, descender_heights)]
    if emoji.emoji_list(text):
        return max(result)
    return median_function(result) if result else 0


def height(text: str, size: int, family: str = 'OpenSans', weight: str = 'Regular'):
    emoji_size = size + (size * 0.4)
    response = int(emoji_size - emoji_size * 0.22) if emoji.emoji_list(text) else None
    if response is None:
        result = [FreeTypeFont.getbbox(font(size, family, weight), text, anchor=anchor)[3] for anchor in ['lt', 'ls']]
        response = result[0] - result[1]
    return response


def image(
        text: str,
        background: Union[Image.open, Image.new] = None,
        font_size: int = 300,
        font_family: str = 'OpenSans',
        font_weight: str = 'Regular',
        original_width: int = 1000,
        original_height: int = 1000,
        text_align: str = 'center',
        left_indent: int = 50,
        top_indent: int = 50,
        left_indent_2: int = 0,
        top_indent_2: int = 0,
        text_color: tuple[int, int, int] = (0, 0, 0),
        background_color: tuple[int, int, int] = (256, 256, 256)
):
    mask, family, spacing, response, coefficient, modal_height = None, font_family, 0, None, 0.6, 0

    if background and original_height == 1000:
        original_height = background.getbbox()[3]
    if background and not original_width == 1000:
        original_width = background.getbbox()[2]

    db = SQL(emojis_path)
    original_height -= top_indent * 2 + top_indent_2
    original_width -= left_indent * 2 + left_indent_2
    size = font_size if font_size != 300 else original_width // 3
    background = copy(background) or Image.new(mode='RGB', size=(original_width, original_height), color=background_color)
    while spacing < modal_height * coefficient or spacing == 0:
        skip, layers, heights, weights = False, [], [], []
        mask = Image.new(mode='RGBA', size=(original_width, original_height), color=(0, 0, 0, 0))
        for line in text.strip().split('\n'):
            line_weight, layer_array = font_weight, []
            if line.startswith('**') and line.endswith('**'):
                line_weight, line = 'Bold', line.strip('**')
            if line.startswith('__') and line.endswith('__'):
                line_weight, line = 'Italic', line.strip('__')
            if line:
                for word in re.sub(r'\s+', ' ', line).strip().split(' '):
                    if width(word, size, family, line_weight) > original_width:
                        skip = True
                        break
                    if width(' '.join(layer_array + [word]), size, family, line_weight) > original_width:
                        weights.append(line_weight), layers.append(' '.join(layer_array))
                        heights.append(height(' '.join(layer_array), size, family, line_weight))
                        layer_array = [word]
                    else:
                        layer_array.append(word)
                else:
                    weights.append(line_weight), layers.append(' '.join(layer_array))
                    heights.append(height(' '.join(layer_array), size, family, line_weight))
            else:
                layers.append(''), heights.append(0), weights.append(line_weight)

        if skip:
            size -= 1
            continue

        layers_count = len(layers) - 1 if len(layers) > 1 else 1
        full_height = heights[0] - min_height(layers[0], size, family, weights[0])
        modal_height = max(heights) if emoji.emoji_list(text) else median_function(heights)
        full_height += sum([min_height(layers[i], size, family, weights[i]) for i in range(0, len(layers))])
        draw, aligner, emoji_size, additional_height = copy(ImageDraw.Draw(mask)), 0, size + (size * 0.4), 0
        spacing = (original_height - full_height) // layers_count
        if spacing > modal_height * coefficient:
            spacing = modal_height * coefficient
            aligner = (original_height - full_height - (spacing if len(layers) > 1 else 0) * layers_count) // 2
        for i in range(0, len(layers)):
            left = left_indent + left_indent_2
            emojis = [e['emoji'] for e in emoji.emoji_list(layers[i])]
            modded = (heights[i] - min_height(layers[i], size, family, weights[i]))
            chunks = [re.sub('&#124;', '|', i) for i in emoji.replace_emoji(layers[i], replace='|').split('|')]
            modded = modded if i != 0 or (i == 0 and layers_count == 0) else 0
            top = top_indent + top_indent_2 + aligner + additional_height - modded
            additional_height += heights[i] - modded + spacing
            if text_align == 'center':
                left += (original_width - width(layers[i], size, family, weights[i])) // 2

            for c in range(0, len(chunks)):
                chunk_width = width(chunks[c], size, family, weights[i])
                emoji_scale = (left + chunk_width + int(emoji_size * 0.055), int(top))
                text_scale = (left, top + heights[i] - height(chunks[c], size, family, weights[i]))
                draw.text(text_scale, chunks[c], text_color, font(size, family, weights[i]), anchor='lt')
                if c < len(emojis):
                    emoji_record = db.get_emoji(emojis[c])
                    if emoji_record:
                        emoji_image = BytesIO(base64.b64decode(emoji_record['data']))
                        foreground = Image.open(emoji_image).resize((int(emoji_size), int(emoji_size)), 3)
                    else:
                        foreground = Image.new('RGBA', (int(emoji_size), int(emoji_size)), (0, 0, 0, 1000))
                    try:
                        mask.paste(foreground, emoji_scale, foreground)
                    except IndexError and Exception:
                        mask.paste(foreground, emoji_scale)
                left += chunk_width + int(emoji_size + emoji_size * 0.11)
        size -= 1
    db.close()
    if mask:
        file_name = f"{''.join(random.sample(string.ascii_letters, 10))}.jpg"
        background.paste(mask, (0, 0), mask)
        background.save(file_name)
        return file_name
    return response
