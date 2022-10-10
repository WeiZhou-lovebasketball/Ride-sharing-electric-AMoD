import matsim
import networkx as nx


def create_graph(network_path):
    # -------------------------------------------------------------------
    # 1. NETWORK: Read a MATSim network:
    net = matsim.read_network(network_path)
    
    # Creat DiGraph
    G = nx.DiGraph()
    link_list = []
    nodes = net.nodes
    print(nodes)
    links = net.links
    min_x = nodes['x'].min()
    max_x = nodes['x'].max()
    min_y = nodes['y'].min()
    max_y = nodes['y'].max()
    print(max_x,min_x,max_y,min_y)
    #Add nodes
    for i in range(len(nodes)):
        G.add_node(int(nodes.loc[i,"node_id"]), x=float(nodes.loc[i,"x"]), y=float(nodes.loc[i,"y"]))
    print('Nodes added')   
    for i in range(len(links)):
        G.add_edge(int(links.loc[i,"from_node"]), int(links.loc[i,"to_node"]), edge_id=int(links.loc[i,"link_id"]) , 
                   length=float(links.loc[i,"length"]) , freespeed=float(links.loc[i,"freespeed"]) , 
                   timer = float(links.loc[i,"length"])/float(links.loc[i,"freespeed"]) ,
                   capacity=float(links.loc[i,"capacity"]))

        
    print('Links added')    
    G.graph['min_x'] = min_x
    G.graph['max_x'] = max_x
    G.graph['min_y'] = min_y
    G.graph['max_y'] = max_y
    
    return G

