# poetry run python3 kml_merger/main.py
import geopandas as gpd
import pandas as pd
import os
import tempfile
from zipfile import ZipFile
from fiona.drvsupport import supported_drivers

supported_drivers['KML'] = 'rw'


def summarize_dir(directory):
    first = True
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            print(f)
            s = suffix(f)
            if s == ".kml":
                df = df_from_kml(f)
            elif s == ".kmz":
                df = df_from_kmz(f)
            else:
                print("continuing",s)
                continue
            # print(df.geom_type)
            # breakpoint()
            df = clean_df(df)
            if first:
                combined_df = df
                print(combined_df.columns)
                print(combined_df['wt'] )
                first = False
            else:
                print(".")
                print(combined_df.columns)
                combined_df = combined_df.overlay(df, how="union", keep_geom_type=True)

                # combined_df['wt'] = combined_df['wt_1']
                combined_df = clean_df(combined_df)
                print(combined_df['wt'] )
                combined_df = clean_columns(combined_df)
                print(combined_df.columns)
                print("..")
    return combined_df

def combine_with_sum(df1, df2):
    combined_df = df1.overlay(df2, how="union")
    # print(combined_df.columns)
    # breakpoint()
    combined_df['wt']=combined_df['wt_1'].fillna(0) + combined_df['wt_2'].fillna(0)
    return clean_columns(combined_df)

def clean_columns(df):
    for col in df.columns:
        if col != "wt" and col != "geometry":
            df = df.drop(col, axis=1)
    return df



def suffix(f):
    split_tup = os.path.splitext(f)
    return split_tup[1].lower()

def df_from_kml(filename):
    return gpd.read_file(filename, driver='KML')


def df_from_kmz(filename):
    kmz = ZipFile(filename, 'r')
    with tempfile.TemporaryDirectory() as tempDir:
        kmz.extract('doc.kml',tempDir)
        return gpd.read_file(os.path.join(tempDir,'doc.kml'), driver='KML')


# add a column with weight constant
def clean_df(df):
    df['id'] = pd.Series([x for x in range(len(df.index))])
    df['wt'] = pd.Series([1 for x in range(len(df.index))])
    df['series'] = pd.Series([1 for x in range(len(df.index))])
    df.set_index('id', inplace = True)
    df["geometry"] = df.buffer(0)
    df = df.dissolve(by="series")
    return df


# df1 = gpd.read_file('../data/aaryn/kml/172-175.kml', driver='KML')
# filename = '../data/scarlet/Buffelgrass_172_sj.kmz'

def main():
    aaryn_df = summarize_dir('../data/aaryn/kml')
    aaryn_df.to_file('aaryn.shp')
    kim_df = summarize_dir('../data/Kim_Franklin_Data')
    kim_df.to_file('kim.shp')
    scarlet_df = summarize_dir('../data/scarlet')
    scarlet_df.to_file('scarlet.shp')

    combined_df = combine_with_sum(aaryn_df, scarlet_df)
    combined_df = combine_with_sum(combined_df, kim_df)
    combined_df.to_file('combined.shp')




if __name__ == "__main__":
    main()