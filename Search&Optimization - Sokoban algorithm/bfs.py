from problem import State, SokobanProblem, ActionType
from pathlib import Path
from typing import List, Tuple
from queue import Queue


class Assignment1:  # Do not change the name of this class!
    STUDENT_ID = '__BFS__'

    def search(self, problem: SokobanProblem) -> List[ActionType]:
        """
        Your documentation should contain the following things:
        - Which algorithm that you designed?
        - Why did you select it?
        - What does each command do?
        """
        frontier = Queue()
        frontier.put(problem.initial_state)
        reached = [problem.initial_state]

        while not frontier.empty():
            state = frontier.get()
            if problem.is_goal_state(state):
                return state.get_action_sequence()

            for child, _ in problem.expand(state):
                if child in reached:
                    continue
                frontier.put(child)
                reached.append(child)

        return []
