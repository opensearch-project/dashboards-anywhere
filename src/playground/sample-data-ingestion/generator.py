from faker import Faker

# Standard libraries
import shutil
import json
import gzip
import csv
import ast
import os

# Function that generates fake values for given fields
# This is based off of the Faker library 
def chooseField(kind, args=None):
    fake = Faker()
    
    # "data-types.json" defines what enumerated types return in Faker
    # Need support for the following:
    #   "null": "return None",
    #   "keyword": "return chooseField",
    with open("data-types.json", "r") as f:
        existingTypes = json.load(f)

    # Null: A null type returns nothing
    if kind == "null":
        return None

    # If the user used a data type defined in "data-types.json", it will be executed
    elif kind in existingTypes:
        try:
            toReturn = getattr(fake, existingTypes[kind])
            if args:
                return toReturn(*args)
            return toReturn()
        except Exception as e:
            print(e)
            print("Invalid data type")
            return None

    # Array: An array type returns an array of field values
    #   There are 2 types: {"type": ["array", <field type>, <int>, *args]}
    #                      {"type": ["array", <field type>, "integer", (min, max), *args]}
    elif kind == "array":
        if not args or len(args) < 2:
            print("Invalid Array: array must specify type and number")
            return None
        if type(args[1]) is not int and len(args) < 3:
            print("Invalid Array: if you want a random array length, specify a tuple of ranges")
        try:
            list = []
            length = 0
            
            # User specifies a fixed array length
            if type(args[1]) is int:
                for i in range(args[1]):
                    val = chooseField(args[0], args[2:])
                    if val:
                        list.append(val)
                return list
            # User specifies a range of possible array lengths
            else:
                length = chooseField(args[1], tuple(args[2]))
                for i in range(length):
                    val = chooseField(args[0], args[3:])
                    if val:
                        list.append(val)
                return list
        except Exception as e:
            print(e)
            print("Invalid Array")
            return None

    # Keyword: A keyword type returns a defined faker attribute (e.g. "zipcode" or "email") with or without arguments
    #   Usage: {"type": "keyword", <faker attribute>, *args}
    elif kind == "keyword":
        if not args:
            print("Invalid Keyword: attribute needs to be defined")
            return None
        try:
            return chooseField(args[0], args[1:])
        except Exception as e:
            print(e)
            print("Invalid Keyword")
            return None

    # Case not explicitly mentioned in OpenSearch field types is tried as a faker attribute
    else:
        try:
            toReturn = getattr(fake, kind)
            if args:
                return toReturn(*args)
            return toReturn()
        except Exception as e:
            print(e)
            print("Invalid data type")
            return None


# Function to generate data
# Returns a JSON object or a list of JSON objects if a JSON  or CSV file was provided
# Format: Paste in your mapping value {"properties": {<properties values>}}
#         Alternatively, pass in a JSON string or string in the form:
#           {<Field>: <Field Type>} 
#         If you provide arguments, the <Field Type> should be a list:
#           {<Field>: [<Field Type>, *args]}
def generateData(input, mappings=True):
    toReturn = {}

    if type(input) is str and "." in input:
        name = input
        # Unzips file if necessary
        if ".gz" in input:
            with gzip.open(input, 'rb') as fin:
                with open(input.split(".gz")[0], 'wb') as fout:
                    shutil.copyfileobj(fin, fout)
            name = input.split(".gz")[0]

    # If a JSON file was provided
    if type(input) is str and ".json" in input:
        JSON_list = []
        with open(name, 'r') as f:
            for line in f:
                JSON_list.append(generateData(line, "properties" in line))
        
        # Deletes unzipped file
        if name != input:
            os.remove(name)
        return JSON_list

    # If a CSV file was provided
    elif type(input) is str and ".csv" in input:
        CSV_list = []
        with open(name, "r") as f:
            reader = csv.reader(f)
            fields = next(reader)
            for row in reader:
                entry_dict = {}
                for i in range(len(fields)):
                    entry_dict[fields[i]] = row[i]
                    # Entries with arguments
                    if "," in entry_dict[fields[i]]:
                        entry_dict[fields[i]] = ast.literal_eval(entry_dict[fields[i]])
                CSV_list.append(generateData(entry_dict, False))
        
        # Deletes unzipped file
        if name != input:
            os.remove(name)
        return CSV_list

    # If mappings was provided as the argument
    elif mappings and (type(input) is dict or json or str):
        # Accepts either dicts or JSON strings
        if type(input) is str:
            input = json.loads(input)
        if "properties" in input:
            for attribute in input["properties"]:
                # Field with arguments
                if type(input["properties"][attribute]) is dict and type(input["properties"][attribute]["type"]) is list:
                    toReturn[attribute] = chooseField(input["properties"][attribute]["type"][0], input["properties"][attribute]["type"][1:])
                # Field with default arguments
                elif type(input["properties"][attribute]) is dict and type(input["properties"][attribute]["type"]) is not list:
                    toReturn[attribute] = chooseField(input["properties"][attribute]["type"])
                else:
                    print("Invalid: dynamic not supported")
                    toReturn[attribute] = input["properties"][attribute]
        else:
            print("Invalid: dynamic not supported")
            return json.dumps(toReturn)
    
    # If you wanted a regular JSON format
    elif not mappings and (type(input) is dict or json or str):
        # Accepts either dicts or JSON strings
        if type(input) is str:
            input = json.loads(input)
        for field in input:
            # Field with arguments
            if type(input[field]) is list:
                toReturn[field] = chooseField(input[field][0], input[field][1:])
            # Field without arguments
            else:
                toReturn[field] = chooseField(input[field])
    
    # No arguments provided
    else:
        print("Invalid argument")
        return json.dumps(toReturn)
    
    return json.dumps(toReturn)