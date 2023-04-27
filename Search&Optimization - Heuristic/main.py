import logging
import math
import random
from itertools import permutations
from collections import defaultdict
from importlib import import_module
from multiprocessing import Process, Queue
from os import cpu_count
from pathlib import Path
from time import time, sleep
from traceback import format_exc

import psutil as pu

from problem import RandomGeometricGraphProblem
from search.load import get_student_assignments

KILOBYTES = 1024
MEMORY_LIMIT = 1024 ** 3  # in bytes (1GB)
TIME_LIMIT = 1800  # in seconds
SUBPROBLEMS = 1
PROBLEMS = 50

CRITERIA = list(permutations(['road', 'time', 'fee'])) + \
           list(permutations(['road', 'time', 'fee'], r=2)) + \
           [['road'], ['time'], ['fee']]


def evaluate_algorithm(alg_spec, problem_spec, ranking_criteria, result_queue: Queue):
    time_limit = int(time() + TIME_LIMIT)
    problem = RandomGeometricGraphProblem()
    problem.restore_for_eval(problem_spec, 0)
    init_memory = problem.get_current_memory_usage()

    # Initialize algorithm
    if alg_spec is not None:
        module = import_module(f'search.search_{alg_spec}')
    else:
        import search.bfs as module

    search_algorithm = module.Assignment(problem)
    student_id = module.STUDENT_ID

    logger = logging.getLogger(student_id)
    logger.setLevel(logging.INFO)
    logger.debug('Initialized.')

    for sub in range(len(problem_spec[-1])):
        problem.restore_for_eval(None, sub)

        # Do search
        solution = None
        score_dict, done, failure = {}, None, None
        try:
            solution = search_algorithm.search(ranking_criteria, time_limit)
            if solution is None:
                failure = 'None returned! (Did you implemented the algorithm?)'
        except:
            failure = format_exc()

        logger.debug(f'Search finished.')

        # Execute the solution
        if solution is not None:
            try:
                score_dict, failure, done = problem.execute(solution)

                if not done:
                    if failure:
                        failure = failure + '; '
                    else:
                        failure = ''
                    failure += f'The solution does not reach a goal state! ' \
                               f'\n\tRequired: {problem.places_to_visit}\n\tReturned: {solution}'
            except:
                failure = format_exc()

        score_dict.update(memory=max(problem.get_max_memory_usage() - init_memory, 0))
        logger.debug(f'Result: Failure {not not failure}, {score_dict}')
        result_queue.put((student_id, sub, failure, score_dict))


