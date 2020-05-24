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
