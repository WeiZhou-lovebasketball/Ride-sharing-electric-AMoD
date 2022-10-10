import osmnx as ox
import networkx as nx

filepath="./data/network.graphml"
# place = {"city": "San Francisco", "state": "California", "country": "USA"}
# place = {"city": "Hong Kong Island", "state": "Hong Kong", "country": "China"}
# G = ox.graph_from_place(place, network_type="drive", truncate_by_edge=True)
# fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0, edge_color="y", edge_linewidth=0.2)
# fig.savefig("San Francisco")
# ox.save_graphml(G, filepath)
G = ox.load_graphml(filepath)
G = ox.speed.add_edge_speeds(G)
# G = ox.speed.add_edge_travel_times(G)
origin = (37.7879, -122.4075) # Union Square
destination = (37.78283, -122.44064) # Kaiser Permanente Medical Center
# acquire the nearest road node to the origin ponit
origin_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
# acquire the nearest road node to the destination
destination_node = ox.distance.nearest_nodes(G, destination[1], destination[0])
# shortest path evaluated by travel time
route = ox.shortest_path(G, origin_node, destination_node, weight='travel_time')
fig, ax = ox.plot_graph_route(G, route, node_size=0)
# length of the route
edge_lengths = ox.utils_graph.get_route_edge_attributes(G, route, "length")
print('route length: ', round(sum(edge_lengths)))