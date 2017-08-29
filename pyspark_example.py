"""
Simple example of a PFA scoring engine using PySpark

Leverages the open source Titus PFA engine:
  https://github.com/opendatagroup/hadrian

Copyright 2017 Alpine Data

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
import os
import sys
import json

if len(sys.argv) != 3:
    sys.exit("pyspark_example.py model.pfa hdfs_file.csv")

# Ensure the correct version of python is leveraged on the cluster
os.environ['PYSPARK_PYTHON'] = '/root/anaconda2/bin/python'

# Create Spark context
APP_NAME = 'SPARK-PFA-EXAMPLE'
conf = SparkConf().setAppName(APP_NAME)
sc = SparkContext(conf=conf)
sqlContext = SQLContext(sc)

# Data to be scored -- use DF and Databricks CSV parser
data_to_score = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true').load(
    sys.argv[2])

# Broadcast pfa model
model_name = sys.argv[1]
with open(model_name) as model_file:
    pfa_model = sc.broadcast(json.load(model_file))


def score_model(partition):
    # Create PFA engine
    from titus.genpy import PFAEngine
    engine, = PFAEngine.fromJson(pfa_model.value)

    # Score Partition data row-by-row
    score_results = list()
    for row in partition:
        score_results.append([engine.action(row.asDict())])
    return score_results


# Score data
results = data_to_score.mapPartitions(score_model)

# Print scored results
print results.collect()
