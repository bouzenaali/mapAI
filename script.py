import streamlit as st
import os
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

@st.cache_resource
def get_map_data(xml_file_path):
    graph = ox.graph_from_xml(xml_file_path, simplify=False)
    return graph

def parse_node_names(xml_file_path):
    node_names = {}
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    for node in root.findall('node'):
        node_id = int(node.attrib['id'])
        name = None
        for tag in node.findall('tag'):
            if 'k' in tag.attrib and tag.attrib['k'] == 'name':
                name = tag.attrib['v']
                break
        if name is not None:
            node_names[name] = node_id  # Store node name as key and node ID as value
        else:
             node_names[f"Unnamed Node {node_id}"] = node_id

    return node_names

def a_star_search(graph, source, target):
    try:
        shortest_path = nx.astar_path(graph, source, target)
        return shortest_path
    except nx.NodeNotFound:
        return None

def plot_shortest_path(graph, shortest_path):
    fig, ax = ox.plot_graph_route(graph, shortest_path, route_color='r', node_size=0, edge_linewidth=2, show=False, close=False)
    plt.title("Shortest Path")
    st.pyplot(fig)

# Initialize Streamlit
st.title("Shortest Path Finder")

# XML file selection
xml_file = st.file_uploader("Upload XML File", type=["xml"])

if xml_file is not None:
    # Save uploaded file to a temporary location
    with open("temp.xml", "wb") as f:
        f.write(xml_file.read())

    # Load XML file and extract node names
    node_names = parse_node_names("temp.xml")

    # Load XML file and create the graph
    graph = get_map_data("temp.xml")
    
    # Source and target selection
    st.subheader("Select Source and Destination Places:")
    selected_source_name = st.selectbox("Source Place:", list(node_names.keys()), key="selected_source")
    selected_target_name = st.selectbox("Destination Place:", list(node_names.keys()), key="selected_target")
    
    # Find shortest path button
    if st.button("Find Shortest Path"):
        source_node = node_names.get(selected_source_name)
        target_node = node_names.get(selected_target_name)
        if source_node is not None and target_node is not None:
            shortest_path = a_star_search(graph, source_node, target_node)
            print(source_node, target_node)
            if shortest_path is not None:
                plot_shortest_path(graph, shortest_path)
            else:
                st.error("Could not find a path between the selected source and target.")
        else:
            st.error("One or both of the selected source and target places do not exist in the map data.")

    # Remove temporary file after processing
    os.remove("temp.xml")
