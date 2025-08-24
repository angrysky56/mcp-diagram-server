# MCP Diagram Server 📊

A powerful Model Context Protocol (MCP) server for creating, manipulating, and analyzing Mermaid diagrams and charts. Inspired by Drawnix's capabilities, this server brings diagram creation and management directly into your AI workflows.

## 🌟 Features

- **Mermaid Diagram Creation**: Create flowcharts, sequence diagrams, Gantt charts, mind maps, and more
- **Markdown to Mind Map**: Convert markdown text into visual mind maps
- **AI-Powered Analysis**: Get intelligent insights and suggestions for your diagrams
- **Template Library**: Pre-built templates for common diagram types
- **Save/Load**: Persist diagrams to disk with metadata
- **Interactive Prompts**: Guided diagram creation workflows
- **Resource Access**: Access diagrams and templates as MCP resources

## 🚀 Quick Start

### Installation

1. Clone or download this repository:
```bash
cd /home/ty/Repositories/ai_workspace/mcp-diagram-server
```

2. Set up the Python environment:
```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
uv add -e .
```

3. Install Playwright for rendering (optional, for export features):
```bash
uv add playwright
uv run playwright install chromium
```

### Claude Desktop Configuration

1. Copy the example configuration from `example_mcp_config.json`
2. Add it to your Claude Desktop configuration file
3. Restart Claude Desktop

## 📚 Available Tools

### Diagram Creation
- `create_diagram` - Create a new Mermaid diagram with templates
- `markdown_to_mindmap` - Convert markdown to mind map
- `save_diagram` - Save diagram to file
- `load_diagram` - Load diagram from file

### Diagram Management
- `list_diagrams` - List all diagrams in memory
- `get_diagram` - Get a specific diagram
- `update_diagram` - Update diagram content
- `analyze_diagram` - AI-powered diagram analysis
- `suggest_diagram_improvements` - Get improvement suggestions

## 🎨 Supported Diagram Types

- **Flowcharts** - Process flows and decision trees
- **Sequence Diagrams** - Interaction sequences
- **Gantt Charts** - Project timelines
- **Mind Maps** - Concept organization
- **State Diagrams** - State machines
- **Entity Relationship** - Database schemas
- **User Journey** - User experience flows
- **Git Graphs** - Version control visualization

## 💡 Usage Examples

### Create a Flowchart
```
Use the create_diagram tool with type "flowchart" and provide Mermaid syntax,
or use use_template=true for a starter template.
```

### Convert Markdown to Mind Map
```
Use markdown_to_mindmap with your markdown text:
# Main Topic
## Subtopic 1
- Point A
- Point B
## Subtopic 2
- Point C
```

### Analyze and Improve Diagrams
```
1. Create or load a diagram
2. Use analyze_diagram for insights
3. Use suggest_diagram_improvements for optimization
```

## 🔧 Advanced Features

### AI Sampling Integration
The server uses Claude's sampling capability to provide intelligent analysis and suggestions for your diagrams.

### Resources
- `diagrams://list` - Access all diagrams as a resource
- `diagrams://templates` - Get available templates

### Prompts
Pre-configured prompts for common diagram creation tasks:
- Create flowchart from description
- Create sequence diagram from scenario
- Create mind map from topic
- Interactive diagram review

## 🛡️ Process Management

The server implements robust process management:
- Signal handling for graceful shutdown
- Automatic cleanup of background tasks
- Process tracking and termination
- Memory-efficient diagram storage

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 🙏 Acknowledgments

- Inspired by [Drawnix](https://drawnix.com) - Open-source whiteboard tool
- Built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
- Powered by [Mermaid](https://mermaid.js.org) diagram syntax

## 📞 Support

For issues or questions, please open an issue on GitHub or contact the maintainers.

---

**Note**: This server requires Python 3.10+ and is designed to work with Claude Desktop or other MCP-compatible clients.