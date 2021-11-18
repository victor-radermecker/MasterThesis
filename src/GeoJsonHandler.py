import json
from tqdm import tqdm
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import *


class GeoJsonHandler:
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.load_json()
        self.load_names()
        self.add_centers()
        self.update_geopandas()

    def load_json(self):
        # open the json
        with open(self.path) as sectors_file:
            self.geodata = json.load(sectors_file)

    def load_names(self):
        self.names = []
        for index in range(len(self.geodata["features"])):
            self.names.append(
                self.geodata["features"][index]["properties"][self.name]
                .strip()
                .replace("  ", " ")
            )

    def update_geopandas(self):
        # Store GeoPandas Format for future
        self.gdf = gpd.GeoDataFrame.from_features(self.geodata["features"])
        self.gdf["geometry"] = self.gdf["geometry"].set_crs(epsg=4326)

    def add_centers(self):
        data = gpd.GeoDataFrame.from_features(self.geodata["features"])
        data["CENTER"] = data["geometry"].centroid
        data["CENTER_LONG"] = data["geometry"].centroid.x
        data["CENTER_LAT"] = data["geometry"].centroid.y
        # self.add_property(data, "CENTER", verbose=False)
        self.add_property(data, "CENTER_LONG", verbose=False)
        self.add_property(data, "CENTER_LAT", verbose=False)

    def add_property(self, data, value, verbose=True):
        """[summary] 

        Args:
            data ([type]): [description]
            value ([type]): [description]
        """

        # For each feature (each shape)
        for index in range(len(self.geodata["features"])):
            # Extract correct element of GeoJSON
            temp_ = self.geodata["features"][index]["properties"]
            # Extract the property from dataframe
            val = data[data[self.name] == temp_[self.name]][value]

            if val.empty:
                val = 0
            else:
                val = val.item()

            # Store results
            temp_[value] = val
            self.geodata["features"][index]["properties"] = temp_

        self.update_geopandas()

        if verbose:
            print(f"Successfully added {value} property to geodata.")

    def save_json(self, output_path):
        with open(output_path, "w",) as f:
            json.dump(self.geodata, f)
        print(f"Successfully saved geojson.")

    def assign_data_to_neighborhood(self, data, output_path, verbose=False):
        """This function assigns the points of some external data to each sector of the geodata.

            Args:
                data ([Pandas DataFrame]): DataFrame containing three columns:
                    - column1: identifier to each row (example: name of each parking spot)
                    - column2: other property to keep 
                    - column3: longitude name as 'Long'
                    - column4: latitude name as 'Lat'
                output_path ([String]): outpath path to save results in a CSV file.

            Returns:
                [Pandas DataFrame]: Results
            """

        colnames = list(data.columns)
        points = []
        saves = pd.DataFrame(columns=[self.name] + colnames)

        for i in tqdm(range(len(data))):  # all points
            row = data.iloc[i]
            Long, Lat = float(row["Long"]), float(row["Lat"])
            points.append(Point(Long, Lat))
            p = gpd.GeoSeries(Point(float(row["Long"]), float(row["Lat"])))

            for n in range(len(self.names)):  # all sectors

                neighborhood = self.geodata["features"][n]["properties"][self.name]

                if verbose:
                    print(neighborhood)

                nbr_polygons = len(
                    self.geodata["features"][n]["geometry"]["coordinates"]
                )

                for k in range(nbr_polygons):

                    poly_coords = Polygon(
                        np.array(
                            self.geodata["features"][n]["geometry"]["coordinates"][k]
                        ).reshape(-1, 3)
                    )

                    poly = gpd.GeoSeries([poly_coords])

                    res = p.intersects(poly)

                    if res[0]:
                        saves.loc[len(saves)] = [
                            neighborhood,
                            row[colnames[0]],
                            row[colnames[1]],
                            Long,
                            Lat,
                        ]
                        # Found a neighborhood for this point, thus exit the loop
                        break
                if res[0]:
                    break  # Already found a match

        saves.to_csv(output_path, index=False)
        print(f"\n Successfully saved CSV file. \n")
        return saves

