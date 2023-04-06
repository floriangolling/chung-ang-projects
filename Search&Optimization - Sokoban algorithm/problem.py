import numpy as np
from enum import Enum
from typing import List, Optional, Tuple, NamedTuple
from collections import namedtuple


class BlockType(Enum):
    WALL = 0
    EMPTY = 1
    TARGET = 2
    BOX_ONTARGET = 3
    BOX_OFFTARGET = 4
    PLAYER = 5
    HILL_TOP = 9


class ActionType(Enum):
    PUSH_UP = 1
    PUSH_DOWN = 2
    PUSH_LEFT = 3
    PUSH_RIGHT = 4
    MOVE_UP = 5
    MOVE_DOWN = 6
    MOVE_LEFT = 7
    MOVE_RIGHT = 8

    def is_push_action(self):
        return self.value < 5


class State(NamedTuple):
    map: np.ndarray
    parent: Optional['State']
    action: Optional[ActionType]
    reward_so_far: float
    depth: int

    def __repr__(self):
        return f'State[{self.parent.map if self.parent is not None else None} + {self.action} = {self.map} (at {self.depth})]'

    def __eq__(self, other: 'State'):
        return (self.map == other.map).all()

    def __ne__(self, other: 'State'):
        return not self == other

    def equals(self, other: 'State'):
        return (self.map == other.map).all() and \
            self.action == other.action and \
            self.depth == other.depth and \
            self.reward_so_far == other.reward_so_far

    def has_ancestor(self, other: 'State'):
        if self == other:
            return True
        if self.parent is not None:
            return self.parent.has_ancestor(other)
        else:
            return False

    def get_action_sequence(self) -> List[ActionType]:
        if self.parent is not None:
            return self.parent.get_action_sequence() + [self.action]
        else:
            return []


def _check_same_room(state: State, fixed: np.ndarray) -> bool:
    return ((state.map == fixed) |
            ((state.map == BlockType.BOX_ONTARGET.value) & (fixed == BlockType.TARGET.value)) |
            (state.map > BlockType.BOX_ONTARGET.value)).all()


def _get_box_places(map):
    return np.argwhere((map == 3) | (map == 4)).tolist()


def _get_hill_distance(map):
    agent = np.argwhere(map == 5)[0]
    hill = np.argwhere(map == 9)[0]
    return int(np.abs(hill - agent).sum())


def _reward_modification(act, curr_map, next_map):
    # There's a hill at (n, n)
    if _get_hill_distance(next_map) > _get_hill_distance(curr_map):
        hill_climbing_delta = -0.1   # Make the climbing action has reward -0.2
    else:
        hill_climbing_delta = 0  # Otherwise reward -0.1

    if not act.is_push_action():
        return hill_climbing_delta

    if _get_box_places(curr_map) == _get_box_places(next_map):
        return -1.0 + hill_climbing_delta
    else:
        return hill_climbing_delta


class SokobanProblem:
    def __init__(self):
        # import gym
        # import gym_sokoban
        from gym_sokoban.envs import SokobanEnv
        self.__random = np.random.Generator(np.random.PCG64(5606))

        self.__env = SokobanEnv((6, 6), max_steps=30, num_boxes=3)
        self.__env.render = lambda *a, **k: []  # Disable rendering function
        self.__init_state = None
        self.__init_env_steps = 0

        self.reset_for_eval()

    def __state(self) -> np.ndarray:
        return self.__env.room_state.copy()

    def __reset_to_state(self, state: Optional[State] = None):
        if state is None:
            self.__env.room_state = self.__init_state.copy()
        else:
            assert _check_same_room(state, self.__env.room_fixed)
            self.__env.room_state = state.map.copy()

        self.__env.num_env_steps = 0
        self.__env.reward_last = 0

        total_targets = (self.__env.room_state == 2) | ((self.__env.room_fixed == 2) & (self.__env.room_state == 5))
        self.__env.boxes_on_target = self.__env.num_boxes - np.where(total_targets)[0].shape[0]
        self.__env.player_position = np.argwhere(self.__env.room_state == 5)[0]

    @property
    def initial_state(self) -> State:
        return State(self.__init_state.copy(), None, None, 0.0, 0)

    def reset_for_eval(self) -> list:
        self.__env.reset()
        # Set a hill position
        walls = np.argwhere(self.__state() == 0).tolist()
        hill_at = tuple(walls[self.__random.choice(len(walls))])
        self.__env.room_fixed[hill_at] = 9
        self.__env.room_state[hill_at] = 9

        self.__init_state = self.__state()
        self.__init_env_steps = self.__env.num_env_steps

        problem_spec = [self.__env.room_fixed.copy(),
                        self.__env.room_state.copy(),
                        self.__env.box_mapping.copy(),
                        self.__env.dim_room, self.__env.num_gen_steps, self.__env.num_boxes,
                        self.__env.player_position]

        return problem_spec

    def restore_for_eval(self, spec):
        self.__env.room_fixed, self.__env.room_state, self.__env.box_mapping,\
            self.__env.dim_room, self.__env.num_gen_steps, self.__env.num_boxes,\
            self.__env.player_position = spec

        self.__env.reward_last = 0

        total_targets = (self.__env.room_state == 2) | ((self.__env.room_fixed == 2) & (self.__env.room_state == 5))
        self.__env.boxes_on_target = self.__env.num_boxes - np.where(total_targets)[0].shape[0]
        self.__init_state = self.__state()
        self.__init_env_steps = self.__env.num_env_steps

    def expand(self, state: State) -> List[Tuple[State, float]]:
        next_state_map = []
        for action in ActionType:
            self.__reset_to_state(state)
            _, reward, _, _ = self.__env.step(action.value)

            next_map = self.__state()
            reward += _reward_modification(action, state.map, next_map)
            next_state = State(next_map, state, action, state.reward_so_far + reward, state.depth + 1)

            if next_state != state:
                next_state_map.append((next_state, reward))

        return next_state_map

    def is_goal_state(self, state: State) -> bool:
        empty_targets = state.map == 2
        player_hiding_target = (self.__env.room_fixed == 2) & (state.map == 5)
        are_all_boxes_on_targets = np.where(empty_targets | player_hiding_target)[0].shape[0] == 0
        return are_all_boxes_on_targets

    def execute(self, actions: List[ActionType]) -> Tuple[float, bool, int]:
        self.__reset_to_state()
        reward = 0.0
        done = False
        state = self.initial_state
        for act in actions:
            _, rew, done, _ = self.__env.step(act.value)

            next_map = self.__state()
            rew += _reward_modification(act, state.map, next_map)
            state = State(next_map, state, act, state.reward_so_far + rew, state.depth + 1)

            reward += rew

            if done:
                break

        assert reward == state.reward_so_far, f'{reward}, {state.reward_so_far}'
        self.__reset_to_state()
        return reward, done, len(actions)


__ALL__ = ['SokobanProblem', 'State', 'ActionType']
