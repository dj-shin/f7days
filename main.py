from character import load_characters
import functools
import logging
from action import Action, BattleAction, DevAction, BuildAction, PlainPatrolAction, EventPatrolAction


def get_action_count(characters, targets):
    logging.info('Targets: {}'.format(targets))
    events = functools.reduce(lambda x, y: x + y, [characters[target].events for target in targets])

    # find last battle area
    area_order = {
        '중앙청': 0,
        '고등학교': 1,
        '동방거리': 2,
        '시가지': 2,
        '연구소': 4,
        '항구도시': 5,
        '구시가지': 6,
        '항구': 7
    }
    area_required = set()
    for event in events:
        if event[1] in area_order.keys():
            area_required.add(event[1])
        for requirement in event[3]:
            if requirement['type'] == 'area_clear':
                area_required.add(requirement['area'])
    last_area = max([area_order[area] for area in area_required])
    if last_area == 2 and '동방거리' in area_required and '시가지' in area_required:
        last_area = 3
    logging.info('Last area: {}'.format(last_area))

    battle_actions = last_area * 6
    event_actions = [event for event in events if event[1] in area_order.keys()]

    # find required like
    required_like_total = 100 * len(targets)
    present_like = min([6, len(targets)]) * 40
    battle_like = battle_actions * 3
    event_like = sum([event[2] for event in events])

    required_like = required_like_total - (present_like + battle_like + event_like)
    logging.info('Like: {} total'.format(required_like_total))
    logging.info('\tpresent: {:3d}'.format(present_like))
    logging.info('\tbattle:  {:3d}'.format(battle_like))
    logging.info('\tevent:   {:3d}'.format(event_like))
    logging.info('\textra:   {:3d}'.format(required_like))

    # find minimum actions count
    aggregated_patrol_actions = (max(required_like, 0) + 14) // 15
    individual_patrol_actions = (max([100 - 40 - battle_actions - sum([event[2] for event in characters[target].events]) for target in targets]) + 4) // 5
    logging.info('Aggregated patrol actions: {}'.format(aggregated_patrol_actions))
    logging.info('Individual patrol actions: {}'.format(individual_patrol_actions))
    plain_patrol_actions = max(aggregated_patrol_actions, individual_patrol_actions)
    extra_actions = 84 - (battle_actions + len(event_actions) + plain_patrol_actions)

    logging.info('Actions: 84 total')
    logging.info('\tbattle: {:2d}'.format(battle_actions))
    logging.info('\tevent:  {:2d}'.format(len(event_actions)))
    logging.info('\tpatrol: {:2d}'.format(plain_patrol_actions))
    logging.info('\textra:  {:2d} (for building)'.format(extra_actions))

    assert extra_actions >= 0

    return battle_actions, event_actions, plain_patrol_actions, extra_actions


def get_city_status(prev_actions):
    build_actions = [action for action in prev_actions if isinstance(action, BuildAction)]
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
                power += 30     # TODO: number of owned characters

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
                science += 30   # TODO: number of owned characters

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
                info += 30   # TODO: number of owned characters
        total_power += power * power_factor
        total_science += science * science_factor
        total_info += info * info_factor

    if len(build_actions) > 0 and build_actions[-1].building == '지하연구소':
        total_science += 25

    logging.debug('Power:\t{}'.format(total_power))
    logging.debug('Science:\t{}'.format(total_science))
    logging.debug('Info:\t{}'.format(total_info))
    return int(total_power + 0.5), int(total_science + 0.5), int(total_info + 0.5), build_by_area

    
