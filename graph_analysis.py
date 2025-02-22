import numpy as np
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import random

position = None
graph = None

def parser_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file", type=str, help="Input GML graph file")
    parser.add_argument("--components", type=int, help="Number of components to partition into")
    parser.add_argument("--plot", type=str, choices=["C", "N", "P"], help="Plot type")
    parser.add_argument("--verify_homophily", action="store_true", help="Verify homophily in the graph")
    parser.add_argument("--verify_balanced_graph", action="store_true", help="Verify if the graph is balanced")
    parser.add_argument("--output", type=str, help="Output GML file")
    return parser.parse_args()

def read_graph(file_path):
    try:
        return nx.read_gml(file_path)
    except Exception as e:
        print(f"Error reading graph: {e}")
        exit()
    except FileNotFoundError:
        print(f"File {e} is not found")

def partition_graph(G, n):
    if n < 1 or n > len(G.nodes):
        raise ValueError("Number of input components must be larger than or equal to 1 and smaller than or equal to the amount of nodes in G.")
    if nx.number_connected_components(G) == G:
        print(f"The graph already has {nx.number_connected_components(G)} connected components.")
    while nx.number_connected_components(G) < n:
        betweenness = nx.edge_betweenness_centrality(G)
        e_remove = max(betweenness, key=betweenness.get)
        G.remove_edge(*e_remove)
        print(f"Edge Removed: {e_remove}")
    print(f"The graph has been partitioned into {n} connected components.")
    return G

def plot_graph(G, plot_type):
    if "N" in plot_type:
        position = nx.spring_layout(G)

        overlap = {
            (u, v): len(set(G.neighbors(u)) & set(G.neighbors(v))) / 
                 len(set(G.neighbors(u)) | set(G.neighbors(v))) 
                 if len(set(G.neighbors(u)) | set(G.neighbors(v))) > 0 else 0
            for u, v in G.edges()
        }
        
        min_overlap, max_overlap = min(overlap.values(), default=0), max(overlap.values(), default=1)
        edge_widths = [
            2 + 8 * (overlap[e] - min_overlap) / (max_overlap - min_overlap) if max_overlap > min_overlap else 2
            for e in G.edges()
        ]

        min_o, max_o = min(overlap.values(), default=0), max(overlap.values(), default=1)
        edge_widths = [2 + 8 * (overlap[e] - min_o) / (max_o - min_o) if max_o > min_o else 2 for e in G.edges()]

        fig, ax = plt.subplots(figsize=(10, 8))
        nx.draw(G, position, ax=ax, node_size=200, edge_color="gray", width=edge_widths, with_labels=True, picker=True)
        
        fig.canvas.mpl_connect("pick_event", on_click)
        plt.title("Neighborhood Overlap Graph")
        plt.show()

    if "C" in plot_type:
        position = nx.spring_layout(G)
        cluster_values = nx.clustering(G)
        min_c, max_c = min(cluster_values.values()), max(cluster_values.values())

        min_s, max_s = 100, 1000
        scale_factor = max_s - min_s if max_c > min_c else 0
        node_sizes = [min_s + ((cluster_values[n] - min_c) / (max_c - min_c) * scale_factor) 
                    if max_c > min_c else min_s for n in G.nodes()]

        degs = {node: val for node, val in G.degree()}
        peak_degree = max(degs.values(), default=1)
        node_shades = [(degs[n] / peak_degree, 0, 1) for n in G.nodes()]

        fig, ax = plt.subplots(figsize=(10, 8))
        nx.draw(G, position, ax=ax, node_size=node_sizes, node_color=node_shades, with_labels=True)
        
        plt.title("Clustering Coefficients & Degree-Based Coloring Graph")
        plt.show()

    if "P" in plot_type:
        default_color = (0.5, 0.5, 0.5)

        def get_node_color(node):
            return getattr(G.nodes[node], "color", default_color)

        node_colors = [get_node_color(node) if get_node_color(node) != default_color else (random.random(), random.random(), random.random()) for node in G.nodes()]

        layout = nx.spring_layout(G)

        plt.figure(figsize=(10, 8))
        nx.draw(G, layout, node_color=node_colors, with_labels=True)

        plt.title("Node colored by attributes graph")
        plt.show()

def on_click(event):
    index = event.ind 
    if index:
        chosen_node = list(graph.nodes())[index[0]] 
        print(f"You chose the node: {chosen_node}")

        plt.close()
        bfs = nx.bfs_tree(graph, chosen_node)
        position = nx.spring_layout(bfs, chosen_node)
        
        plt.figure(figsize=(10, 8))
        nx.draw(bfs, position, with_labels=True, node_size=200)
        plt.title(f"BFS Tree starting from the chosen node {chosen_node}")
        plt.show()

def verify_homophily(G):
    association = nx.get_node_attributes(G, "club") or nx.get_node_attributes(G, "color")
    
    if not association:
        print("Error: Neither 'club' nor 'color' attributes found in graph nodes.")
        return

    sameness = sum(1 for u, v in G.edges if association[u] == association[v])
    total_edges = G.number_of_edges()

    homophily_index = sameness / total_edges if total_edges > 0 else 0
    print(f"Homophily: {homophily_index: .2f}")

    if homophily_index > 0.5:
        print("Graph has strong homophily")
        return "Yes"
    elif homophily_index == 0.5:
        print("Homophily is neutral")
        return "Neutral"
    else:
        print("Homophily is weak")
        return "None"

# Complete
def verify_balanced_graph(G):
    cycles = list(nx.cycle_basis(G))
    if not cycles:
        print("No cycles found in the graph")
        return
    balanced = True
    for cycle in cycles:
        edge_sign_product = 1
        for i in range(len(cycle)):
            node1 = cycle[i]
            node2 = cycle[(i + 1) % len(cycle)]
            if G.has_edge(node1, node2):
                sign = G[node1][node2].get("sign", "+")
                if sign == "+":
                    sign = 1
                elif sign == "-":
                    sign = -1
                else:
                    print(f"Unexpected sign value: {sign} between nodes {node1} and {node2}")
                    continue
                edge_sign_product *= sign
        if edge_sign_product < 0:
            balanced = False
    if balanced:
        print("This is a balanced graph.")
    else:
        print("This is an imbalanced graph.")
    return balanced

def main():
    args = parser_arguments()

    graph = read_graph(args.graph_file)

    if args.components:
        graph = partition_graph(graph, args.components)

    if args.plot:
        plot_graph(graph, args.plot)

    if args.verify_homophily:
        verify_homophily(graph)

    if args.verify_balanced_graph:
        verify_balanced_graph(graph)

    if args.output:
        nx.write_graph(graph, args.output)
        print(f"Graph saved to {args.output}")

if __name__ == "__main__":
    main()