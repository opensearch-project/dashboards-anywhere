from faker_airtravel import AirTravelProvider
from faker_credit_score import CreditScore
from faker_vehicle import VehicleProvider
from mdgen import MarkdownPostProvider
from faker_wifi_essid import WifiESSID
from faker_music import MusicProvider
from faker_web import WebProvider
import faker_microservice
from faker import Faker

# Standard libraries
from shutil import copyfileobj
from ast import literal_eval
import json
import gzip
import csv
import os


def choose_field(kind, args = None):
    """
    Function that generates fake values for given fields
    This is based off of the Faker library

    Arguments:
        - kind: The "type" of data being generated
        - args: An array of arguments to pass on to Faker

    Returns:
        - A generated value from Faker (could be a string, integer, float, etc.)

    Raises:
        - TypeError : Array size is not configured correctly; check to make sure that args[1] is an integer or a string \"integer\"
    """
    fake = Faker()

    # Adding Community Providers to Faker
    fake.add_provider(AirTravelProvider)
    fake.add_provider(CreditScore)
    fake.add_provider(faker_microservice.Provider)
    fake.add_provider(MarkdownPostProvider)
    fake.add_provider(MusicProvider)
    fake.add_provider(VehicleProvider)
    fake.add_provider(WebProvider)
    fake.add_provider(WifiESSID)

    # This Faker class uses only the Standard Provider and some Community Providers.
    # To see more about Community Providers, visit:
    # https://faker.readthedocs.io/en/master/communityproviders.html
    # and follow instructions there to install them on your environment
    #
    # Example code snippet using the Biology Provider:
    #
    # from faker_biology.physiology import CellType, Organ, Organelle
    # fake.add_provider(CellType)
    # fake.add_provider(Organ)
    # fake.add_provider(Organelle)
    #
    # Another example code snipped using the School Provider:
    #
    # from faker_education import SchoolProvider
    # fake.add_provider(SchoolProvider)

    # "custom-field-types.json" defines what enumerated types return in Faker
    #   - E.g.: "integer" will correspond to Faker's "random_int" attribute
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "options/custom-field-types.json"), "r") as f:
        existing_types = json.load(f)

    # Null: A null type returns nothing
    if kind == "null":
        return None

    # If the user used a data type defined in "custom-field-types.json", it will be executed
    elif kind in existing_types:
        try:
            field_types = getattr(fake, existing_types[kind])
            if args:
                # If the user specifies a map for key word arguments, the function unpacks them
                if len(args) == 1 and type(args[0]) is dict:
                    return field_types(**args[0])

                # If args isn't a map, it will be unpacked as a list/tuple
                return field_types(*args)
            return field_types()
        except Exception as e:
            print(e)
            print("Invalid data type for a user defined data type; check arguments again")
            return None

    # Array: An array type returns an array of field values
    #   There are 2 types: {"type": ["array", <field type>, <int>, *args]}
    #                      {"type": ["array", <field type>, "integer", (min, max), *args]}
    elif kind == "array" and args and len(args) >= 2:
        if type(args[1]) is not int and len(args) < 3:
            print("Invalid Array: if you want a random array length, specify a tuple of ranges")
            return None
        try:
            list = []
            length = 0

            # User specifies a fixed array length
            if type(args[1]) is int:
                for i in range(args[1]):
                    val = choose_field(args[0], args[2:])
                    if val:
                        list.append(val)
                return list
            # User specifies a range of possible array lengths
            elif args[1] == "integer":
                # Length: a randomly generated integer used for the array length to generate
                length = choose_field(args[1], tuple(args[2]))
                for i in range(length):
                    val = choose_field(args[0], args[3:])
                    if val:
                        list.append(val)
                return list
            # Input error
            else:
                raise TypeError("Array size is not configured correctly; check to make sure that args[1] is an integer or a string \"integer\"")
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
            return choose_field(args[0], args[1:])
        except Exception as e:
            print(e)
            print("Invalid Keyword")
            return None

    # Case not explicitly mentioned in OpenSearch field types is tried as a faker attribute
    else:
        try:
            field_types = getattr(fake, kind)
            if args:
                # If the user specifies a map for key word arguments, the function unpacks them
                if len(args) == 1 and type(args[0]) is dict:
                    return field_types(**args[0])

                # If args isn't a map, it will be unpacked as a list/tuple
                return field_types(*args)
            return field_types()
        except Exception as e:
            print(e)
            print("Invalid data type; check data type name or argument list")
            return None


