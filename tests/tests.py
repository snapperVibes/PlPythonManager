import logging
import textwrap

import pytest
from sqlalchemy import text

import plpy_man

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_db_setup(db) -> None:
    actual = db.execute(text("SELECT 1")).one()
    expected = (1,)
    assert actual == expected


class TestAddToGD:
    def test_prep_source(self) -> None:
        def func(x="hello", y="world"):
            """ This is a docstring. """
            # This is a comment
            return f"{x}, {y}"

        class Class:
            pass

        actual = plpy_man._prep_source([func, Class])
        expected = textwrap.dedent(
            '''\
            def func(x="hello", y="world"):
                """ This is a docstring. """
                # This is a comment
                return f"{x}, {y}"


            GD["func"] = func


            class Class:
                pass


            GD["Class"] = Class
            '''
        )
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

    def test_write_sql(self) -> None:
        py_script = textwrap.dedent(
            '''\
            def func(x="hello", y="world"):
                """ This is a docstring. """
                # This is a comment
                return f"{x}, {y}"


            GD["func"] = func


            class Class:
                pass


            GD["Class"] = Class
            '''
        )
        result = plpy_man._write_gd_sql(py_script)
        expected_str = textwrap.dedent(
            '''\
            CREATE OR REPLACE FUNCTION _add_to_gd()
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
        )
        assert result != expected_str
        assert str(result) == expected_str

    # def test_upload_to_postgres(self, db):
    #     # Todo: unit test the last part of the function? Seems unnecessary
    #     pass

    # def test_method_with_default_manager(self, db):
    #     manager = plpy_man.PlpyMan()
    #
    #     def hello_world():
    #         return "Hello, world"
    #
    #     manager.to_gd(hello_world)
    #     manager.flush(db)
    #     actual = db.execute(text("SELECT hello_world()")).first()
    #     expected = ("Hello, world",)
    #     assert actual == expected


if __name__ == "__main__":
    pytest.main()
