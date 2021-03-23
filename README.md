# Plpy Man 🦸‍♂️
######PlPython manager that synchronizes Python code between your web server and Postgres database 
[comment]: <> (No more messing about with PlPgSQL; Plpy Man to the rescue!)
## PlPy Man is not released. Do not use yet.

## Quickstart
### Write database function in pure Python.
```python
import plpy_man
import sqlalchemy as sa
from sqlalchemy.orm import Session

# Setup your database
engine = sa.create_engine("<Postgres connection string>")
db = sa.orm.Session(bind=engine)


# Write the database function. Decorate it with plpy_man.plpy_func.
@plpy_man.plpy_func
def py_add(x, y):
    return x + y


# Flush the function to the database!
plpy_man.flush(db)

value = db.execute(sa.text("SELECT py_add(3, 5)"))
assert value == 8
```
### Make objects callable from the PlPython GD
```python
import plpy_man
import sqlalchemy as sa
from plpy_man import plpy, GD
from sqlalchemy.orm import Session, declarative_base

# Setup your database
engine = sa.create_engine("<Postgres connection string>")
db = sa.orm.Session(bind=engine)
Base = declarative_base()
class Employees(Base):
    __tablename__ = "employees"
    id = sa.Column("id", sa.Integer, primary_key=True),
    name = sa.Column("name", sa.TEXT, nullable=False),
    pay = sa.Column("pay", sa.Integer)
db.add(Employees(id=1, name="Alice", pay=15))
db.add(Employees(id=2, name="Bob", pay=15))
db.add(Employees(id=3, name="Charlie", pay=200))
db.flush()


# Write a function.
# This function will be available in both your Python and PlPython scripts
def py_average(sequence):
    return sum(sequence) / len(sequence)


plpy_man.to_gd(py_average)


@plpy_man.plpy_func
def average_wage():
    rows = plpy.execute("SELECT pay FROM employees;")
    wages = [row["pay"] for row in rows]
    average = round(GD["py_average"](wages), 2)
    return f"Average wage is ${average}"


# Flush py_average to the Global Dict and average_wage to the database
plpy_man.flush()

value = db.execute(sa.text("SELECT living_wages()"))
assert value == "Average wage is $76.67"
```



