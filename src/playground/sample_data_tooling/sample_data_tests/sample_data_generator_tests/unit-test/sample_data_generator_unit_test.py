# Test functions
import os
import sys
import json
import pytest
from datetime import date
from types import NoneType

# Adds parent directory sample_data_tooling to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import sample_data_generator.sample_data_generator as generator


# This path is for getting the parent directory sample_data_generator_tests
FILE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Sample inputs (valid)
valid_json_shorthand = {
        "year": "year",
        "random number": "integer",
        "email": "email",
        }

valid_json_mapping = {"properties": {
        "first name":    { "type" : ["first_name"]},
        "last name":     { "type" : "last_name"},
        "companies":{ "type" : ["array", "company", 5] }
        }}

valid_json_string_shorthand = json.dumps({
        "year": "year",
        "addresses": ["array", "address", "integer", [1, 3]],
        "director": "name"
        })

valid_json_string_mapping = json.dumps({"properties": {
        "year":    { "type" : ["year"]},
        "addresses":     { "type" : ["array", "address", "integer", (1, 3)] },
        "director":{ "type" : "name" }
        }})

valid_json_string_mapping_two = json.dumps({"properties": {
        "year":    { "type" : ["year"]},
        "integers":     { "type" : ["array", "integer", "integer", (1, 3), 5, 10] },
        "director":{ "type" : "name" }
        }})


# Sample inputs (invalid)
invalid_json_shorthand = {
        "year": "year",
        "random number": "integer",
        "email": "emaiz",
        }

invalid_empty_json = {}

invalid_json_shorthand_with_array = {
        "year": ["year", 5],
        "addresses": ["array", "address", "integer", [1, 3]],
        "director": "name"
        }

invalid_json_field_type = {
        "year": "y",
        "addresses": ["array", "address", "5", [1, 3]],
        "director": ["integer", 6, 5]
        }


# Testing each function of generator.py
def test_valid_choose_field():
        # Tests for correct type returned with minimum required arguments
        assert generator.choose_field("null") == None
        assert type(generator.choose_field("float")) is float
        assert type(generator.choose_field("double")) is float
        assert type(generator.choose_field("integer")) is int
        assert type(generator.choose_field("keyword", ["email"])) is str
        assert "@" in generator.choose_field("keyword", ["email"])
        assert type(generator.choose_field("date detection string")) is bool
        assert type(generator.choose_field("numeric detection string")) is bool 
        # One of Faker's standard providers
        ssn = generator.choose_field("ssn")
        assert type(ssn) is str and "-" == ssn[3] and "-" == ssn[6]

        # 4 array tests:
        #       - test_array_1: A fixed length array with default field values
        #       - test_array_2: A fixed length array with arguments for field values
        #       - test_array_3: A random length array with default field values
        #       - test_array_4: A random length array with arguments for field values
        test_array_ = generator.choose_field("array", ["integer", 5])
        assert test_array_ != [] and test_array_ != None
        assert len(test_array_) == 5
        for val in test_array_:
                assert type(val) is int
        test_array_2 = generator.choose_field("array", ["integer", 8, 2, 10])
        assert len(test_array_2) == 8
        for val in test_array_2:
                assert type(val) is int and 2 <= val <= 10
        test_array_3 = generator.choose_field("array", ["integer", "integer", (8, 9)])
        assert 8 <= len(test_array_3) <= 9
        for val in test_array_3:
                assert type(val) is int
        test_array_4 = generator.choose_field("array", ["integer", "integer", (10, 15), 44, 56])
        assert 10 <= len(test_array_4) <= 15
        for val in test_array_4:
                assert type(val) is int and 44 <= val <= 56

        # Tests for correct type returned with optional arguments
        test_Float = generator.choose_field("float", [4, 2, True])
        assert type(test_Float) is float and 0 <= test_Float <= 9999.99
        test_Double = generator.choose_field("double", [1,2])
        assert type(test_Double) is float and -9.99 <= test_Double <= 9.99
        test_Int = generator.choose_field("integer", [-1, 1])
        assert type(test_Int) is int and -1 <= test_Int <= 1
        test_Keyword = generator.choose_field("keyword", ["zipcode_in_state", "TX"])
        assert 73301 <= int(test_Keyword) <= 88595
        from dateutil.relativedelta import relativedelta
        # Another one of Faker's standard providers
        test_Birthday = generator.choose_field("date_of_birth", (None, 18, 23))
        assert type(test_Birthday) is date and 18 <= relativedelta(date.today(), test_Birthday).years <= 23


