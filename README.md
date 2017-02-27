# MGH Breast Cancer Pathology Report Project

# How to start service? <br />
You can either setup a docker machine with the right environment to run/use the API, or use the rosetta2 service.   
## Docker Setup 
If you need to run this locally instead of hitting the MIT API, we recommend Docker.
 [dockerfile](dockerfile) shows a working example.

## MIT Server / MGH Server 
If you need to restart it, do: 
export FLASK_APP=classifierAPI.py; 
flask run


# API Usage  <br />
The following API let's you add training data, train models, and get predictions for given reports. Under the hood, it uses boosting for annotation sparse classes and CNN for annotation rich classes. 


For example usage see apiDemo.py, which does everything using the python requests library. 
The api is available at: https://172.17.140.132:5000/\[endpoint\] (under mgh firewall) and https://rosetta7.csail.mit.edu:5000 (upon request in order to avoid hogging gpu resources)

For questions, please ping @yala on slack.
