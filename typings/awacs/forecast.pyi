"""
This type stub file was generated by pyright.
"""

from .aws import Action as BaseAction
from .aws import BaseARN

service_name = "Amazon Forecast"
prefix = "forecast"

class Action(BaseAction):
    def __init__(self, action=...) -> None: ...

class ARN(BaseARN):
    def __init__(self, resource=..., region=..., account=...) -> None: ...

CreateDataset = Action("CreateDataset")
CreateDatasetGroup = Action("CreateDatasetGroup")
CreateDatasetImportJob = Action("CreateDatasetImportJob")
CreateForecast = Action("CreateForecast")
CreateForecastExportJob = Action("CreateForecastExportJob")
CreatePredictor = Action("CreatePredictor")
DeleteDataset = Action("DeleteDataset")
DeleteDatasetGroup = Action("DeleteDatasetGroup")
DeleteDatasetImportJob = Action("DeleteDatasetImportJob")
DeleteForecast = Action("DeleteForecast")
DeleteForecastExportJob = Action("DeleteForecastExportJob")
DeletePredictor = Action("DeletePredictor")
DescribeDataset = Action("DescribeDataset")
DescribeDatasetGroup = Action("DescribeDatasetGroup")
DescribeDatasetImportJob = Action("DescribeDatasetImportJob")
DescribeForecast = Action("DescribeForecast")
DescribeForecastExportJob = Action("DescribeForecastExportJob")
DescribePredictor = Action("DescribePredictor")
GetAccuracyMetrics = Action("GetAccuracyMetrics")
ListDatasetGroups = Action("ListDatasetGroups")
ListDatasetImportJobs = Action("ListDatasetImportJobs")
ListDatasets = Action("ListDatasets")
ListForecastExportJobs = Action("ListForecastExportJobs")
ListForecasts = Action("ListForecasts")
ListPredictors = Action("ListPredictors")
ListTagsForResource = Action("ListTagsForResource")
QueryForecast = Action("QueryForecast")
TagResource = Action("TagResource")
UntagResource = Action("UntagResource")
UpdateDatasetGroup = Action("UpdateDatasetGroup")