from action import BuildAction
from collections import deque
import functools
import logging


def get_city_status(build_actions, num_characters):
    build_by_area = dict()
    build_by_area['중앙청'] = ['중앙청기지']
    for build in build_actions:
        if build_by_area.get(build.area):
            build_by_area[build.area].append(build.building)
        else:
            build_by_area[build.area] = [build.building]
    total_power, total_science, total_info = 0, 0, 0

    power_buildings = ['공정소', '구립공정빌딩', '대형공정소', '시립공정빌딩', '흑문감측소']
    science_buildings = ['연구소', '지하연구소', '구립연구센터', '대형연구소', '시립연구센터', '공공도서관']
    info_buildings = ['정보국', '구립정보국', '대형정보국', '시립정보국', '정보센터']
    special_bulidings = ['가부키초', '쇼핑센터', '지하철역', '기획처', '크레인', '불꽃축제']

    for area in build_by_area:
        power, science, info = 0, 0, 0
        power_factor, science_factor, info_factor = 1., 1., 1.
        for build in build_by_area[area]:
            if build == '중앙청기지':
                power += 5
                science += 5
                info += 5
            elif build == '공정소':
                power += 5
            elif build == '구립공정빌딩':
                power += 5 + len([b for b in build if build in power_buildings])
            elif build == '대형공정소':
                power += 10
            elif build == '시립공정빌딩':
                power += 15
                power_factor = 1.5
            elif build == '흑문감측소':
                power += num_characters

            elif build == '연구소':
                science += 5
            elif build == '구립연구센터':
                science += 5 + len([b for b in build if build in science_buildings])
            elif build == '대형연구소':
                science += 10
            elif build == '시립연구센터':
                science += 15
                science_factor = 1.5
            elif build == '공공도서관':
                science += num_characters

            elif build == '정보국':
                info += 5
            elif build == '구립정보국':
                info += 5 + len([b for b in build if build in info_buildings])
            elif build == '대형정보국':
                info += 10
            elif build == '시립정보국':
                info += 15
                info_factor = 1.5
            elif build == '정보센터':
                info += num_characters
        total_power += power * power_factor
        total_science += science * science_factor
        total_info += info * info_factor

    if len(build_actions) > 0 and build_actions[-1].building == '지하연구소':
        total_science += 25

    logging.debug('Power:\t{}'.format(total_power))
    logging.debug('Science:\t{}'.format(total_science))
    logging.debug('Info:\t{}'.format(total_info))
    return int(total_power + 0.5), int(total_science + 0.5), int(total_info + 0.5), build_by_area


def get_candidates(bt, power, science, build_by_area):
    candidate_area = ['중앙청']
    if power >= 5:
        candidate_area.append('고등학교')
    if power >= 10:
        candidate_area.append('동방거리')
        candidate_area.append('시가지')
    if power >= 20:
        candidate_area.append('연구소')
    if power >= 50:
        candidate_area.append('항구도시')
    if power >= 100:
        candidate_area.append('구시가지')
    if power >= 150:
        candidate_area.append('항구')

    empty_area = [area for area in candidate_area if not build_by_area.get(area)]
    for area in empty_area[1:]:
        candidate_area.remove(area)
    for area in build_by_area:
        if len(build_by_area[area]) >= 4:
            candidate_area.remove(area)

    candidates = list()
    already_built = set(functools.reduce(lambda x, y: x + y, build_by_area.values()))
    underground = len(bt) > 0 and bt[-1].building == '지하연구소'
    for area in candidate_area:
        if (not underground and science >= 60) or (underground and science - 25 < 60 and science >= 60):
            if '시립공정빌딩' not in already_built:
                candidates.append(BuildAction(area, '시립공정빌딩'))
            if '시립연구센터' not in already_built:
                candidates.append(BuildAction(area, '시립연구센터'))
            if '시립정보국' not in already_built:
                candidates.append(BuildAction(area, '시립정보국'))
        if (not underground and science >= 30) or (underground and science - 25 < 30 and science >= 30):
            if '흑문감측소' not in already_built:
                candidates.append(BuildAction(area, '흑문감측소'))
            if '공공도서관' not in already_built:
                candidates.append(BuildAction(area, '공공도서관'))
            if '정보센터' not in already_built:
                candidates.append(BuildAction(area, '정보센터'))
        if (not underground and science >= 35) or (underground and science - 25 < 35 and science >= 35):
            candidates.append(BuildAction(area, '대형공정소'))
            candidates.append(BuildAction(area, '대형연구소'))
            candidates.append(BuildAction(area, '대형정보국'))
        if not underground:
            candidates.append(BuildAction(area, '지하연구소'))
        # candidates.append(BuildAction(area, '공정소'))
        # candidates.append(BuildAction(area, '연구소'))
        # candidates.append(BuildAction(area, '정보국'))
    logging.debug('Candidates: {}'.format(candidates))
    return candidates


def find_build_path(target_city_status, requirements, num_characters):
    target_power, target_science, target_info = target_city_status
    q = deque()
    q.append(list())    # empty build tree
    while len(q) > 0:
        bt = q.popleft()
        logging.info('Currnt BT : {} ({})'.format(len(bt), bt))
        power, science, info, build_by_area = get_city_status(bt, num_characters)
        if power >= target_power and science >= target_science and info >= target_info:
            return bt
        for candidate in get_candidates(bt, power, science, build_by_area):
            q.append(bt + [candidate])
    return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(funcName)s:%(lineno)d] %(message)s')
    bt = find_build_path((100, 0, 75), [], 30)
    logging.info(bt)
