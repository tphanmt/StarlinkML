import os
import numpy as np
import shutil
import zipfile
import multiprocessing

def parseFilesInFolder(filename: str, 
                        zipFilePath: str,
                        out_dir = '/home1/08550/qz3485/workspace/output_data/'
                        ):

    z = zipfile.ZipFile(zipFilePath)
    in_file = z.open(filename, mode='r') # open file in zip file
    in_data = in_file.read().splitlines()[4:] # read in data from file in zip file

    numofmin = 5 
    in_data = np.loadtxt(in_data)[::4*numofmin] # grabs data once every numofmin

    # names output directory and filename = STARLINK-####.txt
    outfile_name = out_dir + ''.join(filename[filename.find('STAR'):filename.find('_', filename.find('STAR'))]) + '.txt'

    # selects the first 24 hours of indices
    ind = np.arange(0, int(60/numofmin*24))
    juliantime = in_data[ind, 0:1] 
    pv = in_data[ind, 1:] # position and velocity
    h = np.cross(pv[:, 0:3], pv[:, 3:6]) # calculates angular momentum which is r cross v

    out_data = np.concatenate((juliantime, pv, h), axis=1)

    # Checks if previously saved data overlaps with the start time of current data.
    if os.path.isfile(outfile_name) == True:
        # deletes the overlaps in the previous data
        last_data = np.loadtxt(outfile_name)
        first_time = in_data[0, 0]
        repeats = np.argwhere(last_data[:, 0] >= first_time)
        last_data = np.delete(last_data, repeats, axis=0)
        # stacks the new data under the old data without any overlaps
        out_data = np.concatenate((last_data, out_data), axis=0)

    np.savetxt(outfile_name, out_data)

if (__name__ == "__main__"):
    rootdir = '/scratch/08550/qz3485/SpaceX_ML'
    out_dir = '/home1/08550/qz3485/workspace/output_data/'

    # deletes the output directory if it exists already
    deletedir = input("Want to delete output data? (1 = yes, 0 = no) ")
    if deletedir == "1":
        shutil.rmtree(out_dir, ignore_errors=True)
        os.makedirs(out_dir, exist_ok=True)
    
    multiprocessing.set_start_method("spawn")
    # loops through each zipfile in rootdir
    for subdir, dirs, files in os.walk(rootdir):
        # Sort files to be chronological order
        files.sort()

        for file in files: 
            zipFilePath = os.path.join(subdir, file)
            print('Extracting from ' + zipFilePath)
            with zipfile.ZipFile(zipFilePath) as z: # go through zip files    
                filepath_list = []
                for filename in z.namelist(): # parse files in the .zip file
                    if not os.path.isdir(filename): # only parse file, not directory
                        filepath_list.append((filename, zipFilePath))
            
                # Multiprocessing for each file within the zip
                with multiprocessing.Pool(processes=os.cpu_count()) as pool:
                    pool.starmap(parseFilesInFolder, filepath_list)
