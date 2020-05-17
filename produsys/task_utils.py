def get_subtasks(parent_id, all_tasks):
    tasks = []
    for task in all_tasks:
        if task.parent and task.parent.id == parent_id:
            tasks.append(task)
    for task in tasks:
        task.subtasks = get_subtasks(task.id, all_tasks)
    return tasks


def get_hierarchical_tasks(project_id, all_tasks):
    tasks = []
    for task in all_tasks:
        if task.parent is None and task.project.id == project_id:
            tasks.append(task)
    for task in tasks:
        task.subtasks = get_subtasks(task.id, all_tasks)
    return tasks