if __name__ == '__main__':
    # Note: If you want to see some logged result, change logging.INFO to logging.DEBUG
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    prob_generator = RandomGeometricGraphProblem()
    search_algorithms = get_student_assignments()

    points = defaultdict(lambda: 0)
    failures = defaultdict(list)


    def _give_rank_scores(ranking):
        prev_item = None
        rank = 0
        for i, rank_info in enumerate(ranking):
            rank_tuple = rank_info['rank_tuple'] + (rank_info['memory'],)
            if prev_item != rank_tuple:
                prev_item = rank_tuple
                rank = i + 1

            if rank_info.get('failure', False):
                # No points will be added
                failures[rank_info['id']].append(rank_info['failure'])
                score = 0
            else:
                score = len(ranking) - rank

            rank_info['score'] = score
            points[rank_info['id']] += score


    def _print(t, s, ranking, criteria):
        print(f'\nCurrent problem: #{t} with criteria: {criteria} / Subproblem {s+1} of {SUBPROBLEMS}')
        print(f' StudentID    | Dist@{s+1:03d}  Time@{s+1:03d}  Fee@{s+1:03d}  Mem@{s+1:03d}  Score@{s+1:03d} |'
              f' TotalScore  Rank  Percentile')
        # 9, 8, 8, 7, 7, 9, 5, 4, 10
        print('=' * 14 + '|' + '=' * 49 + '|' + '=' * 29)

        total_rank_now = {}
        total_rank = 0
        total_score_prev = None
        for i, (_id, _score) in enumerate(sorted(points.items(), key=lambda d: d[1], reverse=True)):
            if total_score_prev != _score:
                total_rank = i + 1
                total_score_prev = _score
            total_rank_now[_id] = (total_rank, _score)

        for rank_info in ranking:
            key = rank_info['id']
            key_print = key if len(key) < 13 else key[:9] + '...'
            t_rank, t_score = total_rank_now[key]
            percentile = int(t_rank / len(ranking) * 100)
            print(f' {key_print:12s} | {rank_info.get("road", float("inf")):8.4f} '
                  f' {rank_info.get("time", float("inf")):8.4f}  {rank_info.get("fee", float("inf")):7.0f} '
                  f' {rank_info["memory"] / KILOBYTES:7.1f}  {rank_info["score"]:9d} |'
                  f' {t_score:10d}  {t_rank:4d}  {percentile:3d}th/100')

            # Write-down the failures
            with Path(f'./failure_{key}.txt').open('w+t') as fp:
                fp.write('\n\n'.join(failures[key]))


    # Start evaluation process (using multi-processing)
    process_results = Queue()
    process_count = max(cpu_count() - 2, 1)


    def _execute(prob, alg, crit):
        proc = Process(name=f'EvalProc', target=evaluate_algorithm, args=(alg, prob, crit, process_results), daemon=True)
        proc.start()
        proc.alg_id = alg if alg is not None else '__BFS__'
        return proc


    for trial in range(PROBLEMS):
        prob_spec = prob_generator.reset_for_eval(SUBPROBLEMS)
        ranking_criteria = tuple(random.choice(CRITERIA))
        logging.info(f'Trial {trial} begins, with ranking criteria: {ranking_criteria}')

        # Execute other algorithms
        results = {(k, s): {'id': k, 'failure': 'Unknown failure!',
                            'rank_tuple': tuple(float('inf') for k in ranking_criteria),
                            'memory': float('inf')}
                   for k in search_algorithms
                   for s in range(SUBPROBLEMS)}
        processes = []
        algorithms_to_run = search_algorithms.copy()
        random.shuffle(algorithms_to_run)

        exceed_limit = set()  # Timeout or Memory limit
        while algorithms_to_run or processes:
            if algorithms_to_run and len(processes) < process_count:
                alg = algorithms_to_run.pop()
                processes.append((_execute(prob_spec, alg, ranking_criteria), time()))

            new_proc_list = []
            for p, begin in processes:
                if not p.is_alive():
                    continue
                if begin + TIME_LIMIT < time():
                    p.terminate()
                    exceed_limit.add(p.alg_id)
                    logging.info(f'[TIMEOUT] {p.alg_id} / '
                                 f'Process is running more than {TIME_LIMIT} sec, from ts={begin}; now={time()}')
                else:
                    try:
                        p_bytes = pu.Process(p.pid).memory_info().rss
                        if p_bytes > MEMORY_LIMIT:
                            p.terminate()
                            exceed_limit.add(p.alg_id)
                            logging.info(f'[MEM LIMIT] {p.alg_id} / '
                                         f'Process consumed memory more than {MEMORY_LIMIT} sec (used: {p_bytes})')
                        else:
                            new_proc_list.append((p, begin))
                    except pu.NoSuchProcess:
                        if p.is_alive():
                            raise ValueError('PSUTIL has some problem')

            processes = new_proc_list

            if len(processes) >= process_count:
                # Wait for one seconds
                sleep(1)

        # Read results
        while not process_results.empty():
            alg_id, sub, f, s = process_results.get()
            if alg_id not in exceed_limit:
                if f is None:
                    s.update(rank_tuple=tuple(s.get(k, float('inf')) for k in ranking_criteria))
                    results[(alg_id, sub)].update(s)
                    results[(alg_id, sub)]['failure'] = False
                else:
                    results[(alg_id, sub)]['failure'] = f'Trial #{trial}: ' + f
            else:
                results[(alg_id, sub)]['failure'] = \
                    f'Trial #{trial}: Process was killed as time/memory usage reached the limit.'

        # Sort the results by rank criteria and memory
        for sub in range(SUBPROBLEMS):
            results_sub = [d for (_, s), d in results.items() if s == sub]
            results_sub = sorted(results_sub, key=lambda d: d['rank_tuple'] + (d['memory'],))
            _give_rank_scores(results_sub)
            _print(trial, sub, results_sub, ranking_criteria)
