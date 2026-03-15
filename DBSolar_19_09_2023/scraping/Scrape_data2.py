import pandas as pd
import sqlite3
from datetime import datetime
import os

# specify the directory containing the files
dir_path = 'C:\\Users\\deshm\\Downloads\\Daily_Reports2\\'

#  list all the files in the directory
files = os.listdir(dir_path)
# print(files)

# sort the files by name
sorted_files = sorted(files)
print(sorted_files)


# # define the directory and file name as variables
file_name = max(sorted_files)

# create the full file path by joining the directory and file name variables
file_path = os.path.join(dir_path, file_name)

# read the Excel file into a Pandas DataFrame
df = pd.read_excel(file_path)
print(df[22:23])


# add a new column with today's date
today = datetime.today().strftime('%Y-%m-%d')
df['Date'] = today


# # Open a connection to the SQLite database
# conn = sqlite3.connect('C:\\Users\\deshm\\PycharmProjects\\Django-Inventory-Management-System-master - dashboard complaint update 26-3-23\\db.sqlite3')
#
# # Create a cursor object to execute SQL statements
# cur = conn.cursor()
#
# # Create a table in the database
# #cur.execute('drop TABLE Meter_Reports3')
#
# cur.execute('CREATE TABLE Meter_Reports3 (Plant text,PV_Capacity_kWp Integer,Self_consumption_electricity_kWh Integer,Export_To_Grid_kWh Integer,Generation_kWh Integer,Revenue_Rs Integer,Co₂_Reduced_kg Integer,Date date,Source Text)')
