import sys
import os

# Flags
DEBUG_ENABLE = False  # For dev/debug purpose
PRINT_FILE_DATA = False  # For dev/debug purpose

def file_reader(setupfile):
    try:
        with open(setupfile, 'r+') as uninstallFileObj:
            rawData = uninstallFileObj.read()
            if DEBUG_ENABLE and PRINT_FILE_DATA:
                print(rawData)
            return rawData
    except IOError:
        print("Uninstall failed as record file for installed packages not found", setupfile)
        sys.exit(1)

def del_dir_recur(basePath, pathIndex=2):
    try:
        if DEBUG_ENABLE:
            print("basePath: ", basePath)
        delPath = ""
        dirs = basePath.split('/')
        if DEBUG_ENABLE:
            print("dirs list: ", dirs)
        for index, element in enumerate(dirs):
            if index > (len(dirs) - pathIndex): 
                break
            delPath += element + '/'

        if DEBUG_ENABLE:
            print("delPath: ", delPath)
        
        if os.path.exists(delPath) and (len(os.listdir(delPath)) == 0):
            if DEBUG_ENABLE:
                print("Deleting directory", delPath)
            resp = os.rmdir(delPath)  
            print("Deleted Directory: ", delPath)
            # rmdir deletes empty directory
            if DEBUG_ENABLE:
                print("pathIndex", pathIndex)
            del_dir_recur(delPath, pathIndex)
        elif os.path.exists(delPath) == False:
            if DEBUG_ENABLE: 
                print("Directory does not exist")
                print("recurPath: ", delPath)
            pathIndex += 1
            del_dir_recur(delPath, pathIndex)
        else:
            if DEBUG_ENABLE:
                print("recurPath: ", delPath)
    except OSError as osErr:
        if ("Directory not empty" in osErr ):
            if DEBUG_ENABLE:
                print("Directory not empty, skipping the directory")
        elif ("TypeError" in osErr ):
            if DEBUG_ENABLE:
                print("Directory not empty, skipping the directory")            
        else:
            print("OSError occured: ", osErr)
    except Exception as unhandledErr:
        print("Error Occured: ", unhandledErr)
        sys.exit(1)

def uninstall(rawData):
    try:
        lines = rawData.splitlines()
        for singleLine in lines:
            dirs = singleLine.split('/')
            if DEBUG_ENABLE:
                print("Deleting file", singleLine)
            if os.path.exists(singleLine) and os.path.isfile(singleLine):
                os.remove(singleLine)
                print("Deleted: ", singleLine)
    
        for singleLine in lines:
            dirs = singleLine.split('/')
            pathIndex = 2
            del_dir_recur(singleLine, pathIndex)
    
    except Exception as err:
        print("Error occured: ", err)
        sys.exit(1)

if __name__ == '__main__':
    setupfile = 'setup_file.txt'
    rawData = file_reader(setupfile)
    uninstall(rawData)
    print("Uninstall completed")
    sys.exit(0)
