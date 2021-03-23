import pytest
from sqlalchemy import text

from plpy_man import plpy_func, _write_plpython_sql, plpy


# fmt: off
########################################################################################
# https://www.postgresql.org/docs/13/plpython-data.html#id-1.8.11.11.4
def test_null_none():
    @plpy_func
    def pymax(a, b):
        if (a is None) or (b is None):
            return None
        if a > b:
            return a
        return b

    actual = _write_plpython_sql(pymax)
    expected = text(
        """\
CREATE FUNCTION pymax (a integer, b integer)
  RETURNS integer
AS $$
    if (a is None) or (b is None):
        return None
    if a > b:
        return a
    return b
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


########################################################################################
# https://www.postgresql.org/docs/13/plpython-data.html#PLPYTHON-ARRAYS
def test_arrays_lists():
    @plpy_func
    def return_arr():
        return [1, 2, 3, 4, 5]

    actual = _write_plpython_sql(return_arr)
    expected = text(
        """\
CREATE FUNCTION return_arr()
  RETURNS int[]
AS $$
    return [1, 2, 3, 4, 5]
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


def test_multi_dimensional_array():
    @plpy_func
    def test_type_conversion_array_int4(x):
        plpy.info(x, type(x))

    actual = _write_plpython_sql(test_type_conversion_array_int4)
    expected = text(
        """\
CREATE FUNCTION test_type_conversion_array_int4(x int4[])
  RETURNS int4[]
AS $$
    plpy.info(x, type(x))
    return x
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


def test_new_to_python_and_strings():
    @plpy_func
    def return_str_arr():
        return "hello"

    actual = _write_plpython_sql(return_str_arr)
    expected = text(
        """\
CREATE FUNCTION return_str_arr()
  RETURNS varchar[]
AS $$
    return "hello"
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


########################################################################################
# https://www.postgresql.org/docs/13/plpython-data.html#id-1.8.11.11.6
def test_composite_types():
    @plpy_func
    def overpaid(e):
        if e["salary"] > 200000:
            return True
        if (e["age"] < 30) and (e["salary"] > 100000):
            return True
        return False

    actual = _write_plpython_sql(overpaid)
    expected = text(
        """\
CREATE FUNCTION overpaid (e employee)
  RETURNS boolean
AS $$
    if e["salary"] > 200000:
        return True
    if (e["age"] < 30) and (e["salary"] > 100000):
        return True
    return False
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


def test_named_pair_sequence():
    @plpy_func
    def make_pair(name, value):
        return ( name, value )
        # or alternatively, as tuple: return [ name, value ]
    actual = _write_plpython_sql(make_pair)
    expected = text(
        """\
CREATE FUNCTION make_pair (name text, value integer)
  RETURNS named_value
AS $$
    return ( name, value )
    # or alternatively, as tuple: return [ name, value ]
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


def test_named_pair_mapping():
    @plpy_func
    def make_pair(name, value):
        return { "name": name, "value": value }

    actual = _write_plpython_sql(make_pair)
    expected = text("""\
CREATE FUNCTION make_pair (name text, value integer)
  RETURNS named_value
AS $$
    return { "name": name, "value": value }
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


def test_make_pair_object():
    @plpy_func
    def make_pair(name, value):
        class named_value:
            def __init__(self, n, v):
                self.name = n
                self.value = v
        return named_value(name, value)

        # or simply
        class nv: pass
        nv.name = name
        nv.value = value
        return nv

    actual = _write_plpython_sql(make_pair)
    expected = text("""\
CREATE FUNCTION make_pair (name text, value integer)
  RETURNS named_value
AS $$
    class named_value:
        def __init__ (self, n, v):
            self.name = n
            self.value = v
    return named_value(name, value)

    # or simply
    class nv: pass
    nv.name = name
    nv.value = value
    return nv
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


def test_function_with_out_parameters():
    @plpy_func
    def multiout_simple(i, j):
        return (1, 2)

    actual = _write_plpython_sql(multiout_simple)
    expected = text("""\
CREATE FUNCTION multiout_simple(OUT i integer, OUT j integer) AS $$
    return (1, 2)
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


def test_procedure_with_output_parameters():
    @plpy_func
    def python_triple(a, b):
        return (a * 3, b * 3)

    actual = _write_plpython_sql(python_triple)
    expected = text("""\
CREATE PROCEDURE python_triple(INOUT a integer, INOUT b integer) AS $$
    return (a * 3, b * 3)
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


########################################################################################
# https://www.postgresql.org/docs/13/plpython-data.html#id-1.8.11.11.7
def test_set_from_sequence():
    @plpy_func
    def greet(how):
        # return tuple containing lists as composite types
        # all other combinations work also
        return ( [ how, "World" ], [ how, "PostgreSQL" ], [ how, "PL/Python" ] )
    actual = _write_plpython_sql(greet)
    expected = text("""\
CREATE FUNCTION greet (how text)
  RETURNS SETOF greeting
AS $$
    # return tuple containing lists as composite types
    # all other combinations work also
    return ( [ how, "World" ], [ how, "PostgreSQL" ], [ how, "PL/Python" ] )
$$ LANGUAGE plpythonu
"""
    )
    assert actual == expected


def test_set_from_iterator():
    @plpy_func
    def greet(how):
        class producer:
            def __init__(self, how, who):
                self.how = how
                self.who = who
                self.ndx = -1

            def __iter__(self):
                return self

            def next(self):
                self.ndx += 1
                if self.ndx == len(self.who):
                    raise StopIteration
                return (self.how, self.who[self.ndx])

        return producer(how, [ "World", "PostgreSQL", "PL/Python" ])

    actual = _write_plpython_sql(greet)
    expected = text("""\
CREATE FUNCTION greet (how text)
  RETURNS SETOF greeting
AS $$
    class producer:
        def __init__ (self, how, who):
          self.how = how
          self.who = who
          self.ndx = -1

        def __iter__ (self):
          return self

        def next (self):
          self.ndx += 1
          if self.ndx == len(self.who):
            raise StopIteration
          return ( self.how, self.who[self.ndx] )

    return producer(how, [ "World", "PostgreSQL", "PL/Python" ])
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


def test_set_from_generator():
    @plpy_func
    def greet(how):
        for who in ["World", "PostgreSQL", "PL/Python"]:
            yield ( how, who )
    actual = _write_plpython_sql(greet)
    expected = text("""\
CREATE FUNCTION greet (how text)
  RETURNS SETOF greeting
AS $$
    for who in [ "World", "PostgreSQL", "PL/Python" ]:
        yield ( how, who )
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


def test_set_returning_function_with_OUT_parameters():
    @plpy_func
    def multiout_simple_setof(n):
        return [(1, 2)] * n
    actual = _write_plpython_sql(multiout_simple_setof)
    expected = text("""\
CREATE FUNCTION multiout_simple_setof(n integer, OUT integer, OUT integer)
  RETURNS SETOF record
AS $$
    return [(1, 2)] * n
$$ LANGUAGE plpythonu;
"""
    )
    assert actual == expected


# fmt: on
if __name__ == "__main__":
    pytest.main()
