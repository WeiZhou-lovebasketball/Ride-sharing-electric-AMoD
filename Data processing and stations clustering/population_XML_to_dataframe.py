import matsim
import pandas as pd
from collections import defaultdict
import xml.etree.ElementTree as ET
import time
import datetime

from tqdm import tqdm
import time
import os, sys


def from_fileXML_to_population(
    population_filename,
    network_path="data/network.xml.gz",
):
    tree = ET.parse(population_filename)
    root = tree.getroot()
    print("Reading frozen demand from ", population_filename)
    time.sleep(2)
    d = {
        "Source node id": [],
        "Link": [],
        "x": [],
        "y": [],
        "Pickup time": [],
        "Dest node id": [],
        "Dest link": [],
        "Dest x": [],
        "Dest y": [],
    }
    d1 = {"id": [], "Link": [], "x": [], "y": [], "Dropoff time": []}
    population_source = pd.DataFrame(data=d)
    population_destination = pd.DataFrame(data=d1)
    # 1. NETWORK: Read a MATSim network:
    day_date = ""
    print("The set date is:")
    net = matsim.read_network(network_path)

    nodes = net.nodes
    links = net.links
    print("Types: ", links.dtypes)
    print(len(root))
    for i in range(1, len(root)):
        # print(i)
        source_link = root[i][0][0].attrib["link"]
        time_string = root[i][0][0].attrib["end_time"]
        # print(source_link,i)
        node = links.loc[links["link_id"] == source_link]
        source_node = node.iloc[0]["from_node"]
        node_pd = nodes.loc[nodes["node_id"] == source_node]
        x = node_pd.iloc[0]["x"]
        y = node_pd.iloc[0]["y"]
        # population_source.loc[i] = [source_node,source_link,x,y,time_string]
        # print(i)

        dest_link = root[i][0][2].attrib["link"]
        dest_time_string = root[i][0][2].attrib["start_time"]
        # print(source_link,i)
        node = links.loc[links["link_id"] == dest_link]
        dest_node = node.iloc[0]["from_node"]
        node_pd = nodes.loc[nodes["node_id"] == dest_node]
        dest_x = node_pd.iloc[0]["x"]
        dest_y = node_pd.iloc[0]["y"]
        population_destination.loc[i] = [
            dest_node,
            dest_link,
            dest_x,
            dest_y,
            dest_time_string,
        ]
        population_source.loc[i] = [
            source_node,
            source_link,
            x,
            y,
            time_string,
            dest_node,
            dest_link,
            dest_x,
            dest_y,
        ]
        if i % 100 == 0:
            print(i)

    return population_source, population_destination


pop_from, pop_dest = from_fileXML_to_population(
    "data/population.xml"
)

pop_from.to_csv("requests/pop_orig.csv", index=False)
pop_dest.to_csv("requests/pop_dest.csv", index=False)