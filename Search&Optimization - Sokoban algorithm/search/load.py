from pathlib import Path


def get_student_assignments():
    assignments = []
    for search in Path(__file__).parent.glob('search_*.py'):
        assignments.append(search.stem.split('_')[1])

    return sorted(assignments)


__ALL__ = ['get_student_assignments']
