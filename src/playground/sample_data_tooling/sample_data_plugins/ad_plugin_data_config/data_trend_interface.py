from datetime import datetime

class DataTrend():
    """
    Abstract Class that generates data based on a generic trend. The idea with the DataTrend class is that
    this class mutates an existing document, and it does not generate a new dataset. This is because in the
    ingest() function, it is already generating random documents. What DataTrend does is that it modifies each
    document such that the one specific field (or multiple) now possesses a data trend with anomalies. Since this
    class cannot generate multiple documents, some form of implementation is necessary to "plot" data. This could
    be something such as defining a delta between data points.

    For example, if you wanted a linear regression, say y = 7x, when defining implementing generate_data_trend, as
    you are generating documents, you could have a "new_value" argument set to 7 times the previous document's value
    (in order to get this previous value, you could return a tuple containing the new value and document generated).
    To add a bit of noise so that the data trend isn't a perfect line, you could also have an argument "data_range"
    such that the actual data generated falls between new_value +- data_range. To generate anomalies, implement
    generate_noise() such that the data generated could become far above or below the "new_value"

    Methods:
        - generate_noise(): Generates anomalies in the trend data
        - generate_data_trend(): Generates a user-defined data trend

    Arguments;
        - feature: The field that will be used to test anomalies
        - timestamp: The field name that contains timestamps
        - current_date: The date at which entries are generated

    Raises:
        - TypeError: Variable \"feature\" must be a string
        - TypeError: timestamp is the field name that contains the timestamp, not the actual unix timestamp
        - TypeError: current_date is a datetime object
    """
    def __init__(self,
        feature,
        timestamp,
        current_date
    ):

        # Input validation
        if type(feature) is not str:
            raise TypeError("Variable \"feature\" must be a string")
        if type(timestamp) is not str:
            raise TypeError("timestamp is the field name that contains the timestamp, not the actual unix timestamp")
        if type(current_date) is not datetime:
            raise TypeError("current_date is a datetime object")

        self.feature = feature
        self.timestamp = timestamp
        self.current_date = current_date

    def generate_noise(self):
        """
        This function should be used to generate anomalies. Whether trend data was generated before calling this
        or not, in order to generate anomalies, a document must have an existing value. This function should either leave the
        existing value as is or mutate it with an outlier.
        """
        pass

    def generate_data_trend(self):
        """
        This function should be used to generate trends in data. Given an existing document, this function should
        modify the specified field value to fit a data trend (which the user defines in a child class of DataTrend).
        """
        pass
