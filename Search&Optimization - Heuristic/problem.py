import math
import logging
import numpy as np
import networkx as nx

from itertools import combinations, permutations
from typing import List, Tuple
from os import getpid
from psutil import Process as PUInfo


SURNAMES = [
    "Williams", "Harris", "Thomas", "Robinson", "Walker", "Scott", "Nelson", "Mitchell", "Morgan", "Cooper", "Howard",
    "Davis", "Miller", "Martin", "Smith", "Anderson", "White", "Perry", "Clark", "Richards", "Wheeler", "Warburton",
    "Stanley", "Holland", "Terry", "Shelton", "Miles", "Lucas", "Fletcher", "Parks", "Norris", "Guzman", "Daniel",
    "Newton", "Potter", "Francis", "Erickson", "Norman", "Moody", "Lindsey", "Gross", "Sherman", "Simon", "Jones",
    "Brown", "Garcia", "Rodriguez", "Lee", "Young", "Hall", "Allen", "Lopez", "Green", "Gonzalez", "Baker", "Adams",
    "Perez", "Campbell", "Shaw", "Gordon", "Burns", "Warren", "Long", "Mcdonald", "Gibson", "Ellis", "Fisher",
    "Reynolds", "Jordan", "Hamilton", "Ford", "Graham", "Griffin", "Russell", "Foster", "Butler", "Simmons", "Flores",
    "Bennett", "Sanders", "Hughes", "Bryant", "Patterson", "Matthews", "Jenkins", "Watkins", "Ward", "Murphy", "Bailey",
    "Bell", "Cox", "Martinez", "Evans", "Rivera", "Peterson", "Gomez", "Murray", "Tucker", "Hicks", "Crawford", "Mason",
    "Rice", "Black", "Knight", "Arnold", "Wagner", "Mosby", "Ramirez", "Coleman", "Powell", "Singh", "Patel", "Wood",
    "Wright", "Stephens", "Eriksen", "Cook", "Roberts", "Holmes", "Kennedy", "Saunders", "Fisher", "Hunter", "Reid",
    "Stewart", "Carter", "Phillips", "Spencer", "Howell", "Alvarez", "Little", "Jacobs", "Foreman", "Knowles",
    "Meadows", "Richmond", "Valentine", "Dudley", "Woodward", "Weasley", "Livingston", "Sheppard", "Kimmel", "Noble",
    "Leach", "Gentry", "Lara", "Pace", "Trujillo", "Grant"
]

PLACE_NAMES = [
    "House", "Building", "Company", "Market", "School", "Hospital", "Library", "Store", "Pharmacy", "CVS", "Tower",
    "Hotel", "Museum", "Mosque", "Palace", "Zoo", "Windmill", "Stadium", "Lighthouse", "Cafe", "Club", "Temple",
    "Port", "Hall", "Church", "Bridge", "Casino", "Castle", "Aquarium", "Gym", "Wall", "Gallery", "Street"
]

ADJECTIVES = [
    "adorable", "adventurous", "aggressive", "agreeable", "alert", "alive", "amused", "angry", "annoyed", "annoying",
    "anxious", "arrogant", "ashamed", "attractive", "average", "awful", "bad", "beautiful", "better", "bewildered",
    "black", "bloody", "blue",
    "blushing", "bored", "brainy", "brave", "breakable", "bright", "busy", "calm", "careful", "cautious", "charming",
    "cheerful", "clean", "clear", "clever", "cloudy", "clumsy", "colorful", "combative", "comfortable", "concerned",
    "condemned", "confused", "cooperative", "courageous", "crazy", "creepy", "crowded", "cruel", "curious", "cute",
    "dangerous", "dark", "dead", "defeated", "defiant", "delightful", "depressed", "determined", "different",
    "difficult", "disgusted", "distinct", "disturbed", "dizzy", "doubtful", "drab", "dull", "eager", "easy", "elated",
    "elegant", "embarrassed", "enchanting", "encouraging", "energetic", "enthusiastic", "envious", "evil", "excited",
    "expensive", "exuberant", "fair", "faithful", "famous", "fancy", "fantastic", "fierce", "filthy", "fine", "foolish",
    "fragile", "frail", "frantic", "friendly", "frightened", "funny", "gentle", "gifted", "glamorous", "gleaming",
    "glorious", "good", "gorgeous", "graceful", "grieving", "grotesque", "grumpy", "handsome", "happy", "healthy",
    "helpful", "helpless", "hilarious", "homeless", "homely", "horrible", "hungry", "hurt", "ill", "important",
    "impossible", "inexpensive", "innocent", "inquisitive", "itchy", "jealous", "jittery", "jolly", "joyous", "kind",
    "lazy", "light", "lively", "lonely", "long", "lovely", "lucky", "magnificent", "misty", "modern", "motionless",
    "muddy", "mushy", "mysterious", "nasty", "naughty", "nervous", "nice", "nutty", "obedient", "obnoxious", "odd",
    "open", "outrageous", "outstanding", "panicky", "perfect", "plain", "pleasant", "poised", "poor", "powerful",
    "precious", "prickly", "proud", "putrid", "puzzled", "quaint", "real", "relieved", "repulsive", "rich", "scary",
    "selfish", "shiny", "shy", "silly", "sleepy", "smiling", "smoggy", "sore", "sparkling", "splendid", "spotless",
    "stormy", "strange", "stupid", "successful", "super", "talented", "tame", "tasty", "tender", "tense", "terrible",
    "thankful", "thoughtful", "thoughtless", "tired", "tough", "troubled", "ugliest", "ugly", "uninterested",
    "unsightly", "unusual", "upset", "uptight", "vast", "victorious", "vivacious", "wandering", "weary", "wicked",
    "wild", "witty", "worried", "worrisome", "wrong", "zany", "zealous"
]


