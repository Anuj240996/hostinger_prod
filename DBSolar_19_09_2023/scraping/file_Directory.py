import os

# specify the directory containing the files
dir_path = 'C:\\Users\\deshm\\Downloads\\Daily_Reports\\'

# list all the files in the directory
files = os.listdir(dir_path)
#print(files)
 #sort the files by name
sorted_files = sorted(files)
print(sorted_files)

# extract a substring from each file name using string slicing
substrings = [filename[13:26] for filename in sorted_files]
print(substrings)

#for substring in substrings:
#  print(substring)
#print(max(sorted_files))
