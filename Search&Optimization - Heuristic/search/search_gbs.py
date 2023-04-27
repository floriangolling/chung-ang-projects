import math

from dataclasses import dataclass
from problem import RandomGeometricGraphProblem
from pathlib import Path
from typing import List, Iterable
from queue import PriorityQueue


STUDENT_ID = Path(__file__).stem.split('_')[1]

@dataclass(order=True)
class State:
    priority: float
    path: tuple


def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

class Assignment:
    def __init__(self, problem: RandomGeometricGraphProblem):
        self.problem = problem

    def heuristic(self, start: str, destinations: Iterable[str]):
        start_place = self.problem.get_position_of(start)
        dist_to_dest = [distance(start_place, self.problem.get_position_of(d))
                        for d in destinations if d != start_place]
        return min(dist_to_dest)

    def search(self, criteria: tuple, time_limit) -> List[str]:
        frontier = PriorityQueue()
        frontier.put(State(self.heuristic(self.problem.initial_state, self.problem.places_to_visit),
                           (self.problem.initial_state,)))
        reached = [self.problem.initial_state]

        while not frontier.empty():
            state = frontier.get()
            if self.problem.is_solution_path(state.path):
                return list(state.path)

            remaining_to_visit = [p
                                  for p in self.problem.places_to_visit
                                  if p not in state.path]

            for child, _ in self.problem.expand(state.path[-1]):
                if child in reached:
                    continue
                frontier.put(State(self.heuristic(child, remaining_to_visit),
                                   state.path + (child,)))
                reached.append(child)

        return []

