import logging

import pytest
from sqlalchemy import text

import plpython_manager as plpy_man

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_db_setup(db):
    actual = db.execute(text("SELECT 1")).one()
    expected = (1,)
    assert actual == expected


class TestCopyRegisteredObjectsToGD:
    def test_prep_source(self):
        def func(x="hello", y="world"):
            """ This is a docstring. """
            # This is a comment
            return f"{x}, {y}"

        class Class:
            pass

        actual = plpy_man._prep_source([func, Class])
        expected = '''\
def func(x="hello", y="world"):
    """ This is a docstring. """
    # This is a comment
    return f"{x}, {y}"


GD["func"] = func


class Class:
    pass


GD["Class"] = Class
'''
        assert actual == expected

    # THIS TEST DOES NOT ACTUALLY WORK AND plpy_man needs updated
    #
    #     def test_prep_source_with_alias(self):
    #         # Todo: Rename test
    #         def original():
    #             pass
    #
    #         new = original
    #
    #         actual = plpy_man._prep_source([new])
    #         expected = """\
    # def original():
    #     pass
    #
    #
    # GD["original"] = original
    # """
    #         assert actual == expected
    #
    #     def test_prep_source_with_new_name(self):
    #         def original():
    #             pass
    #
    #         original.__name__ = "new"
    #
    #         actual = plpy_man._prep_source([original])
    #         expected = """\
    # def original():
    #     pass
    #
    #
    # GD["new"] = new
    # """
    #         assert actual == expected

    def test_write_sql(self):
        py_script = '''\
def func(x="hello", y="world"):
    """ This is a docstring. """
    # This is a comment
    return f"{x}, {y}"


GD["func"] = func


class Class:
    pass


GD["Class"] = Class
'''
        result = plpy_man._write_sql(py_script)
        expected_str = '''\
CREATE OR REPLACE FUNCTION add_to_gd()
RETURNS TEXT AS $$
def func(x="hello", y="world"):
    """ This is a docstring. """
    # This is a comment
    return f"{x}, {y}"


GD["func"] = func


class Class:
    pass


GD["Class"] = Class

$$ LANGUAGE plpython3u;
'''
        assert result != expected_str
        assert str(result) == expected_str

    # def test_upload_to_postgres(self, db):
    #     # Todo: unit test the last part of the function? Seems unnecessary
    #     pass

    # def test_copy_registered_objects_to_GD(self, db):
    #     manager = plpy_man.PlPythonManager()
    #     manager.registered_objects.append()


if __name__ == "__main__":
    pytest.main()
