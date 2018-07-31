import h5py
import numpy
import os
from definitions import CONFIG_PATH


def collect_hdf5(video_ids):
    data_file = h5py.File('collected.hdf5','w')
    
    download_path = os.path.join(CONFIG_PATH,'downloaded_videos')
    found_folders = [d for d in os.listdir(download_path) if d in video_ids]
    print(found_folders)
    for d in found_folders:
        align_folder = os.path.join(download_path,os.path.join(d, 'AlignFilter'))
        hdf5_file = os.path.join(align_folder,d + '_words.hdf5')
        f = h5py.File(hdf5_file,'r')
            
        intervals = f[d]['intervals']
        features = f[d]['features']
        group = data_file.create_group(d)
        group.create_dataset("features",data=features)
        group.create_dataset("intervals",data=intervals)
    data_file.close()