def test_invalid_choose_field():
        # Tests for invalid/garbage inputs
        assert type(generator.choose_field("ints")) is NoneType
        assert type(generator.choose_field("integer", [5, 4])) is NoneType
        assert type(generator.choose_field("boalean")) is NoneType
        assert type(generator.choose_field("keyword")) is NoneType
        assert type(generator.choose_field("keyword", "intx")) is NoneType
        assert type(generator.choose_field("keyword", ["zipcode_in_state", "AB"])) is NoneType
        assert type(generator.choose_field("array")) is NoneType
        assert type(generator.choose_field("array", "integer")) is NoneType
        assert type(generator.choose_field("array", ["integer", "ab"])) is NoneType
        assert generator.choose_field("array", ["integer", 3, 6, 5]) == []
        assert generator.choose_field("array", ["integer", "integer", 6, 5]) == None
        assert generator.choose_field("array", ["integer", "integer", (1)]) == None
        assert generator.choose_field("array", ["integer", "integer", (2, 1)]) == None
        assert generator.choose_field("array", ["integer", "integer", (2, 1), 6 ,4]) == None
        assert type(generator.choose_field("date detection string", 1)) is NoneType

        # Tests for invalid parameters
        with pytest.raises(TypeError):
                generator.choose_field("keyword", "zipcode_in_state", "AB")
        with pytest.raises(TypeError):
                generator.choose_field("array", "integer", 3, 6, 5)
        with pytest.raises(TypeError):
                generator.choose_field("keyword", "zipcode_in_state", "TX")


def test_valid_generate_data():
        # Tests whether each field is indeed populated and contains everything
        test_1 = json.loads(generator.generate_data(valid_json_shorthand, False))
        assert len(test_1) == 3
        for field in test_1:
                assert test_1[field] != None

        test_2 = json.loads(generator.generate_data(valid_json_mapping))
        assert len(test_2) == 3
        for field in test_2:
                assert test_2[field] != None        

        test_3 = json.loads(generator.generate_data(valid_json_string_shorthand, False))
        assert len(test_3) == 3
        for field in test_3:
                assert test_3[field] != None

        test_4 = json.loads(generator.generate_data(valid_json_string_mapping))
        assert len(test_4) == 3
        for field in test_4:
                assert test_4[field] != None

        test_5 = json.loads(generator.generate_data(valid_json_string_mapping_two))
        assert len(test_5) == 3
        for field in test_5:
                assert test_5[field] != None

        test_6 = generator.generate_data(os.path.join(FILE_PATH, "test-files/json-format-test.json"))
        assert len(test_6) == 2
        for jso in test_6:
                jso = json.loads(jso)
                assert len(jso) == 3
                for field in jso:
                        assert jso[field] != None

        test_7 = generator.generate_data(os.path.join(FILE_PATH, "test-files/csv-format-test.csv"))
        assert len(test_7) == 2
        for jso in test_7:
                jso = json.loads(jso)
                assert len(jso) == 3
                for field in jso:
                        assert jso[field] != None

        test_8 = generator.generate_data(os.path.join(FILE_PATH, "test-files/json-format-test-zipped.json.gz"))
        assert len(test_8) == 2
        for jso in test_8:
                jso = json.loads(jso)
                assert len(jso) == 3
                for field in jso:
                        assert jso[field] != None

        test_8 = generator.generate_data(os.path.join(FILE_PATH, "test-files/csv-format-test-zipped.csv.gz"))
        assert len(test_8) == 2
        for jso in test_8:
                jso = json.loads(jso)
                assert len(jso) == 3
                for field in jso:
                        assert jso[field] != None


def test_invalid_generate_data():
        # Tests of garbage/invalid inputs
        test_1 = json.loads(generator.generate_data(invalid_json_shorthand, False))
        assert len(test_1) == 3
        assert type(test_1["year"]) is str
        assert type(test_1["random number"]) is int
        assert test_1["email"] == None
        with pytest.raises(TypeError):
                test_2 = json.loads(generator.generate_data(invalid_empty_json))
                assert test_2 == {}
        test_3 = json.loads(generator.generate_data(invalid_empty_json, False))
        assert test_3 == {}
        test_4 = json.loads(generator.generate_data(invalid_json_shorthand_with_array, False))
        assert len(test_4) == 3
        assert test_4["year"] == None
        assert type(test_4["addresses"]) is list
        for val in test_4["addresses"]:
                assert type(val) is str
        assert type(test_4["director"]) is str
        test_5 = json.loads(generator.generate_data(invalid_json_field_type, False))
        assert len(test_5) == 3
        for val in test_5:
                assert type(test_5[val]) is NoneType

        # Test_s for invalid parameters
        with pytest.raises(TypeError):
                generator.generate_data(valid_json_string_mapping_two, False)
        with pytest.raises(TypeError):
                json.loads(generator.generate_data(valid_json_string_shorthand))
        with pytest.raises(FileNotFoundError):
                generator.generate_data("aaaa.json")
        with pytest.raises(TypeError):
                assert generator.generate_data("gsf.pdf") == 1