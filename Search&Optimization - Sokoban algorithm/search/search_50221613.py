from problem import  SokobanProblem, ActionType
from pathlib import Path
from typing import List

# This algorithm is pretty simple, It will just lookup for the best rewards.
# And nothing interesting is found, it will test least interesting nodes that might 
# Be better in the future.

# I used this algorithm because Score is the most significant thing in our grade
# But for time performance and not timing out, I stopped looking for the best rewards and 
# I just return best first rewards.

# Everything is explained below.

class Assignment1:  # Do not change the name of this class!

    STUDENT_ID = Path(__file__).stem.split('_')[1]

    def removeUselessPush(self, expanded):

        # This function returned a cleaned list of state, if both PUSH and MOVE exist
        # Remove Push because its cost is higher.

        cleaned = []

        moves = {
            ActionType.MOVE_UP: [False, ActionType.PUSH_UP],
            ActionType.MOVE_LEFT: [False, ActionType.PUSH_LEFT],
            ActionType.MOVE_RIGHT: [False, ActionType.PUSH_RIGHT],
            ActionType.MOVE_DOWN: [False, ActionType.PUSH_DOWN]
        }

        # Loop over all possible moves, if it found one, set its array[0] to True
        # I use an Array because Tuple are immutable.

        # Then if its not in the dictionnary key, its obvioulsy a push, so check
        # if Its own move has been set to true, if TRUE dont use it because we found a move
        # Otherwise, push the PUSH

        for state in reversed(expanded):
            if state[0].action in moves:
                moves[state[0].action][0] = True
                cleaned.append(state)
            else:
                for action in moves:
                    if state[0].action == moves[action][1] and moves[action][0] == False:
                        cleaned.append(state)
                        break
        return cleaned
     
    def search(self, problem: SokobanProblem) -> List[ActionType]:

        reached = []            # Contains all known and checked nodes.
        noCurrentPrio = []      # Contains nodes which could be interesting to dig in but not now.

        # Initalize the first node to be expanded with the initial state
        # And set the best answer to None cause it has not been found yet.

        finalState = problem.initial_state
        bestsWays = None
        
        # Im currently using a infinite loop because this algorithm shall always find a solution
        # Because in case if none optimals solutions are found, it will just try every existing nodes.
        # Only issue could be timing out on real hard problems.

        while True:

            # On this loop occurence, for now, the searching node hasnt been changed.
            change = False

            # Get all children from a node, (if MOVE and PUSH are both possible, take only moves because at the end
            # Its the same as push, but with better reward)

            children = self.removeUselessPush(problem.expand(finalState))
            
            # Loop over children of the last interesting found node.

            for child, _ in children:

                # If the child has already been reached, no need to compute it.

                if child in reached:
                    continue

                # append to reached, so never computing it again.

                reached.append(child)  

                # If this is a goal state, it should contain a nice reward because its our
                # main criteria to dig it, so return it, if we dig in more in the possibilities
                # it might timeout, so its safer, otherwise we could just do this until we get the stronger final reward.

                if problem.is_goal_state(child):
                    return child.get_action_sequence()

                # If not a goal state but it has interesting Reward
                # At first, i was checking the depth too but score is more important than depth so I removed it.
                # Set the current searching node with it and set change to True to tell
                # the infite loop that the current searching node has changed, and break to continue
                # searching in this current child's node.

                if child.reward_so_far >= finalState.reward_so_far:
                    change = True
                    finalState = child
                    break           

                # Else, just append the child to an array to dig in later.

                else:
                    noCurrentPrio.append(child)

            # After looping on the node, if a child is interesting (change == true)
            # Check if all interesting nodes has been tested and that a solution has been found
            # if yes, return the solution

            if not change:
                if finalState.parent:
                    finalState = finalState.parent
                if len(noCurrentPrio) > 0:
                    finalState = noCurrentPrio.pop(0)

            # Else, if no solution has been found, no changed on the searching node
            # and our list of nodes to dig in is empty, use the least interesting nodes to dig in.
            
            if bestsWays and finalState == problem.initial_state and len(noCurrentPrio) == 0:
                return bestsWays.get_action_sequence()