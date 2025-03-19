import streamlit as st
import pandas as pd
import numpy as np
from pyvis.network import Network
import tempfile
import os
from app.core.models import Plan, PlanNode


class PlanVisualizer:
    def __init__(self):
        self.network = Network(
            height="700px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#2c3e50",
            directed=True,
        )
        # Hierarchical layout settings
        self.network.set_options(
            """
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "UD",
              "sortMethod": "directed",
              "nodeSpacing": 150,
              "levelSeparation": 200
            }
          },
          "nodes": {
            "font": {
              "size": 16,
              "face": "Helvetica"
            },
            "borderWidth": 2,
            "shadow": {
              "enabled": true,
              "size": 5,
              "x": 2,
              "y": 2
            }
          },
          "edges": {
            "color": {
              "color": "#95a5a6",
              "opacity": 0.8
            },
            "smooth": {
              "type": "straightCross"
            },
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.8
              }
            }
          },
          "physics": {
            "enabled": false
          }
        }
        """
        )

    def _get_node_properties(self, node: PlanNode):
        """Determines node properties."""
        # Calculate node size based on weight
        size = 30 + node.weight * 0.2

        if node.weight >= 70:
            color = "#e74c3c"
            border_color = "#c0392b"
            hover_color = "#ff6b6b"
        else:
            color = "#34495e"
            border_color = "#2c3e50"
            hover_color = "#465c71"

        details = (
            f"Task Description:\n"
            f"{node.description}\n\n"
            f"Complexity: {node.weight:.0f}%"
        )

        return {
            "size": size,
            "color": color,
            "border_color": border_color,
            "hover_color": hover_color,
            "title": details,
        }

    def _add_node_to_network(self, node: PlanNode, parent_id=None, step_prefix=""):
        props = self._get_node_properties(node)

        # Generate step number
        current_step = (
            f"{step_prefix}{node.id.split('_')[-1]}" if node.id != "root" else "Root"
        )

        # Add complexity to node label
        if node.id == "root":
            label = "Plan"
        else:
            label = f"Step {current_step}: {node.weight:.0f}%"

        # Add node
        self.network.add_node(
            node.id,
            label=label,
            title=props["title"],
            size=props["size"],
            color={
                "background": props["color"],
                "border": props["border_color"],
                "highlight": {
                    "background": props["hover_color"],
                    "border": props["border_color"],
                },
                "hover": {
                    "background": props["hover_color"],
                    "border": props["border_color"],
                },
            },
            shape="box",
            shadow=True,
            font={"face": "Helvetica", "size": 16, "color": "#ffffff"},
        )

        # Add edge if parent exists
        if parent_id:
            self.network.add_edge(
                parent_id,
                node.id,
                width=2,
                color={"color": "#95a5a6", "opacity": 0.8},
                smooth={"type": "straightCross"},
            )

        # Recursively add child nodes (add substep to step number)
        for i, child in enumerate(node.children, 1):
            new_prefix = f"{current_step}." if node.id != "root" else ""
            self._add_node_to_network(child, node.id, new_prefix)

    def visualize_plan(self, plan: Plan):
        self.network = Network(
            height="700px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#ffffff",
            directed=True,
        )

        self.network.set_options(
            """
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "UD",
              "sortMethod": "directed",
              "nodeSpacing": 150,
              "levelSeparation": 200,
              "treeSpacing": 200,
              "shakeTowards": "roots"
            }
          },
          "nodes": {
            "font": {
              "size": 16,
              "face": "Helvetica",
              "color": "#ffffff"
            },
            "borderWidth": 2,
            "shadow": {
              "enabled": true,
              "size": 5,
              "x": 2,
              "y": 2
            }
          },
          "edges": {
            "color": {
              "color": "#95a5a6",
              "opacity": 0.8
            },
            "smooth": {
              "type": "straightCross"
            },
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.8
              }
            }
          },
          "physics": {
            "enabled": false,
            "hierarchicalRepulsion": {
              "centralGravity": 0.0,
              "springLength": 100,
              "springConstant": 0.01,
              "nodeDistance": 120
            }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 300,
            "zoomView": true,
            "dragView": true
          }
        }
        """
        )

        # 루트 노드부터 시작하여 모든 노드를 추가
        self._add_node_to_network(plan.root_node)

        # Depth 레이블 추가를 위한 HTML 생성
        depth_labels = """
        <div style='position: absolute; right: 20px; top: 50%; transform: translateY(-50%);
             background: rgba(255,255,255,0.9); padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1)'>
            <h3 style='margin: 0 0 10px 0; color: #2c3e50'>Depth Levels</h3>
            <div style='color: #2c3e50'>
                <p>Root: Plan</p>
                <p>Depth 1: Main Steps</p>
                <p>Depth 2: Sub Steps</p>
            </div>
        </div>
        """

        # 임시 파일에 HTML 저장 (Depth 레이블 포함)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            self.network.save_graph(tmp_file.name)

            # HTML 파일에 Depth 레이블 추가
            with open(tmp_file.name, "r", encoding="utf-8") as f:
                content = f.read()

            # body 태그 바로 뒤에 depth_labels 삽입
            content = content.replace("<body>", f"<body>{depth_labels}")

            with open(tmp_file.name, "w", encoding="utf-8") as f:
                f.write(content)

            return tmp_file.name
