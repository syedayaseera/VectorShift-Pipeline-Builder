from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import networkx as nx

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class Edge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: str
    targetHandle: str

class PipelineRequest(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: PipelineRequest):
    try:
        # Extract nodes and edges
        nodes = pipeline.nodes
        edges = pipeline.edges
        
        # Calculate counts
        num_nodes = len(nodes)
        num_edges = len(edges)
        
        # Create a directed graph to check for DAG
        G = nx.DiGraph()
        
        # Add nodes to the graph
        for node in nodes:
            G.add_node(node.id, type=node.type)
        
        # Add edges to the graph
        for edge in edges:
            G.add_edge(edge.source, edge.target)
        
        # Check if the graph is a DAG (Directed Acyclic Graph)
        is_dag = nx.is_directed_acyclic_graph(G)
        
        # Additional analysis
        has_cycles = not is_dag
        is_connected = nx.is_weakly_connected(G) if num_nodes > 0 else True
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'is_dag': is_dag,
            'has_cycles': has_cycles,
            'is_connected': is_connected,
            'node_types': list(set(node.type for node in nodes)),
            'status': 'success'
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing pipeline: {str(e)}")
