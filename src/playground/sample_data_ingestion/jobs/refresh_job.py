# opensearch-py==2.0.0
from opensearchpy import OpenSearch

# Standard libraries
import sys
from os import environ, listdir, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_indices.sample_data_indices import SampleDataIndex
from datetime import date, timedelta, datetime
from shutil import copyfileobj
from os import remove
from math import ceil
from json import load
import gzip


# Array in which unzipped files will be removed
file_removal_array = []


# Utility function for unzipping files
def unzip(filename):
  if type(filename) is not str or (type(filename) is str and ".json" not in filename):
      print("Payload is not a filename or is not a .json file")
      return None
  if type(filename) is str and ".gz" not in filename:
      print("Payload is already unzipped")
      return filename
  with gzip.open(filename, 'rt') as fin:
      with open(filename.split(".gz")[0], 'wb') as fout:
          copyfileobj(fin, fout)
  file_removal_array.append(filename.split(".gz")[0])
  return filename.split(".gz")[0]


# Configurations for connection
HOST = environ.get("HOST")
PORT = 9200
AUTH = (environ.get("SAMPLE_DATA_USERNAME"), environ.get("SAMPLE_DATA_PASSWORD"))


# Constants
DIR_PATH = path.dirname(path.realpath(__file__))
MINUTES_PER_DAY = 1440
CONFIG_PATH = path.join(DIR_PATH.replace("/jobs", ""), "config")

# Establish connection with OS
client = OpenSearch(
    hosts = [{'host': HOST, 'port': PORT}],
    http_compress = True,
    http_auth = AUTH,
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)


# Opening each config file for each plugin
for file in listdir(CONFIG_PATH):
    filename = unzip(file)
    
    # If the file is a JSON file
    if filename:
        # Open the file
        with open(path.join(CONFIG_PATH, filename), 'r') as f:
            config = load(f)
            # Arguments
            template = config["template"]
            mapping = config["mapping"]
            number = int(config["number"])
            dataset = []
            chunk = int(config["chunk"])
            index_name = config["index_name"]
            if config["timestamp"] == "None":
                timestamp = None
            else:
                timestamp = config["timestamp"]
            index_body = config["index_body"]
            feature = config["feature"]
            anomaly_percentage = float(config["anomaly_percentage"])
            avg_min = config["avg_min"]
            avg_max = config["avg_max"]
            minutes = int(config["minutes"])
            abs_min = config["abs_min"]
            abs_max = config["abs_max"]
            days_before = int(config["days_before"])
            days_after = int(config["days_after"])
            calculated_date = date.today()
            create_payload = config["create_payload"]
            file_provided = config["file_provided"]
            plugin = config["plugin"]

            response = client.indices.get(index = (index_name + "*"))

            # If user specifies a date range, index names with dates are appended
            if days_after or days_before:
                for key in response:
                    year = int(key.split("_")[3])
                    day = int(key.split("_")[2])
                    month = int(key.split("_")[1])

                    # Deletes indices > the amount of days before
                    if (datetime.today() - datetime(year, month, day)).days > days_before:
                        index_to_delete = index_name + "_" + str(month) + "_" + str(day) + "_" + str(year)
                        client.indices.delete(index = index_to_delete)
                        print("Deleted index %s" % (index_to_delete))

                # If user specifies minute intervals, number variable will be updated
                if minutes:
                    number = ceil(MINUTES_PER_DAY/minutes)

                # Creates and ingests data for each day after today until days_after variable
                for i in range(days_after + 1):
                    # Creates a new index class with the new date 
                    new_index_date = datetime.now() + timedelta(days = i)
                    new_index_name = index_name + "_" + str(new_index_date.month) + "_" + str(new_index_date.day) + "_" + str(new_index_date.year)
                    new_index_date = datetime(new_index_date.year, new_index_date.month, new_index_date.day)
                    new_index = SampleDataIndex(new_index_name, client, index_body)
                    
                    # If the index doesn't already exist, create it and ingest data into it
                    if not client.indices.exists(index = new_index_name):
                        new_index.create_index()
                        current_date = new_index_date

                        new_index.ingest_more(
                            template = template, 
                            mapping = False, 
                            index_name = new_index_name, 
                            number = number, 
                            chunk = chunk, 
                            timestamp = timestamp, 
                            feature = feature, 
                            anomaly_percentage = anomaly_percentage, 
                            avg_min = avg_min, 
                            avg_max = avg_max, 
                            abs_min = abs_min, 
                            abs_max = abs_max, 
                            minutes = minutes,
                            current_date = current_date
                        )

# Deletes all unzipped config files at the end
for file in file_removal_array:
  remove(file)