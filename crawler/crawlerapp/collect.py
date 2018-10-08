import h5py
import numpy
import os
from crawlerapp.definitions import *


def collect_hdf5(video_ids,dataset_id):

    download_path = CRAWLED_VIDEOS_DIR
    os.mkdir(os.path.join(download_path, str(dataset_id)))
    output_file_path = os.path.join(download_path,os.path.join(str(dataset_id),str(dataset_id) + ".hdf5"))
    data_file = h5py.File(output_file_path,'w')
    found_folders = [d for d in os.listdir(download_path) if d in video_ids]
    for d in found_folders:
        try:
            align_folder = os.path.join(download_path,os.path.join(d, 'AlignFilter'))
            hdf5_file = os.path.join(align_folder,d + '_words.hdf5')
            f = h5py.File(hdf5_file,'r')

            intervals = f[d]['intervals']
            features = f[d]['features']
            group = data_file.create_group(d)
            group.create_dataset("features",data=features)
            group.create_dataset("intervals",data=intervals)
        except Exception as e:
            print("Couldn't create collect.hdf5")
    data_file.close()
