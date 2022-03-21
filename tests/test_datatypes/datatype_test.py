import pytest
from collections import Counter
from ottoscript.base import OttoBase, OttoContext
from ottoscript.datatypes import (Number,
                                  String,
                                  Var,
                                  Entity,
                                  List,
                                  Dict,
                                  Target,
                                  Area,
                                  Input)


@pytest.mark.asyncio
async def test_numeric():
    """Verify we correctly parse a number"""

    n = Number().parseString("15")[0]
    output = await n.eval()
    assert output == 15


@pytest.mark.asyncio
async def test_string():
    """Verify we correctly parse a string"""

    n = String().parseString("'foo'")[0]
    output = await n.eval()
    assert output == 'foo'


@pytest.mark.asyncio
async def test_var_no_fetch():
    """Verify we correctly parse a var"""

    n = Var().parseString("@foo")[0]
    assert n.name == '@foo'


@pytest.mark.asyncio
async def test_var_with_attributes():
    """Verify we correctly parse a var with attributes"""

    ctx = OttoContext()
    d_string = "(one=1, two=2)"
    e_string = "ship.crew"
    ctx.update_vars({'@foo_entity': Entity().parseString(e_string)[0]})
    ctx.update_vars({'@foo_dict': Dict().parseString(d_string)[0]})
    OttoBase.set_context(ctx)

    n = Var().parseString("@foo_entity:name")[0]
    r = await n.eval()
    assert r == "ship.crew"

    n = Var().parseString("@foo_entity:brightness")[0]
    r = await n.eval()
    assert r == 1

    r = n.fetch()
    assert r.name == "ship.crew.brightness"

    n = Var().parseString("@foo_entity:number")[0]
    r = await n.eval()
    assert r == 1

    n = Var().parseString("@foo_dict:one")[0]
    r = await n.eval()
    assert r == 1

    n = Var().parseString("@foo_dict:two")[0]
    r = await n.eval()
    assert r == 2


@pytest.mark.asyncio
async def test_entity():
    """Verify we correctly parse an entity"""
    test_list = [('ship.crew', 'ship.crew', 'ship.crew'),
                 ('ship.crew:uniform', 'ship.crew.uniform', 1)
                 ]

    for test in test_list:
        n = Entity().parseString(test[0])[0]
        assert n.name == test[1]
        assert await n.eval() == test[2]


@pytest.mark.asyncio
async def test_list():
    """Verify we correctly parse a list"""

    ctx = OttoContext()
    ctx.update_vars({'@foo': 'foostring'})
    OttoBase.set_context(ctx)

    string = "'test1', 27, ship.crew, @foo"
    expected = [String().parseString('"test1"')[0],
                Number().parseString('27')[0],
                Entity().parseString('ship.crew')[0],
                Var().parseString('@foo')[0]]

    n1 = List().parseString(string)[0]

    assert Counter([type(x) for x in n1.contents]) \
        == Counter([type(x) for x in expected])

    n2 = List().parseString(f"({string})")[0]
    assert Counter([type(x) for x in n2.contents]) \
        == Counter([type(x) for x in expected])


@pytest.mark.asyncio
async def test_list_single():
    """Verify we correctly parse a number"""

    string = "ship.crew"
    expected = list

    n1 = List().parseString(string)[0]

    assert type(n1.contents) == expected


@pytest.mark.asyncio
async def test_dictionary():
    """Verify we correctly parse a dictionary"""

    ctx = OttoContext()
    ctx.update_vars({'@foo': 'foostring'})
    OttoBase.set_context(ctx)

    string = "(first = 1, second = 'foo', third = ship.crew, fourth = @foo)"
    expected = {'first': 1,
                'second': 'foo',
                "third": 'ship.crew',
                "fourth": 'foostring'}

    n1 = Dict().parseString(string)[0]

    result = await n1.eval()
    assert result == expected


@pytest.mark.asyncio
async def test_target():

    ctx = OttoContext()
    area = Area().parseString('kitchen')[0]
    ctx.update_vars({'@area': area})

    arealist = List(Area()).parseString('kitchen, living_room')[0]
    ctx.update_vars({'@arealist': arealist})

    OttoBase.set_context(ctx)

    tests = [('ship.crew, ship.phasers',
              {'entity_id': ['ship.crew', 'ship.phasers'], 'area_id': []}
              ),

             ('AREA kitchen, living_room',
              {'area_id': ['kitchen', 'living_room'], 'entity_id': []}
              ),

             ('AREA @area',
              {'area_id': ['kitchen'], 'entity_id': []}
              ),

             ('AREA @arealist',
              {'area_id': ['kitchen', 'living_room'], 'entity_id': []}
              )
             ]

    for test in tests:
        n = Target().parseString(test[0])[0]
        result = await n.eval()
        assert result == test[1]


@pytest.mark.asyncio
async def test_input():

    ctx = OttoContext()
    ctx.update_vars({'@foostring': String().parseString("'foostring'")[0],
                     '@foonumber': Number().parseString("30.0")[0]})

    OttoBase.set_context(ctx)

    tests = [{"type": "text",
              "string": "'foostring'",
              "expected": "foostring"},

             {"type": "text",
              "string": "@foostring",
              "expected": "foostring"},

             {"type": "text",
              "string": "foo.string",
              "expected": "foo.string"},

             {"type": "numeric",
              "string": "15",
              "expected": 15.0},

             {"type": "numeric",
             "string": "@foonumber",
              "expected": 30.0},

             {"type": "numeric",
             "string": "foo.number:attr",
              "expected": 1.0},


             {"type": "any",
             "string": "'foostring'",
                      "expected": "foostring"},

             {"type": "any",
              "string": "@foostring",
              "expected": "foostring"},

             {"type": "any",
              "string": "foo.string",
              "expected": "foo.string"},

             {"type": "any",
              "string": "15",
              "expected": 15.0},

             {"type": "any",
              "string": "@foonumber",
              "expected": 30.0}

             ]

    for test in tests:
        n = Input(test["type"]).parseString(test["string"])[0]
        print(test["string"])
        result = await n.eval()
        assert result == test["expected"]
