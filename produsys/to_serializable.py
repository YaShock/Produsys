from functools import singledispatch
from produsys.db import Project, Task, TaskChunk


@singledispatch
def to_serializable(obj):
    return str(obj)


@to_serializable.register(Project)
def ts_project(obj):
    to_serialize = {
        'id': obj.id,
        'user_id': obj.user_id,
        'name': obj.name,
        'total_duration': obj.total_duration
    }
    return to_serialize


@to_serializable.register(Task)
def ts_task(obj):
    to_serialize = {
        'id': obj.id,
        'name': obj.name,
        'project_id': obj.project.id,
        'parent_id': obj.parent.id if obj.parent else None,
        'started': obj.started,
        'start_time': obj.start_time,
        'total_duration': obj.total_duration
    }
    return to_serialize


@to_serializable.register(TaskChunk)
def ts_task_chunk(obj):
    to_serialize = {
        'id': obj.id,
        'task_id': obj.task_id,
        'task_name': obj.task_name,
        'start': obj.start,
        'end': obj.end,
        'duration': obj.duration
    }
    return to_serialize
