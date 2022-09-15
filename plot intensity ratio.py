import pandas as pd
import os

# load data
data_files_path = r'D:\user_data\javier\21 x tef cheery OEx\Analysis\plate results'

plate_number = 16

# load data files from data_files_path and concat to one dataframe
df_dict = {}
for p in range(1, plate_number+1):
    filename = f'AVG Ratio for plate {p}.txt'  # cur plate datafile
    p_df = pd.read_csv(os.path.join(data_files_path, filename), sep='\t')  # load cur plate datafile
    p_df.insert(loc=0, column='Plate', value=[p] * len(p_df))  # add plate number to dataframe

    df_dict[p] = p_df  # add cur plate dataframe to dictionary

df = pd.concat(df_dict.values(), ignore_index=True)
df.insert(loc=0, column='Plate-Well', value=df['Plate'].astype(str) + df['WellID'])

# plot Intensity Ratio from lowest to highest
df = df.sort_values(by='Intensity Ratio')
df.plot(kind='line', y='Intensity Ratio', x='Plate-Well',
        legend=False, figsize=(25, 10), grid=True, rot=45);