def generate_data(data_template, mappings = True):
    """
    Function to generate data
    Returns a JSON object or a list of JSON objects if a JSON  or CSV file was provided

    Arguments:
        - data_template: See below
            - NDJSON File, zipped or unzipped
            - CSV File, zipped or unzipped
            - Index Mapping (as a JSON string or dict)
                - Note: only explicit mapping is supported and the tool will not support fields within fields
            - JSON "short-hand": {<Field name>: <Field type>}
                - Ex: {"Zip_Code": "zipcode", "Address": "address"}
            - Format for generating data:
                - Paste in your mapping value {"properties": {<properties values>}}
                - Alternatively, pass in a JSON string or string in the form:
                    {<Field>: <Field Type>}
                - If you provide arguments, the <Field Type> should be a list:
                    {<Field>: [<Field Type>, *args]}
        - mappings: A boolean value representing whether the template is a mapping or a short-hand template

    Returns:
        - A JSON string of one generated entry

    Raises:
        - TypeError: Input is not a mapping
        - TypeError: File not supported or could not be found
    """
    data_entry = {}

    if type(data_template) is str and "." in data_template:
        name = data_template.split(".gz")[0]
        # Unzips file if necessary
        if ".gz" in data_template:
            with gzip.open(data_template, 'rb') as fin:
                with open(data_template.split(".gz")[0], 'wb') as fout:
                    copyfileobj(fin, fout)

        # If a JSON file was provided
        if name and ".json" in name:
            JSON_list = []
            with open(name, 'r') as f:
                for line in f:
                    JSON_list.append(generate_data(line, "properties" in line))

            # Deletes unzipped file
            if name != data_template:
                os.remove(name)
            return JSON_list

        # If a CSV file was provided
        elif name and ".csv" in name:
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
                            entry_dict[fields[i]] = literal_eval(entry_dict[fields[i]])
                    CSV_list.append(generate_data(entry_dict, False))

            # Deletes unzipped file
            if name != data_template:
                os.remove(name)
            return CSV_list

        else:
            raise TypeError("File not supported or could not be found")

    # If mappings was provided as the argument
    elif mappings and (type(data_template) is dict or json or str):
        # Accepts either dicts or JSON strings
        if type(data_template) is str:
            data_template = json.loads(data_template)
        if "properties" in data_template:
            for attribute in data_template["properties"]:
                # Field with arguments
                if type(data_template["properties"][attribute]) is dict and type(data_template["properties"][attribute]["type"]) is list:
                    data_entry[attribute] = choose_field(data_template["properties"][attribute]["type"][0], data_template["properties"][attribute]["type"][1:])
                # Field with default arguments
                elif type(data_template["properties"][attribute]) is dict and type(data_template["properties"][attribute]["type"]) is not list:
                    data_entry[attribute] = choose_field(data_template["properties"][attribute]["type"])
                else:
                    print("Invalid: dynamic not supported")
                    data_entry[attribute] = data_template["properties"][attribute]
        else:
            print("Invalid: dynamic not supported")
            raise TypeError("Input is not a mapping")

    # If you wanted a JSON "short-hand" format
    elif not mappings and (type(data_template) is dict or json or str):
        # Accepts either dicts or JSON strings
        if type(data_template) is str:
            data_template = json.loads(data_template)
        for field in data_template:
            # Field with arguments
            if type(data_template[field]) is list:
                data_entry[field] = choose_field(data_template[field][0], data_template[field][1:])
            # Field without arguments
            else:
                data_entry[field] = choose_field(data_template[field])

    # No arguments provided
    else:
        print("Invalid argument")
        return json.dumps(data_entry)

    return json.dumps(data_entry, default = str)