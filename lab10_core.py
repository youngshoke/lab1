from dataclasses import dataclass
from bisect import bisect_left
from time import perf_counter
import copy
import tracemalloc
from pyrsistent import pmap, pvector, pset, freeze, thaw, PRecord, field

@dataclass(frozen=True)
class PList:
    head: object = None
    tail: object = None

    def cons(self, value):
        return PList(value, self)

    @classmethod
    def from_iterable(cls, values):
        result = cls()
        for value in reversed(list(values)):
            result = result.cons(value)
        return result

    def __iter__(self):
        node = self
        while node.tail is not None:
            yield node.head
            node = node.tail

    def to_list(self):
        return list(self)

    def length(self):
        return sum(1 for _ in self)

    def nth(self, index):
        if index < 0:
            raise IndexError(index)
        return self.drop(index)._first()

    def _first(self):
        if self.tail is None:
            raise IndexError("empty")
        return self.head

    def take(self, count):
        from itertools import islice
        return PList.from_iterable(islice(self, max(0, count)))

    def drop(self, count):
        node = self
        for _ in range(count):
            if node.tail is None:
                break
            node = node.tail
        return node

    def map(self, f):
        return PList.from_iterable(map(f, self))

    def filter(self, f):
        return PList.from_iterable(filter(f, self))

    def fold_left(self, f, initial):
        from functools import reduce
        return reduce(f, self, initial)

    def fold_right(self, f, initial):
        return self.reverse().fold_left(lambda acc, x: f(x, acc), initial)

    def reverse(self):
        return self.fold_left(lambda acc, x: acc.cons(x), PList())

    def append(self, other):
        return self.fold_right(lambda x, acc: acc.cons(x), other)

@dataclass(frozen=True)
class Queue:
    front: PList = PList()
    back: PList = PList()
    size: int = 0

    def enqueue(self, x):
        return Queue(self.front, self.back.cons(x), self.size + 1)

    def dequeue(self):
        front, back = self.front, self.back
        if front.tail is None:
            front, back = back.reverse(), PList()
        return front._first(), Queue(front.tail, back, self.size - 1)

    def peek(self):
        return self.dequeue()[0]

    def is_empty(self):
        return not self.size

    def __len__(self):
        return self.size

def benchmark():
    initial = dict.fromkeys(range(10000), 0)
    def deep(d, k, v):
        result = copy.deepcopy(d)
        result[k] = v
        return result
    for name, start, update in [
        ("deepcopy", initial, deep),
        ("dict", initial, lambda d, k, v: {**d, k: v}),
        ("pmap", pmap(initial), lambda d, k, v: d.set(k, v)),
    ]:
        tracemalloc.start()
        begin = perf_counter()
        versions = [start]
        for i in range(1000):
            versions.append(update(versions[-1], i, i + 1))
        print(name, round(perf_counter() - begin, 3),
              round(tracemalloc.get_traced_memory()[1] / 2**20, 2), "MiB")
        tracemalloc.stop()
        del versions

class Student(PRecord):
    name = field(type=str, mandatory=True)
    grade = field(type=int, mandatory=True,
                  invariant=lambda n: (0 <= n <= 100, "grade: 0..100"))

def edge(graph, a, b):
    return graph.set(a, graph.get(a, pset()).add(b)).set(
        b, graph.get(b, pset()).add(a))

def bfs(graph, start):
    from collections import deque
    pending, seen, order = deque([start]), {start}, []
    while pending:
        node = pending.popleft()
        order.append(node)
        for neighbor in sorted(graph.get(node, ())):
            if neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return order

@dataclass(frozen=True)
class Maybe:
    value: object
    @classmethod
    def unit(cls, value):
        return cls(value)
    def bind(self, f):
        return self if self.value is None else f(self.value)
    def map(self, f):
        return self.bind(lambda x: self.unit(f(x)))

@dataclass(frozen=True)
class ListM:
    values: tuple
    @classmethod
    def unit(cls, value):
        return cls((value,))
    def bind(self, f):
        return ListM(tuple(y for x in self.values for y in f(x).values))
    def map(self, f):
        return self.bind(lambda x: self.unit(f(x)))

