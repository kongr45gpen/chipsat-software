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


class PriorityQueue:
    """
    For this to work the types being stored in the priority queue need to be
    well-ordered as we use comparison operations. This should be done by storing
    data belonging to some class which has a self.priority value.
    """

    def __init__(self, queue, limit=1000) -> None:
        self.queue = queue
        self.limit = limit

        n = len(self.queue)
        for i in reversed(range(n // 2)):
            self.__siftup_max(i)

    def push(self, item) -> None:
        """Push item onto heap, maintaining the heap invariant.

        :param heap: The heap to push the item onto
        :type heap: list
        :param item: Any well ordered item
        """
        if len(self.queue) < self.limit:
            self.queue.append(item)
            self.__siftdown_max(0, len(self.queue) - 1)
        else:
            raise Exception("Queue is full")


    def pop(self):
        """Pop the largest item off the heap, maintaining the heap invariant.

        :param heap: The heap to pop the item from
        :type heap: list
        """
        lastelt = self.queue.pop()    # raises appropriate IndexError if heap is empty
        if self.queue:
            returnitem = self.queue[0]
            self.queue[0] = lastelt
            self.__siftup_max(0)
            return returnitem
        return lastelt

    def heapify(self) -> None:
        """Transform list into a maxheap, in-place, in O(len(x)) time.

        :param heap: The list to heapify
        :type heap: list
        """
        n = len(self.queue)
        for i in reversed(range(n // 2)):
            self.__siftup_max(i)

    def size(self) -> int:
        return len(self.queue)
    
    def peek(self):
        return self.queue[0]
    
    def clear(self) -> None:
        self.queue = []

    def empty(self) -> bool:
        return len(self.queue) == 0

    # private methods
    def __siftdown_max(self, startpos, pos) -> None:
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

    def __siftup_max(self, pos) -> None:
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
        self.__siftdown_max(startpos, pos)

    def __str__(self) -> str:
        s = '['
        for idx, item in enumerate(self.queue):
            s += f'(idx: {idx}, priority: {item.priority}, {item.contents})'
        s += ']'
        return s
