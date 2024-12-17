import os
import time
from tabulate import tabulate

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024


def sizeofFolder(path):
    folderSize = 0
    listItems = os.listdir(path)
    for j in listItems:
        itemPath = os.path.join(path, j)
        if os.path.isfile(itemPath):
            folderSize += os.path.getsize(itemPath)
        else:
            folderSize += sizeofFolder(itemPath)
    return folderSize

def fill_data_for_tabulate(current_dir):
    dirs = os.listdir(current_dir)
    
    data = []

    for i in dirs:
        path = os.path.join(current_dir, i)
    
        if os.path.isfile(path):
            fileName = os.path.basename(path)
            fileSize = os.path.getsize(path)
            sizeName = format_size(fileSize)
            fileDate = time.ctime(os.path.getmtime(path))
            data.append([fileName, sizeName, fileDate])
        else:  
            fileName = f"/{os.path.basename(path)}"
            folderSize = sizeofFolder(path)
            sizeName = format_size(folderSize)
            fileDate = time.ctime(os.path.getmtime(path))
            data.append([fileName, sizeName, fileDate])
    return data

def main():
    path = "/home/faiz/Programming"  # Corrected the path
    current_dir = f"{path}"

    data = fill_data_for_tabulate(current_dir)
    print(tabulate(data, headers=["File Name", "Size", "Date of Creation"], tablefmt="grid"))

if __name__ == "__main__":
    main()
