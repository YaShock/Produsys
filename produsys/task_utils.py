def get_subtasks(parent_id, all_tasks):
    tasks = []
    for task in all_tasks:
        if task.parent_id == parent_id:
            tasks.append(task)
    for task in tasks:
        task.subtasks = get_subtasks(task.id, all_tasks)
    return tasks


def get_hierarchical_tasks(project_id, all_tasks):
    tasks = []
    for task in all_tasks:
        if task.parent_id is None and task.project.id == project_id:
            tasks.append(task)
    for task in tasks:
        task.subtasks = get_subtasks(task.id, all_tasks)
    return tasks


def set_task_full_paths(tasks):
    def task_full_path(task):
        if task.parent_id:
            return task_full_path(task.parent) + ' > ' + task.name
        return task.project.name + ' > ' + task.name

    for task in tasks:
        task.full_path = task_full_path(task)
