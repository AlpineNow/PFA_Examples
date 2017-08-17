# PFA_Examples
A few basic examples illustrating the use of models specified using PFA (Portable Format for Analytics). This emerging standard (from the Data Mining Group) is a new model interchange format that is capable of encapsulating entire ML pipelines, including complex pre- and post- processing operations.

The examples in the repo are intended to illustrate how easy it is to create your own PFA scoring solutions using available open source implementations of PFA. 

Examples include:

### CSV scoring
     python csv_example.py tests/models/iris_lor_model.pfa tests/data/iris.csv
     
# Test resources
* **iris_lor_model.pfa** - A PFA representation of a logisitic regression model trained on the well known Iris data set. This PFA doc can be used on conjunction with the included version of the iris.csv dataset to perform scoring experiments.
* **iris.csv** - A copy of the well known Iris data set, with labels removed.

References:
* http://dmg.org/pfa/index.html
* https://archive.ics.uci.edu/ml/datasets/iris
* https://www.slideshare.net/alpine_data/big-datala-spracklenfinal
