"""The Transmission Queue is a max heap of messages to be transmitted.

Messages must support the `__lt__`, `__le__`, `__eq__`, `__ge__`, and `__gt__` operators.
This enables to the max heap to compare messages based on their priority.
"""
# from . import priority_queue as pq
from .priority_queue import PriorityQueue

transmission_queue = PriorityQueue([], 100)