@dataclass(frozen=True)
class Writer:
    value: object
    log: tuple = ()
    @classmethod
    def unit(cls, value):
        return cls(value)
    def bind(self, f):
        result = f(self.value)
        return Writer(result.value, self.log + result.log)
    def map(self, f):
        return self.bind(lambda x: self.unit(f(x)))

def check_laws(unit, values, funcs):
    for x in values:
        m = unit(x)
        assert m.bind(unit) == m and m.map(lambda y: y) == m
        for f in funcs:
            assert m.bind(f) == f(x)
            for g in funcs:
                assert m.bind(f).bind(g) == m.bind(lambda y: f(y).bind(g))
        assert m.map(lambda y: y + 1).map(lambda y: y * 2) == m.map(
            lambda y: (y + 1) * 2)

def triples():
    return ListM(tuple(range(1, 21))).bind(
        lambda a: ListM(tuple(range(a, 21))).bind(
            lambda b: ListM(tuple(range(b, 21))).bind(
                lambda c: ListM.unit((a, b, c)) if a*a + b*b == c*c
                else ListM(())))).values

def factorial(n):
    result = Writer.unit(1)
    for i in range(1, n + 1):
        result = result.bind(lambda x: Writer(x*i, (f"{x} * {i} = {x*i}",)))
    return result

@dataclass(frozen=True)
class Leaderboard:
    versions: object = pvector([pvector()])

    def insert(self, name, score):
        rows = self.versions[-1]
        row = (-score, name)
        i = bisect_left(rows, row)
        updated = rows[:i].append(row).extend(rows[i:])
        return Leaderboard(self.versions.append(updated))

    def remove(self, name, score):
        rows = self.versions[-1]
        row = (-score, name)
        i = bisect_left(rows, row)
        if i == len(rows) or rows[i] != row:
            raise KeyError(name)
        return Leaderboard(self.versions.append(rows[:i].extend(rows[i+1:])))

    def at(self, version=-1):
        return [(name, -score) for score, name in self.versions[version]]

def demo1():
    tail = PList.from_iterable([2, 3])
    print(tail.cons(1).to_list(), tail.cons(4).tail is tail.cons(1).tail)

def demo2():
    from random import Random
    from collections import deque
    rng = Random(42)
    for count in (10000, 50000, 100000):
        begin = perf_counter()
        q, reference = Queue(), deque()
        for i in range(count):
            if not reference or rng.randrange(2):
                q = q.enqueue(i)
                reference.append(i)
            else:
                value, q = q.dequeue()
                assert value == reference.popleft()
        print(count, round(perf_counter() - begin, 4))
    old = Queue().enqueue(10)
    assert old.enqueue(20).dequeue()[1].peek() == 20 and old.peek() == 10

def demo4():
    config = freeze({"app": {"ports": [80, 443]}})
    print(thaw(config.transform(["app", "ports", 0], 8080)))
    vector = pvector(range(1000))
    begin = perf_counter()
    result = vector
    for i in range(1000):
        result = result.set(i, -i)
    print("set:", perf_counter() - begin)
    begin = perf_counter()
    edits = vector.evolver()
    for i in range(1000):
        edits[i] = -i
    assert edits.persistent() == result
    print("evolver:", perf_counter() - begin)
    try:
        Student(name="Ali", grade=101)
    except Exception as exc:
        print(type(exc).__name__, exc)
    print(bfs(edge(edge(pmap(), "A", "B"), "B", "C"), "A"))

def demo5():
    for cls in (Maybe, ListM, Writer):
        check_laws(cls.unit, [0, 1, 5],
                   [lambda x: cls.unit(x + 1), lambda x: cls.unit(x * 2)])
    print(triples())
    print(factorial(5))

def demo6():
    old = Leaderboard().insert("Ali", 10)
    new = old.insert("Dana", 20).remove("Ali", 10)
    assert old.at() == new.at(1) == [("Ali", 10)]
    print(old.at(), new.at())
    begin = perf_counter()
    board = Leaderboard()
    for i in range(500):
        board = board.insert(str(i), i)
    print("pvector:", perf_counter() - begin)
    begin = perf_counter()
    history = [[]]
    for i in range(500):
        rows = history[-1].copy()
        rows.insert(bisect_left(rows, (-i, str(i))), (-i, str(i)))
        history.append(rows)
    print("list copy:", perf_counter() - begin)
