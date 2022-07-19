# opensearch-py==2.0.0
from opensearchpy import OpenSearch

# Standard libraries
import sys
from os import environ, remove, listdir, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_indices.sample_data_indices import SampleDataIndex
from sample_data_plugins.sample_data_plugin import AnomalyDetection, Alerting
from datetime import date, timedelta, datetime
from shutil import copyfileobj
from time import sleep
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

            # Generate date range of indices (or just 1 if days_after and days_before is 0)
            for i in range(days_after + days_before + 1):
                current_date = date.today()
                can_ingest = True
                index_name_to_create = index_name

                # If user specifies minute intervals, number variable will be updated
                if minutes:
                    number = ceil(MINUTES_PER_DAY/minutes)

                # If user specifies a date range, index names with dates are appended
                if days_after or days_before:
                    calculated_date = date.today() - timedelta(days = (days_before - i))
                    calculated_date = datetime(calculated_date.year, calculated_date.month, calculated_date.day)
                    index_name_to_create = index_name + "_" + str(calculated_date.month) + "_" + str(calculated_date.day) + "_" + str(calculated_date.year)
                    current_date = calculated_date

                # Whether the index exists or not, a new index object is created
                new_index = SampleDataIndex(index_name_to_create, client, index_body)

                # If an index exists, we do not ingest more data as it is assumed that the data is already ingested
                if not client.indices.exists(index = index_name_to_create):
                    new_index.create_index()
                    new_index.ingest_more(
                      file_provided = file_provided, 
                      template = template, 
                      mapping = mapping, 
                      index_name = index_name_to_create, 
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
        URL = "https://" + HOST
        sleep(1)
        if plugin == "anomaly_detection":
            new_detector = AnomalyDetection(index_name = index_name + "*", target_index = "opensearch-ad-plugin-result-index", payload = create_payload, base_url = URL, days_ago = days_before)
            new_detector.create_detector()
            new_detector.start_detector()
            new_detector.start_detector(True)
            

# Deletes all unzipped config files at the end
for file in file_removal_array:
  remove(file)