def _generate_places(n: int, rng) -> List[str]:
    places = set()
    while len(places) < n:
        surname = SURNAMES[rng.choice(len(SURNAMES))]
        adjective = ADJECTIVES[rng.choice(len(ADJECTIVES))]
        place = PLACE_NAMES[rng.choice(len(PLACE_NAMES))]

        name = f'{surname}\'s {adjective} {place}'
        places.add(name)

    places = sorted(places)
    rng.shuffle(places)
    return places


def _distance(a: tuple, b: tuple) -> float:
    a1, a2 = a
    b1, b2 = b
    return math.sqrt((a1 - b1) ** 2 + (a2 - b2) ** 2)


def _cut_off_value(f: float) -> float:
    return math.ceil(f * 128) / 128


def safe_shortest_path_length(g, s, t) -> int:
    try:
        return nx.shortest_path_length(g, s, t)
    except nx.NetworkXNoPath:
        return -1


class RandomGeometricGraphProblem:
    def __init__(self):
        self.__random = np.random.Generator(np.random.PCG64(5606))
        self.__graph = None
        self.__is_solvable = False
        self.__places_to_visit: List[str] = []
        self.__subproblems = []
        self.__pu_process_tracker = PUInfo(getpid())
        self.__memory_usage = 0
        self.__update_memory_usage()

    @property
    def initial_state(self) -> str:
        return self.__places_to_visit[0]

    @property
    def places_to_visit(self) -> Tuple[str]:
        return tuple(self.__places_to_visit)

    def all_place_names(self) -> List[str]:
        self.__update_memory_usage()
        return [n for n in self.__graph.nodes]

    def get_position_of(self, state: str) -> Tuple[float, float]:
        self.__update_memory_usage()
        return self.__graph.nodes[state]['pos']

    def get_cost_of(self, state1: str, state2: str, cost_type: str) -> float:
        self.__update_memory_usage()
        try:
            return self.__graph[state1][state2][cost_type]
        except:
            return float('inf')

    def get_max_memory_usage(self):
        return self.__memory_usage

    def get_current_memory_usage(self):
        return self.__pu_process_tracker.memory_info().rss

    def __update_memory_usage(self):
        self.__memory_usage = max(self.__memory_usage, self.get_current_memory_usage())

    def reset_for_eval(self, subproblems: int) -> list:
        # Random graph generation. This code will be changed to other distributions in evaluation.
        n = self.__random.integers(100, 2000)
        radius = self.__random.random() * 0.2 + 0.2  # 0.2 ~ 0.4
        pos = {i: (self.__random.uniform(0, 5), self.__random.uniform(0, 5))
               for i in range(n)}
        names = _generate_places(n, self.__random)
        geo_graph = nx.soft_random_geometric_graph(n, radius, pos=pos)
        named_graph = nx.DiGraph()

        # Set name of the graph
        named_graph.add_nodes_from([(name, {'pos': geo_graph.nodes[n]['pos']})
                                    for n, name in enumerate(names)])

        # Set road distance for the graph
        for a, b in geo_graph.edges:
            conn_type = self.__random.random()
            geo_dist_ab = _distance(geo_graph.nodes[a]['pos'], geo_graph.nodes[b]['pos'])
            distance_ab = _cut_off_value(geo_dist_ab * (self.__random.random() * 0.4 + 1.2))
            speed_ab = .25 + self.__random.random() * .25
            a = names[a]
            b = names[b]

            if conn_type < 0.05:
                named_graph.add_edge(a, b, road=distance_ab, time=_cut_off_value(distance_ab / speed_ab), fee=0)
            elif conn_type < 0.1:
                named_graph.add_edge(b, a, road=distance_ab, time=_cut_off_value(distance_ab / speed_ab), fee=0)
            elif conn_type < 0.3:
                distance_ba = geo_dist_ab * (self.__random.random() * 0.4 + 1.2)
                named_graph.add_edges_from([(a, b, {'road': distance_ab,
                                                    'time': _cut_off_value(distance_ab / speed_ab), 'fee': 0}),
                                            (b, a, {'road': distance_ba,
                                                    'time': _cut_off_value(distance_ba / speed_ab), 'fee': 0})])
            else:
                named_graph.add_edges_from([(a, b, {'road': distance_ab,
                                                    'time': _cut_off_value(distance_ab / speed_ab), 'fee': 0}),
                                            (b, a, {'road': distance_ab,
                                                    'time': _cut_off_value(distance_ab / speed_ab), 'fee': 0})])

        # Add highways randomly between strongly connected components
        scc = list(nx.strongly_connected_components(named_graph))
        for c1, c2 in combinations(scc, r=2):
            if self.__random.random() < 0.3:  # 30% prob.
                pair_with_dist = [(a, b, _distance(named_graph.nodes[a]['pos'], named_graph.nodes[b]['pos']))
                                  for a in c1 for b in c2]
                pair_probs = [math.exp(-p) for _, _, p in pair_with_dist]
                pair_probs = [p / sum(pair_probs) for p in pair_probs]
                if len(pair_with_dist) > 1:
                    choices = self.__random.choice(len(pair_with_dist), p=pair_probs, replace=False,
                                                   size=self.__random.integers(1, min(4, len(pair_with_dist))))
                else:
                    choices = [0]

                for p in choices:
                    a, b, geo_dist_ab = pair_with_dist[p]
                    distance_ab = geo_dist_ab * (self.__random.random() * 0.4 + 1.2)
                    speed_ab = 1.0 + self.__random.random() * .2
                    named_graph.add_edges_from([(a, b, {'road': _cut_off_value(distance_ab),
                                                        'time': _cut_off_value(distance_ab / speed_ab),
                                                        'fee': int(100 * math.ceil(distance_ab * 10))}),
                                                (b, a, {'road': _cut_off_value(distance_ab),
                                                        'time': _cut_off_value(distance_ab / speed_ab),
                                                        'fee': int(100 * math.ceil(distance_ab * 10))})])

        # Set positions to visit (try 10 times to find a path.)
        shortest_path_lengths = dict(nx.shortest_path_length(named_graph))
        degrees = [d for _, d in named_graph.degree(names)]
        prop_deg = [d / sum(degrees) for d in degrees]
        place_to_visit = []
        while len(place_to_visit) < subproblems:
            starting_point = names[self.__random.choice(len(names), p=prop_deg)]
            connected_nodes = [n for n, d in shortest_path_lengths[starting_point].items() if d > 10]
            all_nodes = [n for n in names if starting_point != n]

            target_list = (connected_nodes if connected_nodes else all_nodes)
            end_point = target_list[self.__random.choice(len(target_list))]

            place_to_visit.append((nx.has_path(named_graph, starting_point, end_point),
                                   [starting_point, end_point]))

        self.__graph = named_graph
        self.__places_to_visit = place_to_visit

        problem_spec = [[(n, data) for n, data in named_graph.nodes(data=True)],
                        [(a, b, data) for a, b, data in named_graph.edges(data=True)],
                        self.__places_to_visit.copy()]

        logging.debug(f'Graph generated with {n} nodes, {self.__graph.number_of_edges()} edges.')
        logging.debug(f'Maximum degree: {max(d for _, d in self.__graph.degree)}')
        logging.debug(f'Places to visit: {len(place_to_visit)}')

        self.__update_memory_usage()
        return problem_spec

    def restore_for_eval(self, spec, sub_id: int):
        if spec is not None:
            nodes, edges, subproblem = spec
            self.__graph = nx.DiGraph()
            self.__graph.add_nodes_from(nodes)
            self.__graph.add_edges_from(edges)
            self.__subproblems = subproblem

        self.__is_solvable, self.__places_to_visit = self.__subproblems[sub_id]
        self.__memory_usage = 0
        self.__update_memory_usage()

    def expand(self, state: str) -> List[Tuple[str, dict]]:
        next_state_map = []
        for next_state in self.__graph.successors(state):
            road_cost = self.__graph[state][next_state]['road']
            time_cost = self.__graph[state][next_state]['time']
            fee_cost = self.__graph[state][next_state]['fee']
            next_state_map.append((next_state, dict(road=road_cost, time=time_cost, fee=fee_cost)))

        self.__update_memory_usage()
        return next_state_map

    def is_solution_path(self, path: List[str]) -> bool:
        self.__update_memory_usage()
        return path[0] == self.__places_to_visit[0] \
            and path[-1] == self.__places_to_visit[-1]

    def execute(self, actions: List[str]) -> Tuple[dict, str, bool]:
        done = self.is_solution_path(actions) or (len(actions) == 0 and not self.__is_solvable)
        no_edge_between = None
        dist_cost = 0
        time_cost = 0
        fee_cost = 0
        for a, b in zip(actions[:-1], actions[1:]):
            if self.__graph.has_edge(a, b):
                dist_cost += self.__graph[a][b]['road']
                time_cost += self.__graph[a][b]['time']
                fee_cost += self.__graph[a][b]['fee']
            else:
                no_edge_between = f'No edge between {a} and {b}!'
                dist_cost = float('inf')
                time_cost = float('inf')
                fee_cost = float('inf')

        self.__update_memory_usage()
        return {'road': dist_cost, 'time': time_cost, 'fee': fee_cost}, no_edge_between, done


__ALL__ = ['RandomGeometricGraphProblem']
