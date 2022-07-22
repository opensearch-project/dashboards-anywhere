## Example: Police ticketing data

In this example, a PD may store an offender's first and last name, state, ticket price, and license plate. For this PD, say the ticket price ranges from $50 to $300. Thus, the data template format might look something like this:

~~~
>>> police_template = {
...    "offender-first-name": "first_name",
...    "offender-last-name": "last_name",
...    "state": "state",
...    "ticket-price": ["float", {"right_digits": 2, "positive": True, "min_value": 50, "max_value": 300}]
... }
>>>
>>> generate_data(police_template, False)
'{"offender-first-name": "Aaron", "offender-last-name": "Doyle", "state": "Vermont", "ticket-price": 161.92}'
~~~

## Example: Birthday tracker

In this example, a senior care center may keep a track of senior citizen's birthdays. For this example, a senior citizen is defined as any person over 65 years old (default maximum is assumed to be 115 years old). Thus, the data template format might look something like this:
~~~
>>> senior_template = {
...    "properties": {
...        "first-name": {"type": "first_name"},
...        "last-name": {"type": "last_name"},
...        "birthday": {"type": ["date_of_birth", {"minimum_age": 65}]}
...    }
... }
>>>
>>> generate_data(senior_template)
'{"first-name": "Amanda", "last-name": "Carney", "birthday": "1933-01-06"}'
~~~
