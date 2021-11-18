#!/usr/bin/env python
# coding: utf-8

# `Author: Victor Radermecker | Date: 11/10/2021 | Project: Master Thesis`

# ## Imports

# In[0]:
import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
from tqdm.auto import tqdm
import ipywidgets as widgets
tqdm.pandas()
import json

pd.set_option("display.max_columns", 100)

# In[1]:
# ## Global functions and variables
# ## Geographical Data

# GeoJson Shapefile
sectors_geo = r"../data/maps/prox_neighbor/json/RBC_Neighborhoods_gps.json"

# open the json 
with open(sectors_geo) as sectors_file:
    sectors_json = json.load(sectors_file)


# ## Values for Choropleth Map

# In[2]:

df = pd.read_csv(
    "../data/Proximus/proximusFrequentTrip_RandomlyGenerated.csv",
    encoding="unicode_escape",
)

df.head()


# In[72]:


print("Number of Neighborhoods in Shapefile: ", len(sectors_json['features']))
print("Number of Neighborhoods in Proximus Dataset: ", len(df['originNB'].unique()))


# In[73]:





# ## Generate the Choropleth Map 
# 
# This map shows the number of regular trips from 

# In[113]:


origin = "ALTITUDE 100"

for origin in tqdm(df['originNB'].unique()):
    # Adding the population value to each sector of the geojson file
    subdf = df[df["originNB"] == "ALTITUDE 100"]
    for index in range(len(sectors_json["features"])):
        temp_dict = sectors_json["features"][index]["properties"]    
        val = subdf[subdf["destinationNB"] == temp_dict["NAME_FRE"]]["regularTripSample"]
        if val.empty:
            val = 0
        else:
            val = val.item()
        temp_dict[f"RegularTrips_From_{origin}"] = f"Regular Trips From {origin}: " + str(
            val
        )
        sectors_json["features"][index]["properties"] = temp_dict


# In[117]:


origin_w = widgets.Dropdown(
    options=df['originNB'].unique(),
    value='ALTITUDE 100',
    description='Origin:',
    disabled=False,
)
origin_w


# In[121]:


# initial map coordinates
coords = [50.84892175574389, 4.3514911042124345]

world = folium.Map(
    location=[coords[0], coords[1]], zoom_start=12.45, tiles="openstreetmap"
)

# add tile layers to the map
tiles = ["stamenwatercolor", "cartodbpositron", "openstreetmap", "stamenterrain"]
for tile in tiles:
    folium.TileLayer(tile).add_to(world)

choropleth = folium.Choropleth(
    geo_data=sectors_json,
    data=subdf,
    columns=["destinationNB", "regularTripSample"],
    key_on="feature.properties.NAME_FRE", 
    fill_color="YlOrRd",
    fill_opacity=0.6,
    line_opacity=0.25,
    legend_name="Regular Trips from {origin} to each neighborhoods of Region Brussels Capital",
    highlight=True,
    smooth_factor=0,
).add_to(world)

# Adding Legend to the map
style_function = "font-size: 15px"
choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(
        ["NAME_FRE", f"RegularTrips_From_{origin_w.value}"], style=style_function, labels=False
    )
)

# create a layer control
folium.LayerControl().add_to(world)

world


# In[ ]:




