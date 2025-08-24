"""
Extended Format Support for Diagram Server
Handles multiple input formats beyond markdown
"""

import ast
import csv
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Union


class FormatConverter:
    """Universal format converter for diagram generation"""

    @staticmethod
    def detect_format(content: str, filename: str | None = None) -> str:
        """Auto-detect the format of input content"""
        if filename:
            suffix = Path(filename).suffix.lower()
            format_map = {
                '.md': 'markdown',
                '.json': 'json',
                '.yaml': 'yaml', '.yml': 'yaml',
                '.csv': 'csv',
                '.xml': 'xml',
                '.py': 'python',
                '.js': 'javascript',
                '.html': 'html',
                '.txt': 'plaintext'
            }
            if suffix in format_map:
                return format_map[suffix]

        # Content-based detection
        content = content.strip()
        if content.startswith('{') and content.endswith('}'):
            return 'json'
        elif content.startswith('#') or '##' in content:
            return 'markdown'
        elif ',' in content and '\n' in content:
            return 'csv'
        elif content.startswith('<') and content.endswith('>'):
            return 'xml'
        elif 'class ' in content or 'def ' in content:
            return 'python'
        else:
            return 'plaintext'

class PlainTextConverter:
    """Convert plain text with structure indicators to diagrams"""

    @staticmethod
    def to_mindmap(content: str) -> str:
        """Convert structured plain text to mindmap"""
        lines = content.strip().split('\n')
        mindmap_lines = ["mindmap", "  root((Main Topic))"]

        for line in lines:
            if not line.strip():
                continue

            # Count indentation level
            indent_level = len(line) - len(line.lstrip())
            text = line.strip()

            # Remove common bullet point indicators
            text = re.sub(r'^[-*+•]\s*', '', text)
            text = re.sub(r'^\d+\.\s*', '', text)

            # Calculate mindmap indentation
            mindmap_indent = '  ' * (2 + indent_level // 2)
            mindmap_lines.append(f"{mindmap_indent}{text}")

        return '\n'.join(mindmap_lines)

class JSONConverter:
    """Convert JSON structures to diagrams"""

    @staticmethod
    def to_flowchart(data: str | dict) -> str:
        """Convert JSON to flowchart diagram"""
        if isinstance(data, str):
            data = json.loads(data)

        flowchart_lines = ["flowchart TD"]
        node_counter = 0

        def process_object(obj, parent_id=None, level=0):
            nonlocal node_counter

            if isinstance(obj, dict):
                for key, value in obj.items():
                    node_counter += 1
                    current_id = f"N{node_counter}"
                    node_label = key.replace(' ', '_')

                    if isinstance(value, dict | list):
                        flowchart_lines.append(f"  {current_id}[{node_label}]")
                        if parent_id:
                            flowchart_lines.append(f"  {parent_id} --> {current_id}")
                        process_object(value, current_id, level + 1)
                    else:
                        flowchart_lines.append(f"  {current_id}[{node_label}: {str(value)[:30]}]")
                        if parent_id:
                            flowchart_lines.append(f"  {parent_id} --> {current_id}")

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    node_counter += 1
                    current_id = f"N{node_counter}"
                    if isinstance(item, dict | list):
                        flowchart_lines.append(f"  {current_id}[Item_{i+1}]")
                        if parent_id:
                            flowchart_lines.append(f"  {parent_id} --> {current_id}")
                        process_object(item, current_id, level + 1)
                    else:
                        flowchart_lines.append(f"  {current_id}[{str(item)[:30]}]")
                        if parent_id:
                            flowchart_lines.append(f"  {parent_id} --> {current_id}")

        # Start processing from root
        node_counter = 1
        root_id = "N1"
        flowchart_lines.append(f"  {root_id}[Root]")
        process_object(data, root_id)

        return '\n'.join(flowchart_lines)

class CSVConverter:
    """Convert CSV data to various diagram types"""

    @staticmethod
    def to_organizational_chart(csv_content: str) -> str:
        """Convert CSV to organizational chart"""
        lines = csv_content.strip().split('\n')
        reader = csv.DictReader(lines)

        flowchart_lines = ["flowchart TD"]

        for i, row in enumerate(reader):
            node_id = f"N{i+1}"
            # Assume first column is name/title, second is role/department
            keys = list(row.keys())
            if len(keys) >= 2:
                name = row[keys[0]]
                role = row[keys[1]]
                flowchart_lines.append(f"  {node_id}[{name}<br/>{role}]")
            else:
                flowchart_lines.append(f"  {node_id}[{list(row.values())[0]}]")

        return '\n'.join(flowchart_lines)

    @staticmethod
    def to_relationship_diagram(csv_content: str) -> str:
        """Convert CSV with relationships to network diagram"""
        lines = csv_content.strip().split('\n')
        reader = csv.DictReader(lines)

        flowchart_lines = ["flowchart TD"]

        for row in reader:
            keys = list(row.keys())
            if len(keys) >= 2:
                source = row[keys[0]].replace(' ', '_')
                target = row[keys[1]].replace(' ', '_')
                relationship = row[keys[2]] if len(keys) > 2 else "connects to"

                flowchart_lines.append(f"  {source} -->|{relationship}| {target}")

        return '\n'.join(flowchart_lines)

class PythonCodeConverter:
    """Convert Python code to diagrams"""

    @staticmethod
    def to_class_diagram(code_content: str) -> str:
        """Convert Python code to class diagram"""
        try:
            tree = ast.parse(code_content)
        except Exception as e:
            return f"classDiagram\n  class ParseError {{\n    +error: {str(e)}\n  }}"

        class_lines = ["classDiagram"]

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                class_lines.append(f"  class {class_name} {{")

                # Extract methods and attributes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name
                        args = [arg.arg for arg in item.args.args[1:]]  # Skip 'self'
                        args_str = ", ".join(args)
                        class_lines.append(f"    +{method_name}({args_str})")
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_lines.append(f"    +{target.id}")

                class_lines.append("  }")
                class_lines.append("")

        return '\n'.join(class_lines)

class UniversalDiagramConverter:
    """Main converter that handles multiple formats"""

    def __init__(self):
        self.converters = {
            'plaintext': PlainTextConverter(),
            'json': JSONConverter(),
            'csv': CSVConverter(),
            'python': PythonCodeConverter()
        }
        self.format_detector = FormatConverter()

    def convert_to_diagram(self, content: str, filename: str | None = None,
                          target_type: str = 'auto', source_format: str = 'auto') -> tuple[str, str]:
        """
        Convert any supported format to a diagram

        Args:
            content: The input content
            filename: Optional filename for format detection
            target_type: Target diagram type (mindmap, flowchart, class, etc.)
            source_format: Source format (auto-detect if 'auto')

        Returns:
            tuple of (diagram_content, detected_format)
        """

        # Detect format if not specified
        if source_format == 'auto':
            source_format = self.format_detector.detect_format(content, filename)

        # Choose conversion method based on source format and target type
        if source_format == 'plaintext':
            if target_type in ['auto', 'mindmap']:
                return self.converters['plaintext'].to_mindmap(content), source_format

        elif source_format == 'json':
            if target_type in ['auto', 'flowchart']:
                return self.converters['json'].to_flowchart(content), source_format

        elif source_format == 'csv':
            if target_type == 'organizational':
                return self.converters['csv'].to_organizational_chart(content), source_format
            elif target_type in ['auto', 'relationship', 'network']:
                return self.converters['csv'].to_relationship_diagram(content), source_format

        elif source_format == 'python':
            if target_type in ['auto', 'class']:
                return self.converters['python'].to_class_diagram(content), source_format

        # Fallback to markdown-style processing
        return self._markdown_fallback(content), source_format

    def _markdown_fallback(self, content: str) -> str:
        """Fallback conversion treating content as markdown-style"""
        lines = content.strip().split('\n')
        mindmap_lines = ["mindmap", "  root((Document))"]

        for line in lines:
            if line.strip():
                if line.startswith('#'):
                    level = len(line.split()[0])
                    text = line.replace('#', '').strip()
                    indent = '  ' * (level + 1)
                    mindmap_lines.append(f"{indent}{text}")
                elif line.startswith(('- ', '* ', '+ ')):
                    text = line.replace('- ', '').replace('* ', '').replace('+ ', '').strip()
                    mindmap_lines.append(f"    {text}")

        return '\n'.join(mindmap_lines)

# Example usage and testing functions
def create_sample_files():
    """Create sample files for testing different formats"""

    # Sample JSON
    sample_json = {
        "system": "Meta-Matrix Architecture",
        "components": {
            "matrices": {
                "V1_Matrix": "Edge Detection",
                "V4_Matrix": "Color and Form",
                "Hippocampus": "Memory Formation"
            },
            "learning_rules": {
                "predictive_alignment": "Local Stability",
                "global_coherence": "Inter-Matrix Learning"
            }
        },
        "advantages": ["Robustness", "Flexibility", "Emergent Generalization"]
    }

    # Sample CSV
    sample_csv = """Name,Role,Department,Reports_To
Alice Johnson,Director,Engineering,CEO
Bob Smith,Senior Engineer,Engineering,Alice Johnson
Carol Davis,Product Manager,Product,CEO
David Wilson,Engineer,Engineering,Alice Johnson"""

    # Sample Python Code
    sample_python = '''
class MetaMatrix:
    def __init__(self, num_matrices=5):
        self.matrices = []
        self.connectome = {}
        self.learning_rate = 0.01

    def add_matrix(self, matrix_type, input_dim, output_dim):
        matrix = Matrix(matrix_type, input_dim, output_dim)
        self.matrices.append(matrix)
        return matrix

    def predictive_alignment(self, matrix):
        """Local learning rule for stability"""
        pass

    def global_coherence(self):
        """Inter-matrix learning"""
        pass

class Matrix:
    def __init__(self, matrix_type, input_dim, output_dim):
        self.type = matrix_type
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.weights = []

    def forward(self, input_data):
        pass

    def backward(self, error):
        pass
'''

    return {
        'json': json.dumps(sample_json, indent=2),
        'csv': sample_csv,
        'python': sample_python
    }

if __name__ == "__main__":
    # Test the converter
    converter = UniversalDiagramConverter()
    samples = create_sample_files()

    print("=== JSON to Flowchart ===")
    diagram, fmt = converter.convert_to_diagram(samples['json'], target_type='flowchart')
    print(diagram)

    print("\n=== CSV to Organization Chart ===")
    diagram, fmt = converter.convert_to_diagram(samples['csv'], target_type='organizational')
    print(diagram)

    print("\n=== Python to Class Diagram ===")
    diagram, fmt = converter.convert_to_diagram(samples['python'], target_type='class')
    print(diagram)
