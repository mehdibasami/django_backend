from enum import Enum


class RequestStatus(Enum):
    PENDING = 'Pending'
    REJECTED = 'Rejected'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'

    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]
