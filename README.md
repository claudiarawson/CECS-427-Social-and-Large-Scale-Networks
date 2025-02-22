# Graph Analysis and Visualization

This Python script provides functionalities for **graph analysis** and **visualization** using a GML graph file.

## Features:
- **Graph Partitioning**: Split graph into connected components.
- **Homophily Verification**: Check if similar nodes are connected.
- **Balance Verification**: Check if the graph is structurally balanced.
- **Visualization**: Supports various plot types:
  - **Neighborhood Overlap**
  - **Clustering Coefficients & Degree-Based Coloring**
  - **Attribute-Based Coloring**

## Requirements:
- Python 3.x
- Install dependencies:
  ```bash
  pip install networkx matplotlib
  ```

## Arguments
 - graph_file (required): Path to the input GML graph file.
 - --components: Number of components to partition into.
 - --plot: Type of plot: "C", "N", or "P".
 - --verify_homophily: Check for homophily.
 - --verify_balanced_graph: Check if the graph is balanced.
 - --output: Save the graph after modification.

For Example:
```bash
python graph_analysis.py graph_file.gml --plot N --verify_homophily
```

## Functions
parser_arguments(): Parse command-line arguments.\
read_graph(): Read the graph from a GML file.\
partition_graph(): Partition graph into components.\
plot_graph(): Plot the graph based on the plot type.\
on_click(): Handle node click for BFS tree generation.\
verify_homophily(): Verify homophily in the graph.\
verify_balanced_graph(): Verify structural balance of the graph.
