import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import functions as func
import pandas as pd

# experiment data
folder_path = r'D:\user_data\javier\21 x tef cheery OEx'

# loop over plate data
plate_number = 16  # total number of plates
wells_num = 384  # number of wells per plate
positions_num = 3  # number of positions per well

plates_to_analyze = [10]

cur_plate_df = pd.DataFrame()
for plate in range(1, plate_number+1):
    # set plate data directories
    microscope_images_folder = os.path.join(folder_path, f'plate_{plate}', 'data')
    mask_images_folder = os.path.join(folder_path, 'Analysis', f'plate {plate}', 'processed')

    # set well and position:
    for w in range(1, wells_num+1):  # for each well in plate
        WellID = func.conv_wellID_num(w, plate_shape=[16, 24], method='num2ID_row_stack')

        for p in range(1, positions_num+1):  # for each position in the current well
            # set images path
            img_488nm_path = os.path.join(microscope_images_folder, f'{WellID}--W{"{:05}".format(w)}--P{"{:05}".format(p)}--Z00000--T00000--488nm.tif')
            img_CellMask_path = os.path.join(mask_images_folder, f'{WellID}--W{"{:05}".format(w)}--P{"{:05}".format(p)}--Z00000--T00000--CellMask.tif')

            # create 2 new cell masks - cell contour 'cont_mask' and cell without contour 'wo_cont_mask'
            # if no cells are found in the mask: cont_mask, wo_cont_mask = None, None
            cont_mask, wo_cont_mask = func.get_masks(img_CellMask_path)
            # check if the position is empty (no contours found)
            if np.all(cont_mask == 0) or np.all(wo_cont_mask == 0):
                continue

            # quantify 488nm intensity for each one of the segmentations and concat to cur_plate_df
            # each row of the dataframe correspondent to for the specific plate-well-position images
            cur_plate_df = pd.concat([cur_plate_df, func.Quantification(cont_mask, wo_cont_mask, img_488nm_path)])

            print(f'plate {plate}, well {w}, position {p} - DONE!')

    # export cur_plate_df to .txt file
    cur_plate_df.to_csv(os.path.join(folder_path, 'Analysis', 'plate results', f'plate {plate}.txt'), sep='\t')

    # well average analysis:
    # average the data for each well
    well_avg_df = cur_plate_df.groupby(by='Well Number', sort=False, as_index=False).mean()
    # add 'WellID' column to well_avg_df
    well_avg_df.insert(loc=0, column='WellID', value=[func.conv_wellID_num(w, plate_shape=[16, 24], method='num2ID_row_stack') for w in well_avg_df['Well Number']])
    # add column 'Intensity Ratio' - 'Membrane Mean intensity' / 'W_O Membrane Mean intensity'
    well_avg_df['Intensity Ratio'] = well_avg_df['Membrane Mean intensity'] / well_avg_df['W_O Membrane Mean intensity']
    # sort well_avg_df by 'Intensity Ratio'
    well_avg_df = well_avg_df.sort_values(by='Intensity Ratio')
    # export well_avg_df to .txt file
    well_avg_df.to_csv(os.path.join(folder_path, 'Analysis', 'plate results', f'AVG Ratio for plate {plate}.txt'), sep='\t', index=False)

    cur_plate_df = pd.DataFrame()  # initialize for next plate
    print(f'Finished plate {plate} out of {plate_number} plates')

