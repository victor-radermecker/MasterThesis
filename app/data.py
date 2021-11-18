# %%
import pandas as pd
import json
from tqdm.auto import tqdm
import folium
import io
import os

# %%
class DataHandler:
    def __init__(self, preprocess):
        self.preprocess = preprocess
        self.load_data()

    def get_map(self, origin):
        # ChoroPleth Map
        return self.generate_map(origin)

    def load_data(self):

        # Proximus Data
        dir_name = os.getcwd()
        base_filename = "Code\data\proximus\proximusFrequentTrip_RandomlyGenerated.csv"
        data_path = os.path.join(dir_name, base_filename)

        self.df = pd.read_csv(data_path, encoding="unicode_escape",)
        self.ngbh = self.df["originNB"].unique()

        # GeoJson Data
        if self.preprocess:
            base_filename = (
                "Code\data\maps\prox_neighbor\json\RBC_Neighborhoods_gps.json"
            )
        else:
            print("Not preprocessing. Using already preprocessed data.")
            base_filename = "Code\data\maps\prox_neighbor\json\RBC_Neighborhoods_gps_preprocessed.json"

        geo_json_path = os.path.join(dir_name, base_filename)

        with open(geo_json_path) as sectors_file:
            self.geojson = json.load(sectors_file)

        if self.preprocess:
            self.pre_process_geojson()

    def pre_process_geojson(self):
        """This functions adds the features (ex. Number of regular trips) from each origin to each destination into the geojson file.
        """
        print("Preprocessing the original dataset...")
        for origin in tqdm(self.df["originNB"].unique()):
            # Adding the population value to each sector of the geojson file
            subdf = self.df[self.df["originNB"] == origin]
            for index in range(len(self.geojson["features"])):
                temp_dict = self.geojson["features"][index]["properties"]
                val = subdf[subdf["destinationNB"] == temp_dict["NAME_FRE"]][
                    "regularTripSample"
                ]
                if val.empty:
                    val = 0
                else:
                    val = val.item()
                temp_dict[
                    f"RegularTrips_From_{origin}"
                ] = f"Regular Trips From {origin}: " + str(val)
                self.geojson["features"][index]["properties"] = temp_dict

    def generate_map(self, origin):

        # initial map coordinates
        coords = [50.84892175574389, 4.3514911042124345]

        world = folium.Map(
            location=[coords[0], coords[1]], zoom_start=12.45, tiles="openstreetmap"
        )

        # add tile layers to the map
        tiles = [
            "stamenwatercolor",
            "cartodbpositron",
            "openstreetmap",
            "stamenterrain",
        ]
        for tile in tiles:
            folium.TileLayer(tile).add_to(world)

        choropleth = folium.Choropleth(
            geo_data=self.geojson,
            data=self.df[self.df["originNB"] == origin],
            columns=["destinationNB", "regularTripSample"],
            key_on="feature.properties.NAME_FRE",
            fill_color="YlOrRd",
            fill_opacity=0.6,
            line_opacity=0.25,
            legend_name=f"Regular Trips from {origin} to each neighborhoods of Region Brussels Capital",
            highlight=True,
            smooth_factor=0,
        ).add_to(world)

        # Adding Legend to the map
        style_function = "font-size: 15px"
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(
                ["NAME_FRE", f"RegularTrips_From_{origin}"],
                style=style_function,
                labels=False,
            )
        )

        # create a layer control
        folium.LayerControl().add_to(world)

        return world


# %%
if __name__ == "__main__":
    dh = DataHandler()
    world = dh.get_map("ALTITUDE 100")


# %%
