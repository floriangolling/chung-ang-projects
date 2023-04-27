from problem import RandomGeometricGraphProblem
from typing import List
from queue import Queue

STUDENT_ID = '__BFS__'

class Assignment:
    def __init__(self, problem: RandomGeometricGraphProblem):
        self.problem = problem

    def search(self, criteria: tuple, time_limit) -> List[str]:
        """
        Your documentation should contain the following things:
        - Which algorithm that you designed?
        - Why did you select it?
        - What does each command do?
        """
        frontier = Queue()
        frontier.put((self.problem.initial_state,))
        reached = [self.problem.initial_state]

        while not frontier.empty():
            path = frontier.get()
            if self.problem.is_solution_path(path):
                return list(path)

            for child, _ in self.problem.expand(path[-1]):
                if child in reached:
                    continue
                frontier.put(path + (child,))
                reached.append(child)

        return []
