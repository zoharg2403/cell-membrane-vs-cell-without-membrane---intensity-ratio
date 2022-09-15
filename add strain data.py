import pandas as pd
import re
import os

# load strain data file
strain_df = pd.read_excel('List of genes 210 x Tef Cherry oex Javier.xlsx',
                          usecols=['ORF', 'Gene', '384 Plate_Row_Col'])
# edit '384 Plate_Row_Col' column into more usable 3 columns 'Plate', 'Row', 'Column':
# split '384 Plate_Row_Col' column into list (split when the character is a number)
# then take items [1, 2, 3] from the list ([plate, row, column])
# turn to a list of lists, and then into a dataframe with columns names 'Plate', 'Row', 'Column'
# join 'Row', 'Column' columns to one 'WellID' column
# concat with strain_df['ORF', 'Gene'] columns
strain_df = strain_df.join(pd.DataFrame(strain_df['384 Plate_Row_Col'].apply(lambda s: list(re.split('(\d+)', s))[1:4])
                                    .tolist(), columns=['Plate', 'Row', 'Column']))
strain_df = strain_df.drop(columns='384 Plate_Row_Col')
strain_df['WellID'] = strain_df['Row'] + strain_df['Column']

# iterate over results data files and add 'ORF' and 'Gene' columns:

# set directory and file names
results_files_path = r'D:\user_data\javier\21 x tef cheery OEx\Analysis\image processing\plate results'
results_files_list = [f for f in os.listdir(results_files_path) if f.endswith('txt')]

for f in results_files_list:
    plat_num = list(re.split('(\d+)', f))[1]  # get current plate number from filename 'f'
    # strain data for current plate
    cur_strain_data = strain_df[strain_df["Plate"] == plat_num].drop(columns=['Plate', 'Row', 'Column'])
    # plate resultes file for current plate
    cur_results_df = pd.read_csv(os.path.join(results_files_path, f), sep='\t')  # load current file
    # merge dataframes by 'WellID' column
    cur_results_w_strains = pd.merge(cur_strain_data, cur_results_df, on="WellID")
    # sort by 'Intensity Ratio' if column exist
    if 'Intensity Ratio' in cur_results_df.columns:
        cur_results_w_strains = cur_results_w_strains.sort_values(by='Intensity Ratio')
    # export cur_results_w_strains
    cur_results_w_strains.to_csv(os.path.join(results_files_path, 'W strains', f), sep='\t', index=False)
    print(f)









