import json
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
from shapely.geometry import *
import numpy as np

# Used to measure the length of lines
from shapely.geometry import LineString
from shapely.ops import transform
from functools import partial
import pyproj

# Local packages
from GeoJsonHandler import GeoJsonHandler


class OSMGeoJsonHandler:
    def __init__(self, path, feature_type):
        self.path = path
        self.feature_type = feature_type
        self.load_json()
        self.create_geodataframe()

    def load_json(self):
        # open the json
        with open(self.path, encoding="utf-8") as fh:
            self.geodata = json.load(fh)

    def create_geodataframe(self):

        self.gdf = gpd.GeoDataFrame.from_features(self.geodata["features"])

        if self.feature_type in ["university", "health"]:
            self.gdf.rename(
                columns={"id": "ID", "name": "NAME", "amenity": "AMENITY"},
                inplace=True,
            )
            self.gdf[["TYPE", "ID"]] = self.gdf["ID"].str.split("/", expand=True)
            self.gdf = self.gdf[["ID", "TYPE", "NAME", "AMENITY", "geometry"]]

            self.gdf.sort_values(by="TYPE", ascending=False)
            self.gdf.drop_duplicates(subset="ID", keep="first", inplace=True)

        elif self.feature_type == "residential":
            self.gdf.rename(
                columns={"@id": "ID", "name": "NAME", "landuse": "LANDUSE"},
                inplace=True,
            )
            self.gdf[["TYPE", "ID"]] = self.gdf["ID"].str.split("/", expand=True)
            self.gdf = self.gdf[["ID", "TYPE", "NAME", "LANDUSE", "geometry"]]

            # Drop LineString elements
            self.gdf = self.gdf.drop(
                self.gdf[self.gdf["geometry"].type == "LineString"].index
            )

            # For the relations, we have separate lines for Points and Polygons
            # We sort the dataframes to make sure that all the "points" are at the bottom because the drop_duplicates
            # will only keep the first elements.
            self.gdf.sort_values(by="TYPE", ascending=False)
            self.gdf.drop_duplicates(subset="ID", keep="first", inplace=True)

        elif self.feature_type == "sport":
            self.gdf.rename(
                columns={"id": "ID", "name": "NAME",}, inplace=True,
            )
            self.gdf[["TYPE", "ID"]] = self.gdf["ID"].str.split("/", expand=True)
            self.gdf = self.gdf[["ID", "TYPE", "NAME", "geometry"]]

            # Drop LineString elements
            self.gdf = self.gdf.drop(
                self.gdf[self.gdf["geometry"].type == "LineString"].index
            )

        elif self.feature_type in ["sustenance", "health", "culture"]:
            self.gdf.rename(
                columns={"id": "ID", "name": "NAME", "amenity": "AMENITY"},
                inplace=True,
            )
            self.gdf[["TYPE", "ID"]] = self.gdf["ID"].str.split("/", expand=True)
            self.gdf = self.gdf[["ID", "TYPE", "NAME", "AMENITY", "geometry"]]

        elif self.feature_type in ["shop", "office", "tourism", "residential"]:
            self.gdf.rename(
                columns={"id": "ID", "name": "NAME",}, inplace=True,
            )
            self.gdf[["TYPE", "ID"]] = self.gdf["ID"].str.split("/", expand=True)
            self.gdf = self.gdf[["ID", "TYPE", "NAME", "geometry"]]

        elif self.feature_type in ["lanes"]:
            self.gdf.rename(
                columns={"@id": "ID", "name": "NAME",}, inplace=True,
            )
            self.gdf[["TYPE", "ID"]] = self.gdf["ID"].str.split("/", expand=True)
            self.gdf = self.gdf[["ID", "TYPE", "NAME", "geometry"]]
            self.compute_length()

        elif self.feature_type in ["parking"]:
            self.gdf.rename(
                columns={"@id": "ID", "name": "NAME",}, inplace=True,
            )
            self.gdf[["TYPE", "ID"]] = self.gdf["ID"].str.split("/", expand=True)
            self.gdf = self.gdf[["ID", "TYPE", "NAME", "geometry"]]

        # Convert back to GeoDataFrame
        self.gdf = gpd.GeoDataFrame(self.gdf)
        self.compute_area()
        self.get_center()

    def compute_area(self):
        # Explanation aobut why should we use this CRS projection to comute the area?
        # Available here: https://gis.stackexchange.com/questions/218450/getting-polygon-areas-using-geopandas
        gdf = gpd.GeoDataFrame(self.gdf)
        gdf["geometry"] = gdf["geometry"].set_crs(epsg=4326)
        temp_ = gdf["geometry"].to_crs("epsg:32633")

        self.gdf["AREA"] = temp_.area / 1e6

        if self.feature_type in [
            "university",
            "health",
            "culture",
            "office",
            "tourism",
        ]:
            # Fill null areas with the median (not the average as there are too many extreme values)
            self.gdf["AREA"].replace(
                0, self.gdf[self.gdf["AREA"] != 0]["AREA"].median(), inplace=True
            )

        elif self.feature_type == "residential":
            pass  # @TODO

        elif self.feature_type in ["sustenance", "parking"]:
            print(len(self.gdf["AREA"][self.gdf["AREA"] == 0]))
            # Fill null areas with the mean
            #self.gdf["AREA"].replace(
            #    0, self.gdf[self.gdf["AREA"] != 0]["AREA"].mean(), inplace=True
            #)

    def get_center(self):
        self.gdf["LAT"] = self.gdf.centroid.y
        self.gdf["LON"] = self.gdf.centroid.x

    def assign_ngh(self, ngh: GeoJsonHandler, verbose=False):
        """This function adds a 'NEIGH' column to a OSMGeoJsonHandler object. This new column gives the neighborhood in which the object belong.

        Args:
            ngh (GeoJsonHandler): OSMGeoJsonHandler - detailing the simits of each sector. (see GeoJsonHanlder documentation)
            verbose (bool, optional): [description]. Defaults to False.
        """
        points = []

        self.gdf["NAME_FRE"] = ""

        for i in tqdm(range(len(self.gdf))):  # all points
            row = self.gdf.iloc[i]
            lon, lat = float(row["LON"]), float(row["LAT"])
            points.append(Point(lon, lat))
            p = gpd.GeoSeries(Point(float(row["LON"]), float(row["LAT"])))

            for n in range(len(ngh.names)):  # all sectors

                neighborhood = ngh.geodata["features"][n]["properties"][ngh.name]

                nbr_polygons = len(
                    ngh.geodata["features"][n]["geometry"]["coordinates"]
                )

                for k in range(nbr_polygons):

                    poly_coords = Polygon(
                        np.array(
                            ngh.geodata["features"][n]["geometry"]["coordinates"][k]
                        ).reshape(-1, 3)
                    )

                    poly = gpd.GeoSeries([poly_coords])

                    res = p.intersects(poly)

                    if res[0]:
                        self.gdf["NAME_FRE"].iloc[i] = neighborhood
                        break
                if res[0]:
                    break  # Already found a match

    def compute_length(self):

        # Geometry transform function based on pyproj.transform
        project = partial(
            pyproj.transform, pyproj.Proj("EPSG:4326"), pyproj.Proj("EPSG:32633")
        )
        self.gdf["length"] = self.gdf["geometry"].progress_apply(
            lambda line: transform(project, line).length
        )

