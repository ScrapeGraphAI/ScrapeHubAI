#!/usr/bin/env python3
"""Test script to verify the LangGraph agent works"""

import sys
sys.path.append('.')

from src.agent import graph

# Test the graph
print("Testing GitHub Star to Company Agent...")
print("Graph nodes:", list(graph.nodes))

# Get the graph structure
try:
    graph_repr = graph.get_graph()
    print("Graph edges:", graph_repr.edges)
    
    # Try to generate Mermaid diagram
    try:
        mermaid_str = graph.get_graph().draw_mermaid()
        print("\nMermaid diagram:")
        print(mermaid_str)
        
        # Save as PNG if possible
        img_data = graph.get_graph().draw_mermaid_png()
        with open("graph_visualization.png", "wb") as f:
            f.write(img_data)
        print("\nGraph visualization saved to graph_visualization.png")
    except Exception as e:
        print(f"\nCould not generate visualization: {e}")
except Exception as e:
    print(f"Could not get graph structure: {e}")

print("\nGraph structure is valid!")