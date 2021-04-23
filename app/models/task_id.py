from uuid import UUID

from odmantic import Model


class TaskId(Model):
    task_id: str
