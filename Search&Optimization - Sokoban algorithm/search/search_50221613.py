from problem import  SokobanProblem, ActionType
from pathlib import Path
from typing import List
from queue import PriorityQueue

# This call is in order to use Priority Queue
# I had some issues using Priority Queue because it needed a weight and a counter to work
# So this class increment its counter each addition itself in order not to 
# do it in the actual program

class indexPriorityQueue(PriorityQueue):
    def __init__(self):
        PriorityQueue.__init__(self)
        self.counter = 0

    def put(self, item, priority):
        PriorityQueue.put(self, (priority, self.counter, item))
        self.counter += 1

    def get(self, *args, **kwargs):
        _, _, item = PriorityQueue.get(self, *args, **kwargs)
        return item

# This algorithm is a common Uniform Cost algorithm.

class Assignment1:  # Do not change the name of this class!

    STUDENT_ID = Path(__file__).stem.split('_')[1]
     
    def search(self, problem: SokobanProblem) -> List[ActionType]:
        # Create a PriorityQueue in order to get according to the reward so far which is the weight.
        uncheckedNodes = indexPriorityQueue()
        # Reached node list, not to check anymore.
        reached = []
        # Put the initial state in the queue to be checked.
        # We put 0 as priority but it does not matter it will get removed anyway
        uncheckedNodes.put(problem.initial_state, 0)

        # Loop over all node in the queue until we find a solution
        while not uncheckedNodes.empty():
            # Get the best reward so far node
            state = uncheckedNodes.get()
            # If its the goal state, return it.
            if problem.is_goal_state(state):
                return state.get_action_sequence()
            # set it to not be expanded anymore in the list.
            if state not in reached:
                reached.append(state)
            # If not, check all its children and put them in order in the 
            # PriorityQueue according to their reward_so_far, (I multiply it by -1* because it sort it 
            # in the PriorityQueue by best reward_so_far)
            for child, _ in problem.expand(state):
                if child in reached:
                    continue
                uncheckedNodes.put(child, child.reward_so_far * -1)