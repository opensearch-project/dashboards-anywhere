# Test functions
import json
from operator import ge
from types import NoneType
import generator
import pytest
from datetime import date

# Testing stuff
def generateCommerceData():
    from faker import Faker
    f = Faker()

    sampleDate = f.iso8601()
    sampleOrder = f.pyint(0, 20)
    sampleFailure = f.pyint(0, 2)
    sampleRevenue = f.pricetag()

    return {'date': sampleDate, 'count': sampleOrder, 'failure': sampleFailure, 'revenue': sampleRevenue}


# Sample inputs (valid)
jinput = {
        "year": "year",
        "random number": "integer",
        "email": "email",
        }

jinput2 = {"properties": {
        "first name":    { "type" : ["first_name"]},
        "last name":     { "type" : "last_name"},
        "companies":{ "type" : ["array", "company", 5] }
        }}

jinput3 = json.dumps({
        "year": "year",
        "addresses": ["array", "address", "integer", [1, 3]],
        "director": "name"
        })

jinput4 = json.dumps({"properties": {
        "year":    { "type" : ["year"]},
        "addresses":     { "type" : ["array", "address", "integer", (1, 3)] },
        "director":{ "type" : "name" }
        }})

jinput5 = json.dumps({"properties": {
        "year":    { "type" : ["year"]},
        "integers":     { "type" : ["array", "integer", "integer", (1, 3), 5, 10] },
        "director":{ "type" : "name" }
        }})


# Sample inputs (invalid)
jinput_invalid = {
        "year": "year",
        "random number": "integer",
        "email": "emaiz",
        }

jinput2_invalid = {}

jinput3_invalid = {
        "year": ["year", 5],
        "addresses": ["array", "address", "integer", [1, 3]],
        "director": "name"
        }

jinput4_invalid = {
        "year": "y",
        "addresses": ["array", "address", "5", [1, 3]],
        "director": ["integer", 6, 5]
        }


# Testing each function of generator.py
def test_valid_chooseField():
        # Tests for correct type returned with minimum required arguments
        assert generator.chooseField("null") == None
        assert type(generator.chooseField("float")) is float
        assert type(generator.chooseField("double")) is float
        assert type(generator.chooseField("integer")) is int
        assert type(generator.chooseField("keyword", ["email"])) is str
        assert "@" in generator.chooseField("keyword", ["email"])
        assert type(generator.chooseField("date detection string")) is bool
        assert type(generator.chooseField("numeric detection string")) is bool 
        # One of Faker's standard providers
        ssn = generator.chooseField("ssn")
        assert type(ssn) is str and "-" == ssn[3] and "-" == ssn[6]

        # 4 array tests:
        #       - testArray: A fixed length array with default field values
        #       - testArray2: A fixed length array with arguments for field values
        #       - testArray3: A random length array with default field values
        #       - testArray4: A random length array with arguments for field values
        testArray = generator.chooseField("array", ["integer", 5])
        assert testArray != [] and testArray != None
        assert len(testArray) == 5
        for val in testArray:
                assert type(val) is int
        testArray2 = generator.chooseField("array", ["integer", 8, 2, 10])
        assert len(testArray2) == 8
        for val in testArray2:
                assert type(val) is int and 2 <= val <= 10
        testArray3 = generator.chooseField("array", ["integer", "integer", (8, 9)])
        assert 8 <= len(testArray3) <= 9
        for val in testArray3:
                assert type(val) is int
        testArray4 = generator.chooseField("array", ["integer", "integer", (10, 15), 44, 56])
        assert 10 <= len(testArray4) <= 15
        for val in testArray4:
                assert type(val) is int and 44 <= val <= 56

        # Tests for correct type returned with optional arguments
        testFloat = generator.chooseField("float", [4, 2, True])
        assert type(testFloat) is float and 0 <= testFloat <= 9999.99
        testDouble = generator.chooseField("double", [1,2])
        assert type(testDouble) is float and -9.99 <= testDouble <= 9.99
        testInt = generator.chooseField("integer", [-1, 1])
        assert type(testInt) is int and -1 <= testInt <= 1
        testKeyword = generator.chooseField("keyword", ["zipcode_in_state", "TX"])
        assert 73301 <= int(testKeyword) <= 88595
        from dateutil.relativedelta import relativedelta
        # Another one of Faker's standard providers
        testBirthday = generator.chooseField("date_of_birth", (None, 18, 23))
        assert type(testBirthday) is date and 18 <= relativedelta(date.today(), testBirthday).years <= 23

