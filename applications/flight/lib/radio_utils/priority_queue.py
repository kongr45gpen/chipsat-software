# Based on CPython's heapq
# Converted to a max heap, and greatly simplified
# https://github.com/python/cpython/blob/3.10/Lib/heapq.py
""" Priority Queue Algorithm

Usage:

>>> heap = []         # creates an empty heap
>>> push(heap, item)  # pushes a new item on the heap
>>> item = pop(heap)  # pops the largest item from the heap
>>> item = heap[0]    # largest item on the heap without popping it
>>> heapify(x)        # transforms list into a heap, in-place, in linear time
"""

__all__ = ['push', 'pop', 'heapify']

def push(heap, item):
    """Push item onto heap, maintaining the heap invariant.

    :param heap: The heap to push the item onto
    :type heap: list
    :param item: Any well ordered item
    """
    heap.append(item)
    _siftdown_max(heap, 0, len(heap) - 1)

def pop(heap):
    """Pop the largest item off the heap, maintaining the heap invariant.

    :param heap: The heap to pop the item from
    :type heap: list
    """
    lastelt = heap.pop()    # raises appropriate IndexError if heap is empty
    if heap:
        returnitem = heap[0]
        heap[0] = lastelt
        _siftup_max(heap, 0)
        return returnitem
    return lastelt

def heapify(heap):
    """Transform list into a maxheap, in-place, in O(len(x)) time.

    :param heap: The list to heapify
    :type heap: list
    """
    n = len(heap)
    for i in reversed(range(n // 2)):
        _siftup_max(heap, i)
    return heap

def _siftdown_max(heap, startpos, pos):
    'Maxheap variant of _siftdown'
    newitem = heap[pos]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    while pos > startpos:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        if parent < newitem:
            heap[pos] = parent
            pos = parentpos
            continue
        break
    heap[pos] = newitem

def _siftup_max(heap, pos):
    'Maxheap variant of _siftup'
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    # Bubble up the larger child until hitting a leaf.
    childpos = 2 * pos + 1    # leftmost child position
    while childpos < endpos:
        # Set childpos to index of larger child.
        rightpos = childpos + 1
        if rightpos < endpos and not heap[rightpos] < heap[childpos]:
            childpos = rightpos
        # Move the larger child up.
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2 * pos + 1
    # The leaf at pos is empty now.  Put newitem there, and bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = newitem
    _siftdown_max(heap, startpos, pos)


class PriorityQueue:

    def __init__(self) -> None:
        self.queue = []

    def push(self, item):
        """Push item onto heap, maintaining the heap invariant.

        :param heap: The heap to push the item onto
        :type heap: list
        :param item: Any well ordered item
        """
        self.queue.append(item)
        _siftdown_max(0, len(self.queue) - 1)

    def pop(self):
        """Pop the largest item off the heap, maintaining the heap invariant.

        :param heap: The heap to pop the item from
        :type heap: list
        """
        lastelt = self.queue.pop()    # raises appropriate IndexError if heap is empty
        if self.queue:
            returnitem = self.queue[0]
            self.queue[0] = lastelt
            self._siftup_max(0)
            return returnitem
        return lastelt

    def heapify(self):
        """Transform list into a maxheap, in-place, in O(len(x)) time.

        :param heap: The list to heapify
        :type heap: list
        """
        n = len(self.queue)
        for i in reversed(range(n // 2)):
            self._siftup_max(i)

    def _siftdown_max(self, startpos, pos):
        'Maxheap variant of _siftdown'
        newitem = self.queue[pos]
        # Follow the path to the root, moving parents down until finding a place
        # newitem fits.
        while pos > startpos:
            parentpos = (pos - 1) >> 1
            parent = self.queue[parentpos]
            if parent < newitem:
                self.queue[pos] = parent
                pos = parentpos
                continue
            break
        self.queue[pos] = newitem

    def _siftup_max(self, pos):
        'Maxheap variant of _siftup'
        endpos = len(self.queue)
        startpos = pos
        newitem = self.queue[pos]
        # Bubble up the larger child until hitting a leaf.
        childpos = 2 * pos + 1    # leftmost child position
        while childpos < endpos:
            # Set childpos to index of larger child.
            rightpos = childpos + 1
            if rightpos < endpos and not self.queue[rightpos] < self.queue[childpos]:
                childpos = rightpos
            # Move the larger child up.
            self.queue[pos] = self.queue[childpos]
            pos = childpos
            childpos = 2 * pos + 1
        # The leaf at pos is empty now.  Put newitem there, and bubble it up
        # to its final resting place (by sifting its parents down).
        self.queue[pos] = newitem
        self._siftdown_max(startpos, pos)
