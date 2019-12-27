#Sample code to load data from csv
import sys
sys.path.append('G:/MyDocuments/smartsteel/task/')
from app import DB
objdb= DB()
objdb.load_data('G:/MyDocuments/smartsteel/task/task_data.csv')
#objdb.get_taskdata()

