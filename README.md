# PFA_Examples
A few basic examples illustrating the use of models specified using PFA (Portable Format for Analytics). This emerging standard (from the Data Mining Group) is a new model interchange format that is capable of encapsulating entire ML pipelines, including complex pre- and post- processing operations.

The examples in the repo are intended to illustrate how easy it is to create your own PFA scoring solutions using available open source implementations of PFA. 

Examples include:

### CSV scoring
     python csv_example.py tests/models/iris_lor_model.pfa tests/data/iris.csv
    
### RESTful scoring
     python web_example.py 9092
     
#### List deployed models
     curl http://localhost:9092/alpine/deploy
#### Upload PFA model
     curl --upload-file tests/models/iris_lor_model.pfa http://localhost:9092/alpine/deploy/my_first_model
#### Download PFA model
     curl http://localhost:9092/alpine/deploy/my_first_model
#### Score a single sample
     curl --data '{"Sepal_length" : "1.0","Sepal_width" : "1.0", "Petal_length" : "1.0","Petal_width" : "1.0"}' http://localhost:9092/alpine/score/my_first_model
#### Get model metrics
     curl http://localhost:9092/alpine/metrics/my_first_model
     
     
# Test resources
* **iris_lor_model.pfa** - A PFA representation of a logisitic regression model trained on the well known Iris data set. This PFA doc can be used on conjunction with the included version of the iris.csv dataset to perform scoring experiments.
* **iris.csv** - A copy of the well known Iris data set, with labels removed.

References:
* http://dmg.org/pfa/index.html
* https://archive.ics.uci.edu/ml/datasets/iris
* https://www.slideshare.net/alpine_data/big-datala-spracklenfinal
