# Sample Data Tooling: Generation

Before using this tool, make sure the required libraries as listed in `requirements.txt` are downloaded. As this tool only generates data entries based on the [Faker library](https://faker.readthedocs.io), running this tool alone does not require configuration of OpenSearch (OS) or OpenSearch Dashboards (OSD). 

Additionally, this tool requires some familiarization of Faker methods and optional arguments to both use this tool and find all supported data types.

## Methods

- `choose_field()`: Given a data type, this function will generate a single data value using Faker
    - **Arguments:**
        - `kind` (string): The type of variable to be generated
            - *ex:* `choose_field("ascii_company_email")` taken directly from [ascii_company_email](https://faker.readthedocs.io/en/master/providers/faker.providers.internet.html#faker.providers.internet.Provider.ascii_company_email)
            ~~~
            >>> choose_field("ascii_company_email")
            'achang@green.info'
            ~~~
            - *ex:* `choose_field("job")` taken directly from [job](https://faker.readthedocs.io/en/master/providers/faker.providers.job.html)
            ~~~
            >>> choose_field("job")
            'Musician'
            ~~~
            - *ex:* `choose_field("float")` taken from `options/custom-field-types.json`
            ~~~
            >>> choose_field("float")
            '-69804.3874773259'
            ~~~
        ### Quick Notes on "kind" Argument
            - Some methods in Faker can be confusing to read, like for instance `ssn`, which is Faker's [social security number](https://faker.readthedocs.io/en/master/providers/faker.providers.ssn.html) generator. To rename the attribute `ssn` to a more readable term such as `social_security_number`, add this configuration to `options/custom-field-types.json` as follows:
            ~~~
            {
                "__comment__": "Define custom field types that map to a Faker attribute",
                "float": "pyfloat",
                "double": "pyfloat",
                "integer": "random_int",
                "date detection string": "boolean",
                "numeric detection string": "boolean",
                "social_security_number": "ssn"
            }
            ~~~
            Now, when you want to generate a social security number, you can now specify `kind` as `social_security_number` in addition to `ssn`, improving readability.
            ~~~
            >>> choose_field("ssn")
            '042-34-8377'
            >>> choose_field("social_security_number")
            '865-50-6891'
            ~~~
            - If you wanted timestamps generated to simulate real-time data ingestion, `unix_time` is the only format currently supported. To configure timestamps for this purpose, see the Ingestion tool.
        - `args` (list): The arguments for `kind`. If you want to specify key word arguments, use a dictionary inside the list.
            - *ex:* `choose_field("float", [2, 3, True])` generates a positive float with two left digits and three right digits. See [pyfloat](https://faker.readthedocs.io/en/master/providers/faker.providers.python.html) for more information on arguments
            ~~~
            >>> choose_field("float", [2, 3, True])
            `24.387'
            ~~~
            - *ex:* `choose_field("file_extension", ["image"])` taken directly from [file_extension](https://faker.readthedocs.io/en/master/providers/faker.providers.file.html) generates an image file format (jpg, png, etc.)
            ~~~
            >>> choose_field("file_extension", ["image"])
            'jpeg'
            ~~~
            - *ex:* `choose_field("file_name", [{"category": "audio"}])` taken directly from [file_name](https://faker.readthedocs.io/en/master/providers/faker.providers.file.html) generates a file name with the `category` argument set to `audio`, which means audio filenames will be generated
            ~~~
            >>> choose_field("file_name", [{"category": "audio"}])
            'career.flac'
            ~~~ 
                - **Note:** Make sure the dictionary is *inside* the list for `choose_field()` to properly parse arguments.
    - **Returns:** 
        - Depending on the data type you specify, `choose_field()` may generate `int`, `float`, `string`, `dicts`, and more
- `generate_data()`: Given an input type (listed below) and a mapping flag, the function generates a document in the specified format
    - **Arguments:**
        - `mapping` (boolean): Whether or not the `input` is a JSON string/dict [mapping](https://opensearch.org/docs/latest/opensearch/mappings/). Currently, only explicit mapping is supported. This value is `True` by default.
        - `input` (JSON string, dictionary, string): The data template of the document to be generated. There are four types of input:
            - `JSON string/dict mapping`: A mapping of the document to be generated. This format allows for users who specify an [explicit mapping](https://opensearch.org/docs/latest/opensearch/mappings/) for their index settings to then just copy the `mappings` value as an argument to `generate_data()`. `mapping` must be set to `True`.

            For this example, say we want to generate bike data, like for instance, prices (between $100 and $1000) and manufacturers. The data template, then, would be as shown below:
            ~~~
            >>> # JSON Mapping as a dict
            >>> bike_template = {
            ...    "properties": {
            ...        "manufacturer": { "type" : "company" }, 
            ...        "price": { "type" : ["integer", 100, 1000]}
            ...    }
            ... }
            >>>
            >>> # JSON Mapping as a string
            >>> bike_template = '{"properties": {"manufacturer": {"type": "company"}, "price": {"type": ["integer", 100, 1000]}}}'
            >>>
            >>> generate_data(bike_template, True)
            '{"manufacturer": "Stout-Moreno", "price": 955}'
            ~~~ 
            In this example, the `price` field had arguments as a list. The arguments can also be a dictionary of key word arguments, in case the user does not need all optional arguments. Again, to see these key word arguments, refer to the Faker library for optional arguments:
            ~~~
            >>> bike_template = {
            ...    "properties": {
            ...        "manufacturer": { "type" : "company" }, 
            ...        "price": { "type" : ["integer", {"min": 100, "max": 1000}]}
            ...    }
            ... }
            ~~~
            - `JSON dict/string "Short-hand"`: Users can define the template as a typical key-value pair. If the data type has arguments, they are written as an array. `mapping` boolean flag must be set to `False`.

            For this example, say we want to generate basic career information about Texan users, including their name, job title, employer, and their zip codes. For this example, such a data template would be as shown below
            ~~~
            >>> # JSON Short-hand as a dict 
            >>> user_career_data_template = {
            ...    "name": "name",
            ...    "job-title": "job",
            ...    "employer": "company",
            ...    "zip-codes": ["array", "zipcode_in_state", "integer", [1, 3],{"state_abbr": "TX"}]
            ... }
            >>>
            >>> # JSON Short-hand as a string
            >>> user_career_data_template = '{"name": "name", "job-title": "job", "employer": "company", "zip-codes": ["array", "zipcode_in_state", "integer", [1, 3], {"state_abbr": "TX"}]}'
            >>>
            >>> generate_data(user_career_data_template, False)
            '{"name": "Andrew Lucas", "job-title": "Gaffer", "employer": "Marquez-Ferguson", "zip-codes": ["79461", "77810"]}'
            ~~~ 
            `zip-codes` is a special type of value. Since we want an array of different TX zip codes, we have to specify some arguments. See [An Aside on Arrays and Keywords](### An Aside on Arrays and Keywords) for more information.

            - `NDJSON filename`: The filename/filename path, zipped or unzipped, for the NDJSON file. A filename can specify multiple data templates and `generate_data()` will return a list of the documents generated.

            For this example, say we want to generate documents containing addresses of movie directors and the year they were born in. Let's also say that we define the data template in `filename.json` as shown below:
            ~~~
            { "year": "year", "addresses": ["array", "address", "integer", [1, 3]], "director": "name"}
            {"properties": { "year":    { "type" : "year"}, "addresses":     { "type" : ["array", "address", "integer", [1, 3]] }, "director":{ "type" : "name" }}}
            ~~~
            In this file, there are two templates that generate the same data template. One template uses `JSON Mapping` while the other uses `JSON Short-hand`. Thus, when we call `generate_data()`:
            ~~~
            >>> generate_data("filename.json")
            ['{"year": "1991", "addresses": ["916 Smith Squares Apt. 039\\nBryanburgh, NV 35476", "8029 Michelle Rue Suite 821\\nMelanieberg, WV 79395", "5481 Nathan Trail Apt. 760\\nEast Allisonport, MN 02571"], "director": "Lauren Colon DVM"}', '{"year": "2002", "addresses": ["071 Miller Springs Apt. 122\\nBrittanyville, KS 96282"], "director": "Brittney Payne"}']
            ~~~
            `generate_data()` returns a list of two documents that correspond to each template we specified in `filename.json`.

            - `CSV filename`: The filename/filename path, zipped or unzipped, for the CSV file.`generate_data()` will return a list of the documents generated. This input format is not recommended for readability reasons.

            For this example, say we want to generate a list of names, their birth years, and their addresses. Let's assume each person will have between one and three addresses. The CSV template file will be as follows:
            ~~~
            year,addresses,name
            year,"[""array"", ""address"", ""integer"", [1, 3]]",name
            ~~~
            
            And when we call `generate_data()`:
            ~~~
            generate_data("filename.csv")
            ['{"year": "2007", "addresses": ["USS Briggs\\nFPO AE 62588", "556 Cobb Spurs\\nWest Georgehaven, WI 29821"], "name": "Timothy Murillo"}']
            ~~~
            `generate_data()` returns a list of the document we just generated.

            In general the CSV template format is as follows:
            ~~~
            <field name 1>,<field name 2>, ...
            [<field type 1>, *args],[<field type 2>, *args], ...
            ~~~

            ### An Aside on Arrays and Keywords
            - OpenSearch has several predefined [value types](https://opensearch.org/docs/latest/opensearch/mappings/), which this generation tool supports. Two special data types are `arrays` and `keywords`, which aren't easily generated by Faker. Thus, the format is defined as follows

            - **For Arrays:** The array has to not only generate the desired type of entry but also the desired number of entries. There are two main scenarios the array supports:  
                - *Generating a random-length array:* This is what is used in the `user_career_data_template` example. The `zip-codes` field generated one to three Texas zipcodes, inclusive, stored in an array.

                In general, the format for this scenario is:
                ~~~
                "<field name>": ["array", "<field type>", "integer", (<min array length>, <max array length>), *args]
                ~~~
                Where `*args` is the same `args` argument as `choose_field()`. `*args` can be left blank.
                - *Generating a fixed-length array:* Using the `user_career_data_template` example, if we wanted each candidate to instead have exactly three Texas zip codes, we would define the `zip-codes` field as follows:
                ~~~
                "zip-codes": ["array", "zipcode_in_state", 3, {"state_abbr": "TX"}]
                ~~~

                In general, the format for this scenario is:
                 ~~~
                "<field name>": ["array", "<field type>", <array length>, *args]
                ~~~
                Where `*args` is the same `args` argument as `choose_field()`. `*args` can be left blank.
            - **For Keywords:** This field may not be needed for most use cases as Faker generates specific data types. However, this datatype is still supported. 

            As an example, let us take the `zip-code` field of `user_career_data_template` again. Instead of making `zip-code` an array of TX zip codes, let's just make it a keyword format instead. Thus, the new field would be:
            ~~~
            {"zip-codes": ["keyword", "zipcode_in_state", {"state_abbr": "TX"}]}
            ~~~

            In general, the format for keyword data types are:
            ~~~
            {"<field name>":  ["keyword", "<field type>", *args]}
            ~~~
            Where `*args` is the same `args` argument as `choose_field()`. `*args` can be left blank.
    - **Returns:**
        - A JSON string representing the document just created. If the `input` argument was a NDJSON or CSV file, a list of JSON string(s) would be returned.