"""Тесты лабораторной работы №8."""

from compose_lab8 import identity, compose, pipe, pipe_value, slugify
from containers_lab8 import Some, Nothing, Ok, Err, sequence, partition_results
from curry_lab8 import convert, between, replace_all


def test_compose_and_pipe():
    f = lambda x: x + 1
    g = lambda x: x * 2
    h = lambda x: x - 3

    for value in [0, 1, 2, 5, 10]:
        assert compose(f, compose(g, h))(value) == compose(compose(f, g), h)(value)
        assert compose(f, identity)(value) == f(value)
        assert compose(identity, f)(value) == f(value)
        assert pipe(f, g, h)(value) == h(g(f(value)))

    assert pipe_value("  ABC ", str.strip, str.lower) == "abc"
    assert slugify("  Привет, Мир!  ") == "privet-mir"


def test_curry():
    assert convert(500)(50)(2) == 950
    assert between(1)(10)(5) is True
    assert between(1)(10)(11) is False
    assert replace_all(" ")("-")("a b c") == "a-b-c"


def test_maybe_functor_monad():
    identity_fn = lambda x: x
    f = lambda x: x + 1
    g = lambda x: x * 2

    values = [Some(1), Some(2), Some(5), Some(10), Nothing()]
    for m in values:
        assert m.map(identity_fn) == m
        assert m.map(f).map(g) == m.map(lambda x: g(f(x)))

    unit = Some
    mf = lambda x: Some(x + 1)
    mg = lambda x: Some(x * 2)

    for value in [1, 2, 5, 10, -3]:
        m = Some(value)
        assert unit(value).bind(mf) == mf(value)
        assert m.bind(unit) == m
        assert m.bind(mf).bind(mg) == m.bind(lambda x: mf(x).bind(mg))


def test_result_functor_monad():
    identity_fn = lambda x: x
    f = lambda x: x + 1
    g = lambda x: x * 2

    values = [Ok(1), Ok(2), Ok(5), Ok(10), Err("x")]
    for r in values:
        assert r.map(identity_fn) == r
        assert r.map(f).map(g) == r.map(lambda x: g(f(x)))

    unit = Ok
    rf = lambda x: Ok(x + 1)
    rg = lambda x: Ok(x * 2)

    for value in [1, 2, 5, 10, -3]:
        r = Ok(value)
        assert unit(value).bind(rf) == rf(value)
        assert r.bind(unit) == r
        assert r.bind(rf).bind(rg) == r.bind(lambda x: rf(x).bind(rg))

    assert sequence([Ok(1), Ok(2)]) == Ok([1, 2])
    assert sequence([Ok(1), Err("bad"), Ok(3)]) == Err("bad")
    assert partition_results([Ok(1), Err("a"), Ok(2)]) == ([1, 2], ["a"])


def run_all():
    test_compose_and_pipe()
    test_curry()
    test_maybe_functor_monad()
    test_result_functor_monad()
    print("Все тесты lab8 успешно пройдены.")


if __name__ == "__main__":
    run_all()
