import pandas as pd
import sqlite3
from datetime import datetime
import os

# specify the directory containing the files
dir_path = 'C:\\Users\\deshm\\Downloads\\Daily_Reports\\'
#
#  list all the files in the directory
files = os.listdir(dir_path)
 #print(files)
#
#  #sort the files by name
sorted_files = sorted(files)
print(sorted_files)
#
# # extract a substring from each file name using string slicing
# timestamps = [filename[13:27] for filename in sorted_files]
# print(timestamps)
#
# for i in timestamps:
#     print(i)
#
# # extract a substring from each file name using string slicing
# #substrings = [filename[13:26] for filename in sorted_files]
# #print(substrings)
#
# # define the directory and file name as variables
file_name = max(sorted_files)

# create the full file path by joining the directory and file name variables
file_path = os.path.join(dir_path, file_name)

# read the Excel file into a Pandas DataFrame
df = pd.read_excel(file_path)
#print(df)


# add a new column with today's date
today = datetime.today().strftime('%Y-%m-%d')
df['Date'] = today


# Open a connection to the SQLite database
conn = sqlite3.connect('C:\\Users\\deshm\\PycharmProjects\\Django-Inventory-Management-System-master - new & list  profile create  5-3-23\\db.sqlite3')

# Create a cursor object to execute SQL statements
cur = conn.cursor()

# Create a table in the database
cur.execute('drop TABLE Meter_Reports')

cur.execute('CREATE TABLE Meter_Reports(Plant text,Installed_Power Integer,Today_Yield Integer,Total_Yield Integer,Today_Revenue Integer, Total_CO2_Reduction Integer, Date date,Source Text)')
#Insert the data into the table
for i in range(len(df[4::])):
    cur.execute('INSERT INTO Meter_Reports ( Plant, Installed_Power, Today_Yield, Total_Yield, Today_Revenue, Total_CO2_Reduction, Date,Source) VALUES (?,?,?,?,?,?,?,"IND_1")', tuple(df[4::].iloc[i]))


cur.execute('drop TABLE Meter_Reports_2')

cur.execute('CREATE TABLE Meter_Reports_2 (Today_Yield_MWh float,Total_Yield_GWh float,Total_CO₂_reduction_kg float,Today_CO₂_reduction_kg float,Today_Revenue_INR float,Cumulative_Total_Revenue_INR float,Date date,Source Text)')

for i in range(len(df[1:2])):
    cur.execute('INSERT INTO Meter_Reports_2 (Today_Yield_MWh,Total_Yield_GWh,Total_CO₂_reduction_kg,Today_CO₂_reduction_kg,Today_Revenue_INR,Cumulative_Total_Revenue_INR,Date,Source) Values (?,?,?,?,?,?,?,"IND_1")', tuple(df[1:2].iloc[i]))

#Commit the changes to the database and close the connection
conn.commit()
conn.close()
