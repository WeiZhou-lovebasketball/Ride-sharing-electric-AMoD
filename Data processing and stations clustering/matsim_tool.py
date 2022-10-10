from Graph_from_xml import create_graph
import networkx as nx

# G = create_graph('data/network.xml.gz')
# nx.write_gexf(G, 'data/networkx')
G = nx.read_gexf('data/networkx.xml')
# print(nx.dijkstra_path(G, source='1221046512', target='1221102766', weight='timer'))
# print(nx.astar_path(G, source='7233943448', target='65343962', weight='timer'))
travel_time = nx.astar_path_length(G, source = '7233943448', target='65343962', weight='timer')
short_path = nx.astar_path(G, source = '7233943448', target='65343962', weight='timer')
distance = nx.path_weight(G, short_path, weight = 'length')
print(travel_time)
print(distance)