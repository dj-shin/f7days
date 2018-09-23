class Action:
    DEV = 0
    BUILD = 1
    BATTLE = 2
    PATROL = 3

    def __init__(self, action_type, area):
        self._type = action_type
        self.area = area

    def valid(self, prev_actions):
        raise NotImplemented

    @staticmethod
    def cleared_area(prev_actions):
        return set(['중앙청'] + [action.area for action in prev_actions if isinstance(action, BattleAction) and action.order == 6])


class BattleAction(Action):
    def __init__(self, area, order):
        super(BattleAction, self).__init__(Action.BATTLE, area)
        self.order = order

    def __repr__(self):
        return '<Battle: {} ({}/6)>'.format(self.area, self.order)


class DevAction(Action):
    def __init__(self, area, order):
        super(DevAction, self).__init__(Action.DEV, area)
        self.order = order

    def __repr__(self):
        return '<Dev: {} ({})>'.format(self.area, self.order)


class BuildAction(Action):
    def __init__(self, area, building):
        super(BuildAction, self).__init__(Action.BUILD, area)
        self.building = building

    def __repr__(self):
        return '<Build: {} ({})>'.format(self.building, self.area)


class PlainPatrolAction(Action):
    def __init__(self, area, characters):
        super(PlainPatrolAction, self).__init__(Action.PATROL, area)
        self.characters = characters

    def __repr__(self):
        return '<Plain Patrol: {}>'.format(self.characters)


class EventPatrolAction(Action):
    def __init__(self, area, character, order, requirements):
        super(EventPatrolAction, self).__init__(Action.PATROL, area)
        self.character = character
        self.order = order
        self.requirements = requirements

    def __repr__(self):
        return '<Event Patrol: {} ({}, {})>'.format(self.character, self.area, self.order)
