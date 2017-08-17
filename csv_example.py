"""
Basic example illustrating the use of a PFA engine to score a CSV dataset

Leverages the open source Titus PFA engine:
  https://github.com/opendatagroup/hadrian

Requirements:
1) the CSV file is assumed to include a header

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

import json
import csv
import sys
from titus.genpy import PFAEngine

if len(sys.argv) != 3:
    sys.exit("csv_example.py model.pfa data.csv")

pfa_model = sys.argv[1]
data_to_score = sys.argv[2]

# Create PFA engine
pfa_engine, = PFAEngine.fromJson(json.load(open(pfa_model)))

# Initialize PFA engine
pfa_engine.begin()

# Score CSV file
with open(data_to_score) as f:
    # Leverage CSV parser
    reader = csv.reader(f)

    # Grab header -- required to correctly identify inputs
    csv_header = reader.next()

    # Score rows one-by-one
    for row in reader:

        # Create dictionary
        input = dict(zip(csv_header, row))

        # Score row
        results = pfa_engine.action(input)

        print results

