import os
import re
import numpy as np
import shutil
import zipfile
import multiprocessing

def parseFilesInFolder(filename: str, 
                        zipFilePath: str,
                        out_dir = '/home1/08550/qz3485/workspace/output_data/'
                        ):

    z = zipfile.ZipFile(zipFilePath)
    in_file = z.open(filename,'r') # open file in zip file
    in_data = in_file.read().splitlines()[4:] # read in data from file in zip file
    outfile = open(out_dir+''.join(filename[filename.find('STAR'):filename.find('_',filename.find('STAR'))]) + '.txt', 'a') # names output file as STARLINK-####.txt
    
    # Only get the data for the date specified in the file name
    current_time = float(in_data[0].split()[0])
    tf = current_time+1000000.726
    idx = 0
    while current_time <= tf:
        toks = in_data[idx].split()
        # reads in position and velocity values from data and converts into m and m/s respectively
        pv = np.array(toks[1:],dtype = float)*1000
        # calculates  angular momentum of the data
        h = np.cross(pv[0:3], pv[3:6])
        # Stores position, velocity, and angular momentum as a string
        pvh = np.array2string(np.concatenate((pv,h)))
        # cleans up the string for storage
        pvh = re.sub('\[','',pvh)
        pvh = re.sub('\]','',pvh)
        pvh = re.sub('\n','',pvh)
        # adds converts time in to string and cleans up the string
        time = str(toks[0])
        time = re.sub('^b\'','', time)
        time = re.sub('\'$', ' ', time)
        # writes to the outputfile
        outfile.write(time)
        outfile.write(pvh)
        outfile.write('\n')

        idx = idx + 20
        current_time = float(toks[0])

    in_file.close()
    outfile.close()

if (__name__ == "__main__"):
    rootdir = '/scratch/08550/qz3485/SpaceX_ML'
    out_dir = '/home1/08550/qz3485/workspace/output_data/'

    # deletes the output directory if it exists already
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs('output_data', exist_ok = True)
    
    multiprocessing.set_start_method("spawn")
    # loops through each zipfile in rootdir
    for subdir, dirs, files in os.walk(rootdir):
        # Sort files to be chronological order
        files.sort()

        for file in files: 
            zipFilePath = os.path.join(subdir,file)
            print('Extracting from '+ zipFilePath)
            with zipfile.ZipFile(zipFilePath) as z: # go through zip files    
                filepath_list = []
                for filename in z.namelist(): # parse files in the .zip file
                    if not os.path.isdir(filename): # only parse file, not directory
                        filepath_list.append((filename, zipFilePath))
            
                # Multiprocessing for each file within the zip
                with multiprocessing.Pool(processes=os.cpu_count()) as pool:
                    pool.starmap(parseFilesInFolder, filepath_list)