def test_invalid_chooseField():
        # Tests for invalid/garbage inputs
        assert type(generator.chooseField("ints")) is NoneType
        assert type(generator.chooseField("integer", [5, 4])) is NoneType
        assert type(generator.chooseField("boalean")) is NoneType
        assert type(generator.chooseField("keyword")) is NoneType
        assert type(generator.chooseField("keyword", "intx")) is NoneType
        assert type(generator.chooseField("keyword", ["zipcode_in_state", "AB"])) is NoneType
        assert type(generator.chooseField("array")) is NoneType
        assert type(generator.chooseField("array", "integer")) is NoneType
        assert type(generator.chooseField("array", ["integer", "ab"])) is NoneType
        assert generator.chooseField("array", ["integer", 3, 6, 5]) == []
        assert generator.chooseField("array", ["integer", "integer", 6, 5]) == None
        assert generator.chooseField("array", ["integer", "integer", (1)]) == None
        assert generator.chooseField("array", ["integer", "integer", (2, 1)]) == None
        assert generator.chooseField("array", ["integer", "integer", (2, 1), 6 ,4]) == None
        assert type(generator.chooseField("date detection string", 1)) is NoneType

        # Tests for invalid parameters
        with pytest.raises(TypeError):
                generator.chooseField("keyword", "zipcode_in_state", "AB")
        with pytest.raises(TypeError):
                generator.chooseField("array", "integer", 3, 6, 5)
        with pytest.raises(TypeError):
                generator.chooseField("keyword", "zipcode_in_state", "TX")

def test_valid_generateData():
        # Tests whether each field is indeed populated and contains everything
        test1 = json.loads(generator.generateData(jinput, False))
        assert len(test1) == 3
        for field in test1:
                assert test1[field] != None

        test2 = json.loads(generator.generateData(jinput2))
        assert len(test2) == 3
        for field in test2:
                assert test2[field] != None        

        test3 = json.loads(generator.generateData(jinput3, False))
        assert len(test3) == 3
        for field in test3:
                assert test3[field] != None

        test4 = json.loads(generator.generateData(jinput4))
        assert len(test4) == 3
        for field in test4:
                assert test4[field] != None

        test5 = json.loads(generator.generateData(jinput5))
        assert len(test5) == 3
        for field in test5:
                assert test5[field] != None

        test6 = generator.generateData("./tests/sample.json")
        assert len(test6) == 2
        for jso in test6:
                jso = json.loads(jso)
                assert len(jso) == 3
                for field in jso:
                        assert jso[field] != None

        test7 = generator.generateData("./tests/sample.csv")
        assert len(test7) == 2
        for jso in test7:
                jso = json.loads(jso)
                assert len(jso) == 3
                for field in jso:
                        assert jso[field] != None

def test_invalid_generateData():
        # Tests of garbage/invalid inputs
        test1 = json.loads(generator.generateData(jinput_invalid, False))
        assert len(test1) == 3
        assert type(test1["year"]) is str
        assert type(test1["random number"]) is int
        assert test1["email"] == None
        test2 = json.loads(generator.generateData(jinput2_invalid))
        assert test2 == {}
        test3 = json.loads(generator.generateData(jinput2_invalid, False))
        assert test3 == {}
        test4 = json.loads(generator.generateData(jinput3_invalid, False))
        assert len(test4) == 3
        assert test4["year"] == None
        assert type(test4["addresses"]) is list
        for val in test4["addresses"]:
                assert type(val) is str
        assert type(test4["director"]) is str
        test5 = json.loads(generator.generateData(jinput4_invalid, False))
        assert len(test5) == 3
        for val in test5:
                assert type(test5[val]) is NoneType

        # Tests for invalid parameters
        with pytest.raises(TypeError):
                generator.generateData(jinput5, False)
        assert json.loads(generator.generateData(jinput3)) == {}
        with pytest.raises(FileNotFoundError):
                generator.generateData("aaaa.json")
        with pytest.raises(json.decoder.JSONDecodeError):
                generator.generateData("gsf.pdf")