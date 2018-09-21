from character import load_characters
import functools
import logging


def verify_action_count(characters, targets):
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
    event_actions = len([event for event in events if event[1] in area_order.keys()])

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
    plain_patrol_actions = (max(required_like, 0) + 14) // 15
    extra_actions = 84 - (battle_actions + event_actions + plain_patrol_actions)
    logging.info('Actions: 84 total')
    logging.info('\tbattle: {:2d}'.format(battle_actions))
    logging.info('\tevent:  {:2d}'.format(event_actions))
    logging.info('\tpatrol: {:2d}'.format(plain_patrol_actions))
    logging.info('\textra:  {:2d} (for building)'.format(extra_actions))

    assert extra_actions >= 0

    
def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(funcName)s:%(lineno)d] %(message)s')

    characters = load_characters()
    targets = ['달비라', '에뮤사', '라비', '누르', '세이유이']
    verify_action_count(characters, targets)


if __name__ == '__main__':
    main()
