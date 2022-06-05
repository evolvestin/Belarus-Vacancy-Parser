import re
import random
from typing import Union


def tags_generator():
    cities_list, generated_tags = [], {}
    for city in [('None', 'None'), ('витебск', 'витебске'), ('могилев', 'могилеве'),
                 ('гродно', 'гродно'), ('брест', 'бресте'), ('минск', 'минске'), ('гомель', 'гомеле')]:
        cities_list.append(city[0]) if city[0] != 'None' else None
        city_tags, generated = [city[0]] if city[0] != 'None' else [], [('работа', 'мечты')]
        for place in [('беларусь', 'беларуси')] + [city if city[0] != 'None' else None]:
            if place:
                for action in ['заработок', 'работа', 'вакансии']:
                    generated.extend([(place if type(place) == str else place[0], action),
                                      (action, 'в', place if type(place) == str else place[1])])
        for tag in generated:
            if len(tag) == 2:
                city_tags.extend([f'{tag[0]}{tag[1]}', f'{tag[0]}_{tag[1]}', f'{tag[1]}{tag[0]}'])
            elif len(tag) == 3:
                city_tags.extend([f'{tag[0]}{tag[1]}{tag[2]}', f'{tag[0]}_{tag[1]}_{tag[2]}'])
        city_tags.extend(['работа', 'деньги', 'заработок'])
        generated_tags[city[0]] = city_tags
    return generated_tags, cities_list


gen_tags, cities = tags_generator()
text = 'Найти вакансию можно в нашем Telegram канале ' \
       '(ссылка в шапке профиля) по №{0} (воспользуйтесь поиском по каналу)\n\nID {0}\n\n'


def generator(post_id: Union[int, str], place: str, vacancy_tags: list):
    tags, response = [], text.format(post_id)
    for tag in vacancy_tags:
        tags.append(tag.lower())
        modified = re.sub('_', '', tag).lower()
        tags.append(modified) if modified != tag.lower() else None
    for city in cities:
        if city in re.sub('ё', 'е', place.lower()):
            break
    else:
        city = 'None'
    city_tags = gen_tags.get(city, [])
    len_city_tags = len(city_tags) if len(city_tags) <= 30 - len(tags) else 30 - len(tags)
    tags.extend(random.sample(city_tags, len_city_tags))
    for tag in random.sample(tags, len(tags)):
        if len(response) + len(tag) + 2 <= 2000:
            response += f' #{tag}'
    return response
