from problem import RandomGeometricGraphProblem
from pathlib import Path
from typing import List
import heapq

STUDENT_ID = Path(__file__).stem.split('_')[1]

# This algorithm is a simple Djikstra algorithm, but taking in account 
# x dynamic number of criteria and not only the distance.
# A heapq is used to sort the found nodes according to X criteria in a tuple.

class Assignment:
    def __init__(self, problem: RandomGeometricGraphProblem):
        self.problem = problem
        
    def search(self, criteria, time_limit) -> List[str]:
        # Initialize the heapQ with its first element which is the starting node.
        # Each node in the heapq contains multiple element.
        # NODE(TupleOfCriteriasCost, pathToThisNodeList, currentNodeName)
        # Tuple of criteriaCost is a tuple from 1 to 3 in length beginning by 0, 0, 0
        # Its orderer according to the criteria priority, and will be sorted according to it.
        # If two node has the same first criteria values, then they will be sorted according to the second.. then the third..

        # When using a node from this heapq.
        # => Node[-1] Will ALWAYS be the current's node name.
        # => Node[-2] Will ALWAYS be the current's node path.
        # => Node[0] Will always be the most important criteria cost
        # => Node[0 + i (where i is the len(criteria - 1))] will be the rest of the criterias cost 
        # sorted by priority.

        toVisit = [tuple([0] * len(criteria)) + ([self.problem.initial_state], self.problem.initial_state)]

        # Reached nodes, no need to expand them anymore.

        reached = []

        # While nodes are to be visited.
        
        while toVisit:
            # Get the first node in all criterias.

            bestCurrentNode = heapq.heappop(toVisit)

            # If its path is correct, return it.

            if self.problem.is_solution_path(bestCurrentNode[-2]):
                return bestCurrentNode[-2]
            
            # If we already expanded it, skip it.

            if bestCurrentNode[-1] in reached:
                continue

            # Else, mark it as expanded now, for future checks.

            reached.append(bestCurrentNode[-1])

            # expand it to get all children.

            for child, _ in self.problem.expand(bestCurrentNode[-1]):
                # Initialize a list with all criteria cost.
                criteria_costs = []
                i = 0
                for cri in criteria:

                    # Loop over all criteria in priority order
                    # And append to the previous list its cost from the previous node to this one, adding the cost to reach the previous node.
                    # Which is bestCurrentNode[i]
                    # Our node always begin with X values (1 to 3) values which is len(criteria)
                    # So node[i] loop from 0 to len(criteria) and will always get its corresponding value.

                    criteria_costs.append(self.problem.get_cost_of(bestCurrentNode[-1], child, cri) + bestCurrentNode[i])
                    i += 1

                #  Create the path to get to this node which is the node list + the child.

                new_path = bestCurrentNode[-2] + [child]

                # Format everything into a tuple, to put in in the heapq and be sorted.
                # With the criteria cost at first, and then the path

                newt = tuple(criteria_costs) + (new_path, child)

                # Append it.

                heapq.heappush(toVisit, newt)

        # If the code goes there, it must have found no correct solution.

        return []