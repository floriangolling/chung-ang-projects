import math
from pathlib import Path

from search.load import get_student_assignments
from problem import SokobanProblem
from time import process_time, time, sleep
from collections import defaultdict
from traceback import format_exc
from importlib import import_module
from multiprocessing import Process, Queue, TimeoutError
from os import cpu_count

import logging
import numpy as np


def evaluate_algorithm(alg_spec, problem_spec, result_queue: Queue):
    logging.getLogger('gym').setLevel(logging.ERROR)
    problem = SokobanProblem()
    problem.restore_for_eval(problem_spec)

    # Initialize algorithm
    if alg_spec is not None:
        alg_cls = import_module(f'search.search_{alg_spec}').Assignment1
    else:
        from search.bfs import Assignment1
        alg_cls = Assignment1
    print(f'Start to execute {alg_cls.STUDENT_ID}.')

    # Begin to measure time
    time_start = process_time()
    algorithm = alg_cls()
    print(f'Initialize complete: {alg_cls.STUDENT_ID}.')

    # Do search
    solution = None
    score, done, steps, failure = None, None, None, None
    try:
        solution = algorithm.search(problem)
        if solution is None:
            failure = 'None returned! (Did you implemented the algorithm?)'
    except:
        failure = format_exc()

    # Get the end time
    time_end = process_time()
    print(f'Searching complete: {alg_cls.STUDENT_ID}.')

    # Execute the solution
    if solution is not None:
        try:
            score, done, steps = problem.execute(solution)

            if not done:
                failure = 'The solution does not reach a goal state!'
        except:
            failure = format_exc()

    print(f'Result of {alg_cls.STUDENT_ID}: Failure {not not failure}, {score}, {time_end - time_start}, {steps}')
    result_queue.put((algorithm.STUDENT_ID, failure, score, time_end - time_start, steps))


if __name__ == '__main__':
    logging.getLogger('gym').setLevel(logging.ERROR)

    prob_generator = SokobanProblem()
    search_algorithms = get_student_assignments()

    time_measures = defaultdict(list)
    score_measures = defaultdict(list)
    step_measures = defaultdict(list)
    failures = defaultdict(list)
    def _print(trial):
        measure_aggregated = [(key, (-len(failures[key]),
                                     float(np.mean(score_measures[key]) if len(score_measures[key]) else float('-inf')),
                                     -float(np.mean(time_measures[key]) if len(time_measures[key]) else float('inf')),
                                     -float(np.mean(step_measures[key]) if len(step_measures[key]) else float('inf'))),
                               failures[key])
                              for key in set().union(time_measures.keys(), failures.keys())]
        measure_aggregated = sorted(measure_aggregated, key=lambda x: x[1], reverse=True)

        print(f'Current trial: {trial}/100')
        print('\n Rank  Student ID   Score   Time(s)   Steps   Failures | Percentile')
        print('=' * 55 + '|' + '=' * 11)
        previous_item = None
        rank = 0
        percentile = 0
        for i, (key, (f, s, t, st), failure_list) in enumerate(measure_aggregated):
            if previous_item != (f, s, t, st):
                previous_item = (f, s, t, st)
                rank = i + 1  # Set the current index as rank
                percentile = int(rank / len(measure_aggregated) * 100)
                if rank % 5 == 0:
                    print('-' * 55 + '|' + '-' * 11)

            print(f'#{rank:2d}    {key:10s}  {s:7.2f}  {-t:7.2f}  {-st:7.2f}  {-f:8d} |  {percentile:3d}th/100')

            # Write-down the failures
            with Path(f'./failure_{key}.txt').open('w+t') as fp:
                fp.write('\n\n'.join(failure_list))

    # Start evaluation process (using multi-processing)
    process_results = Queue()
    process_count = max(cpu_count() - 2, 1)
    def _execute(prob, alg):
        proc = Process(name=f'EvalProc', target=evaluate_algorithm, args=(alg, prob, process_results), daemon=True)
        proc.start()
        proc.alg_id = alg if alg is not None else '__BFS__'
        return proc

    for trial in range(25):
        prob_spec = prob_generator.reset_for_eval()
        print(f'Trial {trial} begins...')

        # Execute BFS first (to compute time limit)
        bfs_start = time()
        bfs_p = _execute(prob_spec, None)
        bfs_p.join()
        bfs_end = time()

        time_limit = math.ceil((bfs_end - bfs_start) * 100)
        print(f'Time limit for the trial {trial}: {time_limit} sec')

        # Execute other algorithms
        processes = []
        algorithms_to_run = search_algorithms.copy()
        timeouts = set()  # Timeout by default
        while algorithms_to_run or processes:
            if algorithms_to_run and len(processes) < process_count:
                alg = algorithms_to_run.pop()
                processes.append((_execute(prob_spec, alg), time()))

            new_proc_list = []
            for p, begin in processes:
                if not p.is_alive():
                    continue
                if begin + time_limit < time():
                    p.terminate()
                    timeouts.add(p.alg_id)
                    print(f'[TIMEOUT] {p.alg_id} / '
                          f'Process is running more than {time_limit} sec, from ts={begin}; now={time()}')
                else:
                    new_proc_list.append((p, begin))
            processes = new_proc_list

            if len(processes) >= process_count:
                # Wait for one seconds
                sleep(1)

        # Read results
        result_not_logged = set(search_algorithms)
        while not process_results.empty():
            alg_id, f, s, t, st = process_results.get()
            if alg_id not in timeouts:
                if alg_id in result_not_logged:
                    result_not_logged.remove(alg_id)
                if f is None:
                    time_measures[alg_id].append(t)
                    score_measures[alg_id].append(s)
                    step_measures[alg_id].append(st)
                else:
                    failures[alg_id].append(f'Trial #{trial}: ' + f)

        # Add timeouts
        for alg_id in timeouts:
            failures[alg_id].append(f'Trial #{trial}: Time out!')
            result_not_logged.remove(alg_id)

        for alg_id in result_not_logged:
            failures[alg_id].append(f'Trial #{trial}: Process terminated by unexpected way!')

        _print(trial)
