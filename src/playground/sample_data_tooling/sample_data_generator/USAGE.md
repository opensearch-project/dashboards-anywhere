## Example: Police ticketing data

In this example, a PD may store an offender's first and last name, state, ticket price, and license plate. For this PD, say the ticket price ranges from $50 to $300. Thus, the data template format might look something like this:

```
police_template = {
   "offender-first-name": "first_name",
   "offender-last-name": "last_name",
   "state": "state",
   "ticket-price": ["float", {"right_digits": 2, "positive": True, "min_value": 50, "max_value": 300}]
}

generate_data(police_template, False)
'{"offender-first-name": "Aaron", "offender-last-name": "Doyle", "state": "Vermont", "ticket-price": 161.92}'
```

## Example: Birthday tracker

In this example, a senior care center may keep a track of senior citizen's birthdays. For this example, a senior citizen is defined as any person over 65 years old (default maximum is assumed to be 115 years old). Thus, the data template format might look something like this:
```
senior_template = {
   "properties": {
       "first-name": {"type": "first_name"},
       "last-name": {"type": "last_name"},
       "birthday": {"type": ["date_of_birth", {"minimum_age": 65}]}
   }
}

generate_data(senior_template)
'{"first-name": "Amanda", "last-name": "Carney", "birthday": "1933-01-06"}'
```

## Example: Car auction prices

In this example, a sports car auction website may want to keep track of all auctions, including car make, car model, car year, date of auction, and winning final bid price. Assume they have existing statistics to determine that the average final bid "trend" is around $20,000 to $40,000. Thus, the data template might look like below:
```
car_template = {
    "make": "vehicle_make",
    "model": "vehicle_model",
    "year": "vehicle_year",
    "auction_date": ["date_between", "-10y"],
    "final_winning_bid": ["float", {"right_digits": 2, "min_value": 20000, "max_value": 40000}]
}
generate_data(car_template, False)

'{"make": "Mitsubishi", "model": "Aerostar Cargo", "year": "2002", "auction_date": "2014-03-27", "final_winning_bid": 39238.29}'
```
This data was made using the [`faker_vehicle`](https://pypi.org/project/faker-vehicle/) community provider. See [Community Providers](https://faker.readthedocs.io/en/master/communityproviders.html) to install and get a list of more industry-specific data types.

**Note:** In real life, car auctions can have volatility; some auctions may go for huge amounts of money. Some auctions may have a bidding war, the car may be in a rare color or have low miles on the odometer. In the example above, we implicitly defined a trend that tended to occur with auction outcomes (which were outcomes between $20k and $40k). However, in order to throw anomalies in the data, such as higher-than-average final bid prices, see the ingestion tool, wherein the tool provides support for anomaly generation.

Currently, the only data trend fully supported for use with the Anomaly Detection plugin is the `average` trend, with numeric data generated between a specified range.