def get_candidates(prev_actions, required_actions, extra_actions):
    candidates = list()
    cleared_areas = Action.cleared_area(prev_actions)
    power, science, info, build_by_area = get_city_status(prev_actions)

    # next patrol actions
    patrol_actions = [action for action in prev_actions if isinstance(action, EventPatrolAction)]
    for action in required_actions:
        if action.area in cleared_areas and (action.order == 1 and not [x for x in patrol_actions if x.character == action.character]
                or [x for x in patrol_actions if x.character == action.character and x.order + 1 == action.order] and not [x for x in patrol_actions if x.character == action.character and x.order == action.order]):
            possible = True
            for requirement in action.requirements:
                if requirement['type'] == 'area_clear':
                    possible &= requirement['area'] in cleared_areas
                elif requirement['type'] == 'area_build':
                    possible &= requirement['value'] in build_by_area[requirement['area']]
            if possible:
                candidates.append(action)

    # next battle action = 1 case
    # exception: 시가지 or 동방거리 선택
    battle_actions = [action for action in prev_actions if isinstance(action, BattleAction)]
    battle_areas = set([action.area for action in prev_actions if isinstance(action, BattleAction)])
    last_battle_action = battle_actions[-1] if len(battle_actions) > 0 else None
    if last_battle_action:
        if last_battle_action.order != 6:
            candidates.append(BattleAction(last_battle_action.area, last_battle_action.order + 1))
        else:
            if last_battle_action.area == '고등학교' and power >= 10:
                candidates.append(BattleAction('동방거리', 1))
                candidates.append(BattleAction('시가지', 1))
            elif last_battle_action.area == '동방거리' and power >= 10:
                if '시가지' in battle_areas and power >= 20:
                    candidates.append(BattleAction('연구소', 1))
                else:
                   candidates.append(BattleAction('시가지', 1))
            elif last_battle_action.area == '시가지' and power >= 10:
                if '동방거리' in battle_areas and power >= 20:
                    candidates.append(BattleAction('연구소', 1))
                else:
                    candidates.append(BattleAction('동방거리', 1))
            elif last_battle_action.area == '연구소' and power >= 50:
                candidates.append(BattleAction('항구도시', 1))
            elif last_battle_action.area == '항구도시' and power >= 100:
                candidates.append(BattleAction('구시가지', 1))
            elif last_battle_action.area == '구시가지' and power >= 100:
                candidates.append(BattleAction('항구', 1))
    else:
        candidates.append(BattleAction('고등학교', 1))

    if extra_actions > 0:
        # next build action
        already_built = set(functools.reduce(lambda x, y: x + y, build_by_area.values()))
        for area in cleared_areas:
            if science >= 60:
                if '시립공정빌딩' not in already_built:
                    candidates.append(BuildAction(area, '시립공정빌딩'))
                if '시립연구센터' not in already_built:
                    candidates.append(BuildAction(area, '시립연구센터'))
                if '시립정보국' not in already_built:
                    candidates.append(BuildAction(area, '시립정보국'))
            if science >= 30:
                if '흑문감측소' not in already_built:
                    candidates.append(BuildAction(area, '흑문감측소'))
                if '공공도서관' not in already_built:
                    candidates.append(BuildAction(area, '공공도서관'))
                if '정보센터' not in already_built:
                    candidates.append(BuildAction(area, '정보센터'))
            if science >= 35:
                candidates.append(BuildAction(area, '대형공정소'))
                candidates.append(BuildAction(area, '대형연구소'))
                candidates.append(BuildAction(area, '대형정보국'))
            candidates.append(BuildAction(area, '지하연구소'))
            candidates.append(BuildAction(area, '공정소'))
            candidates.append(BuildAction(area, '연구소'))
            candidates.append(BuildAction(area, '정보국'))

        # next dev action = 1 for each cleared area
        dev_actions = [action for action in prev_actions if isinstance(action, DevAction)]
        dev_status = dict()
        for action in dev_actions:
            dev_status[action.area] = max(dev_status.get(action.area, 0), action.order)
        for area in cleared_areas:
            candidates.append(DevAction(area, dev_status.get(area, 0) + 1))

    logging.debug('Candidates : {}'.format(candidates))
    return candidates


def traverse(actions, characters, targets):
    battle_actions, event_actions, plain_patrol_actions, extra_actions = actions
    # Phase 1: fit actions in each hour of a week
    # order: dev - bulid - battle - (dev - build) in just cleared area - patrol (+ exceptional build)

    def _traverse(prev_actions, required_actions, extra_actions):
        done = True
        for action in required_actions:
            if action not in prev_actions:
                done = False
                break
        if done:
            return True, prev_actions
        if len(prev_actions) >= 12 * 7:
            return False, []
        if len(prev_actions) == 12 * 3:
            power, science, info, build_by_area = get_city_status(prev_actions)
            if info < 75:
                return False, []
        candidates = get_candidates(prev_actions, required_actions, extra_actions)
        for candidate in candidates:
            logging.debug('Hour {} : Choose {}'.format(len(prev_actions), candidate))
            done, complete_actions = _traverse(prev_actions + [candidate], required_actions, extra_actions - int(isinstance(candidate, BuildAction) or isinstance(candidate, DevAction)))
            if done:
                return True, complete_actions
        return False, []

    required_actions = list()
    for character in targets:
        order = 1
        for event in characters[character].events:
            if event[1] in ['중앙청', '고등학교', '동방거리', '시가지', '연구소', '항구도시', '구시가지', '항구']:
                required_actions.append(EventPatrolAction(event[1], character, order, event[3]))
                order += 1
    done, complete_actions =_traverse([], required_actions, extra_actions)
    if done:
        logging.info('==================================')
        for action in complete_actions:
            logging.info(action)
        logging.info('==================================')

    
def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(funcName)s:%(lineno)d] %(message)s')

    characters = load_characters()
    targets = ['달비라', '에뮤사', '라비', '누르', '세이유이']
    actions = get_action_count(characters, targets)
    traverse(actions, characters, targets)


if __name__ == '__main__':
    main()
