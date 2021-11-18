import folium
import numpy as np
import geopandas as gpd
import branca.colormap as cm
from GeoJsonHandler import GeoJsonHandler


class BrusselsMap:
    def __init__(self, geojson: GeoJsonHandler, width: int = 800, height: int = 800):
        self.geojson = geojson
        self.width = width
        self.height = height
        self.init_map()
        self.init_colors()

        self.gdf = gpd.GeoDataFrame.from_features(self.geojson.geodata["features"])
        self.gdf["geometry"] = self.gdf["geometry"].set_crs(epsg=4326)

    def init_map(self):
        # Brussels coordinates
        coords = [50.84892175574389, 4.3514911042124345]
        self.map = folium.Map(
            width=self.width,
            height=self.height,
            location=[coords[0], coords[1]],
            zoom_start=12.45,
            tiles="openstreetmap",
        )
        self.add_tiles()

    def add_tiles(self):
        # add tile layers to the map
        tiles = [
            "stamenwatercolor",
            "cartodbpositron",
            "openstreetmap",
            "stamenterrain",
        ]
        for tile in tiles:
            folium.TileLayer(tile).add_to(self.map)

        # create a layer control
        folium.LayerControl(position="bottomleft").add_to(self.map)

    def add_markers(self, data, icon="car", color=None):
        """Adds markers to points of Folium Map.

        Args:
            data ([Pandas DataFrame]): Pandas Frame containing details about points to plot. 
            Format: 
                - Column1: Name of point of Interest
                - Column2: Longitude (GPS coordinates system)
                - Column3: Latitude (GPS coordinates system)
                - Column4: type of each marker (if applicable)
        
        List of Folium icons available here: https://fontawesome.com/v4.7/icons/
        """

        names = list(data.columns)

        if len(names) == 3:
            points = list(zip(data.iloc[:, 0], data.iloc[:, 1], data.iloc[:, 2]))
        else:
            points = list(
                zip(data.iloc[:, 0], data.iloc[:, 1], data.iloc[:, 2], data.iloc[:, 3])
            )

        for point in points:
            label = "{}: {},\n Longitude: {}, \n Latitude: {}".format(
                str(names[0]), point[0], str(point[1]), point[2]
            )
            popup = folium.Popup(label, autopan="False", parse_html=True)

            if len(names) == 3 and color == None:
                color = self.colors[0]
            elif len(names) == 4:
                color = self.colors[point[3]]

            folium.Marker(
                location=[point[2], point[1]],
                popup=popup,
                icon=folium.Icon(color=color, icon=icon, prefix="fa"),
            ).add_to(self.map)

    def add_choropleth(self, data, legend=None, labels=False):
        """This function adds a choropleth map on top of the Folium map. 

        Args:
            geodata ([json object]): Json file describing the limites of shapes of choropleth map. Should contain properties: name matching with pandas dataframe. 
            data ([Pandas DataFrame]): DataFrame containing two columns. 
                - Column1: Names (of each regions) matching with GeoJson. Column name should match with Geodata object.
                - Column2: Values to assign to each region.
            legend ([Str], optional): Text to show near the legend. Defaults to None.
            labels ([Boolean]): Indicating whether or not add labels when mouse hover a region. Note that the geojson file has to have the value property.

            --- Reminder: Typical GeoJson Format:
            Dictionary FeatureCollection having for key 'features' a list of features.
                {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [125.6, 10.1]},
                "properties": {
                    "name": "Dinagat Islands"}
                }
        """

        colnames = list(data.columns)

        choropleth = folium.Choropleth(
            geo_data=self.geojson.geodata,
            data=data,
            columns=[colnames[0], colnames[1]],
            key_on=f"feature.properties.{colnames[0]}",
            color="black",
            fill_color="YlOrRd",
            # threshold_scale=scale,
            fill_opacity=0.6,
            line_opacity=0.25,
            legend_name="Regular Trips from {origin} to each neighborhoods of Region Brussels Capital",
            highlight=True,
            smooth_factor=0,
        ).add_to(self.map)

        if labels:
            # Adding Legend to the map
            style_function = "font-size: 15px"
            choropleth.geojson.add_child(
                folium.features.GeoJsonTooltip(
                    [colnames[0], colnames[1]], style=style_function, labels=False,
                )
            )

    def add_choropleth_style2(
        self, data, legend=None, nbr_steps=10, colormap_type="step", colormap=None
    ):

        colnames = list(data.columns)
        max_value = max(data[colnames[1]])

        if colormap_type == "manual":
            colormap = colormap
        if colormap_type == "quant":
            colormap = cm.linear.YlOrRd_05.to_step(
                method="quantiles", data=data[colnames[1]], n=nbr_steps,
            ).scale(0, max_value)
        elif colormap_type == "linear":
            colormap = cm.linear.YlGnBu_05.scale(0, max_value)
        elif colormap_type == "step":
            colormap = cm.LinearColormap(
                colors=["white"] + cm.linear.YlOrRd_04.colors + ["black"],
                index=[-500] + list(np.linspace(max_value / 100, max_value, 5)),
                vmin=0,
                vmax=max_value,
            ).to_step(nbr_steps)

        colormap.caption = legend

        style_function = lambda x: {
            "weight": 0.5,
            "color": "black",
            "fillColor": colormap(x["properties"][colnames[1]]),
            "fillOpacity": 0.65,
        }

        highlight_function = lambda x: {
            "fillColor": "#000000",
            "color": "#000000",
            "fillOpacity": 0.50,
            "weight": 0.1,
        }

        dpop = gpd.GeoDataFrame.from_features(self.geojson.geodata["features"])
        dpop["geometry"] = dpop["geometry"].set_crs(epsg=4326)

        NIL = folium.features.GeoJson(
            data=self.geojson.gdf[["geometry", colnames[0], colnames[1]]],
            style_function=style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip=folium.features.GeoJsonTooltip(
                fields=[colnames[0], colnames[1]],
                aliases=["Neighborhood", colnames[1]],
                style=(
                    "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
                ),
                sticky=True,
            ),
        )
        colormap.add_to(self.map)
        self.map.add_child(NIL)

    def init_colors(self):

        self.colors = [
            "red",
            "orange",
            "gray",
            "lightblue",
            "blue",
            "green",
            "purple",
            "darkred",
            "lightred",
            "beige",
            "darkblue",
            "darkgreen",
            "cadetblue",
            "darkpurple",
            "white",
            "pink",
            "lightgreen",
            "black",
            "lightgray",
        ]

