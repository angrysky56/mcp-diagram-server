"""
MCP Diagram Server - Create and manipulate Mermaid diagrams with AUTO-SAVE
"""

import asyncio
import atexit
import json
import logging
import os
import signal
import sys
from datetime import datetime
from pathlib import Path

import aiofiles
from mcp.server.fastmcp import Context, FastMCP

# Import format conversion capabilities
from format_extensions import UniversalDiagramConverter

# Configure logging to stderr for MCP servers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Diagram Server")

# Global storage for diagrams
diagram_storage: dict[str, dict] = {}
background_tasks = set()

# Directory for diagram storage
DIAGRAMS_DIR = Path("diagrams")

# Initialize format converter
format_converter = UniversalDiagramConverter()

# Default diagram templates
DIAGRAM_TEMPLATES = {
    "flowchart": """flowchart TD
    Start[Start] --> A[Process A]
    A --> B{Decision?}
    B -->|Yes| C[Action C]
    B -->|No| D[Action D]
    C --> End[End]
    D --> End""",

    "sequence": """sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob!
    B->>A: Hi Alice!
    A->>B: How are you?
    B->>A: Great, thanks!""",

    "gantt": """gantt
    title Project Schedule
    dateFormat YYYY-MM-DD
    section Design
    Design Phase :a1, 2024-01-01, 30d
    section Development
    Development :after a1, 60d""",

    "class": """classDiagram
    class Animal {
        +String name
        +int age
        +eat()
        +sleep()
    }
    class Dog {
        +String breed
        +bark()
    }
    Animal <|-- Dog""",

    "er": """erDiagram
    CUSTOMER {
        int customer_id PK
        string name
        string email
    }
    ORDER {
        int order_id PK
        int customer_id FK
        date order_date
        decimal total
    }
    CUSTOMER ||--o{ ORDER : places""",

    "git": """gitgraph
    commit
    branch develop
    commit
    commit
    checkout main
    commit
    merge develop
    commit""",

    "pie": """pie title Project Time Distribution
    "Development" : 45
    "Testing" : 20
    "Documentation" : 15
    "Meetings" : 20""",

    "journey": """journey
    title User Journey
    section Discovery
        Visit website: 5: User
        Browse products: 4: User
    section Purchase
        Add to cart: 3: User
        Checkout: 2: User
        Payment: 1: User, System
    section Post-purchase
        Confirmation: 5: User, System"""
}
# Cleanup functions for background task management
def cleanup_tasks():
    """Clean up background tasks"""
    logger.info("Starting cleanup of background tasks")

    # Cancel background tasks
    for task in background_tasks:
        if not task.done():
            task.cancel()

    background_tasks.clear()
    logger.info("Cleanup completed")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully")
    cleanup_tasks()
    sys.exit(0)

# Register cleanup handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup_tasks)

# Helper function to track background tasks
def track_background_task(task: asyncio.Task):
    """Track background tasks for cleanup"""
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

# DIAGRAM DISCOVERY AND LOADING FUNCTIONS
async def discover_existing_diagrams() -> dict[str, dict]:
    """
    Discover existing diagrams from the diagrams directory.
    Returns a dict of diagram_id -> diagram_info for diagrams found on disk.
    """
    existing_diagrams = {}

    if not DIAGRAMS_DIR.exists():
        logger.info("Diagrams directory doesn't exist yet")
        return existing_diagrams

    try:
        # Find all .mmd files
        mmd_files = list(DIAGRAMS_DIR.glob("*.mmd"))

        for mmd_file in mmd_files:
            diagram_id = mmd_file.stem
            metadata_file = DIAGRAMS_DIR / f"{diagram_id}_metadata.json"

            # Read diagram content
            async with aiofiles.open(mmd_file) as f:
                content = await f.read()

            # Try to read metadata
            metadata = {
                "type": "unknown",
                "name": diagram_id,
                "created": datetime.fromtimestamp(mmd_file.stat().st_mtime).isoformat(),
                "modified": datetime.fromtimestamp(mmd_file.stat().st_mtime).isoformat()
            }

            if metadata_file.exists():
                try:
                    async with aiofiles.open(metadata_file) as f:
                        saved_metadata = json.loads(await f.read())
                        metadata.update(saved_metadata)
                except Exception as e:
                    logger.warning(f"Failed to read metadata for {diagram_id}: {e}")

            existing_diagrams[diagram_id] = {
                **metadata,
                "content": content,
                "source": "disk",
                "file_path": str(mmd_file),
                "metadata_path": str(metadata_file) if metadata_file.exists() else None
            }

        logger.info(f"Discovered {len(existing_diagrams)} existing diagrams")
        return existing_diagrams

    except Exception as e:
        logger.error(f"Failed to discover existing diagrams: {e}")
        return {}

async def load_diagram_from_disk(diagram_id: str) -> dict | None:
    """
    Load a specific diagram from disk into memory.
    """
    try:
        mmd_file = DIAGRAMS_DIR / f"{diagram_id}.mmd"
        metadata_file = DIAGRAMS_DIR / f"{diagram_id}_metadata.json"

        if not mmd_file.exists():
            return None

        # Read content
        async with aiofiles.open(mmd_file) as f:
            content = await f.read()

        # Read metadata if available
        metadata = {
            "type": "unknown",
            "name": diagram_id,
            "created": datetime.fromtimestamp(mmd_file.stat().st_mtime).isoformat(),
            "modified": datetime.fromtimestamp(mmd_file.stat().st_mtime).isoformat()
        }

        if metadata_file.exists():
            try:
                async with aiofiles.open(metadata_file) as f:
                    saved_metadata = json.loads(await f.read())
                    metadata.update(saved_metadata)
            except Exception as e:
                logger.warning(f"Failed to read metadata for {diagram_id}: {e}")

        return {
            **metadata,
            "content": content,
            "source": "disk"
        }

    except Exception as e:
        logger.error(f"Failed to load diagram {diagram_id} from disk: {e}")
        return None

async def initialize_diagram_storage():
    """
    Initialize diagram storage by loading existing diagrams from disk.
    This should be called when the server starts.
    """
    logger.info("Initializing diagram storage...")

    # Ensure diagrams directory exists
    DIAGRAMS_DIR.mkdir(exist_ok=True)

    # Discover existing diagrams (but don't load content into memory yet to save RAM)
    existing = await discover_existing_diagrams()

    logger.info(f"Found {len(existing)} existing diagrams on disk")
    for diagram_id in existing:
        logger.info(f"  - {diagram_id} ({existing[diagram_id]['type']})")

# AUTO-SAVE HELPER FUNCTION
async def auto_save_diagram(diagram_id: str) -> str:
    """
    Automatically save a diagram to disk when created or modified.
    This prevents data loss from session timeouts or forgetting to save.
    """
    try:
        if diagram_id not in diagram_storage:
            return f"Diagram '{diagram_id}' not found in storage"

        diagram = diagram_storage[diagram_id]

        # Ensure diagrams directory exists
        DIAGRAMS_DIR.mkdir(exist_ok=True)

        # Create filepath
        filepath = DIAGRAMS_DIR / f"{diagram_id}.mmd"
        metadata_path = DIAGRAMS_DIR / f"{diagram_id}_metadata.json"

        # Save diagram content
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(diagram['content'])

        # Save metadata
        metadata = {
            "type": diagram["type"],
            "name": diagram["name"],
            "created": diagram["created"],
            "modified": diagram["modified"]
        }
        if "source_markdown" in diagram:
            metadata["source_markdown"] = diagram["source_markdown"]

        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata, indent=2))

        logger.info(f"AUTO-SAVED: {diagram_id} to {filepath}")
        return f"Auto-saved to {filepath} and {metadata_path}"

    except Exception as e:
        logger.error(f"Failed to auto-save diagram: {e}")
        return f"Auto-save failed: {e}"

# MCP Tools with AUTO-SAVE

@mcp.tool()
async def create_diagram(
    ctx: Context,
    diagram_type: str,
    content: str | None = None,
    name: str | None = None,
    use_template: bool = False
) -> str:
    """
    Create a new Mermaid diagram with AUTOMATIC SAVING.

    **KEY IMPROVEMENT**: Diagrams are now automatically saved to disk when created,
    preventing data loss from session timeouts or forgetting to save manually.

    Args:
        diagram_type: Type of diagram (flowchart, sequence, gantt, class, er, git,
                      pie, journey, mindmap, etc.)
        content: Mermaid syntax content. If not provided, uses template or default
        name: Optional name for the diagram
        use_template: Whether to use a template (default: False)

    Returns:
        Diagram ID, content, and auto-save status
    """
    try:
        diagram_id = f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if name:
            diagram_id = f"{name}_{diagram_id}"

        if use_template and diagram_type in DIAGRAM_TEMPLATES:
            content = DIAGRAM_TEMPLATES[diagram_type]
        elif not content:
            # Provide basic templates for common types
            if diagram_type == "mindmap":
                content = """mindmap
  root((Main Topic))
    Branch 1
      Sub-item 1
      Sub-item 2
    Branch 2
      Sub-item 3"""
            elif diagram_type == "timeline":
                content = """timeline
    title Project Timeline
    2024-01 : Project Start
    2024-02 : Planning Phase
    2024-03 : Development
    2024-04 : Testing
    2024-05 : Launch"""
            else:
                content = "graph TD\n    A[Start] --> B[End]"

        # Store in memory
        diagram_storage[diagram_id] = {
            "type": diagram_type,
            "content": content,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "name": name or diagram_id
        }

        # AUTO-SAVE: Automatically save to disk
        save_result = await auto_save_diagram(diagram_id)

        logger.info(f"Created and auto-saved diagram: {diagram_id}")
        return (
            f"Created diagram '{diagram_id}' of type '{diagram_type}'\n"
            f"🔄 AUTO-SAVE: {save_result}\n\n"
            f"Content:\n{content}"
        )

    except Exception as e:
        logger.error(f"Failed to create diagram: {e}")
        raise

@mcp.tool()
async def markdown_to_mindmap(
    ctx: Context,
    markdown_text: str,
    name: str | None = None
) -> str:
    """
    Convert markdown text to a mind map diagram with AUTOMATIC SAVING.

    Args:
        markdown_text: Markdown formatted text
        name: Optional name for the mind map

    Returns:
        Generated mind map in Mermaid syntax with auto-save status
    """
    try:
        lines = markdown_text.strip().split('\n')
        mindmap_lines = ["mindmap", "  root((Main Topic))"]

        for line in lines:
            if line.strip():
                # Count heading level
                if line.startswith('#'):
                    level = len(line.split()[0])
                    text = line.replace('#', '').strip()
                    indent = '  ' * (level + 1)
                    mindmap_lines.append(f"{indent}{text}")
                elif line.startswith(('- ', '* ', '+ ')):
                    # Handle bullet points
                    text = (line.replace('- ', '')
                               .replace('* ', '')
                               .replace('+ ', '')
                               .strip())
                    indent = '    '  # Standard indentation for bullet points
                    mindmap_lines.append(f"{indent}{text}")

        mindmap_content = '\n'.join(mindmap_lines)

        # Store the mindmap
        diagram_id = f"mindmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if name:
            diagram_id = f"{name}_{diagram_id}"

        diagram_storage[diagram_id] = {
            "type": "mindmap",
            "content": mindmap_content,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "name": name or diagram_id,
            "source_markdown": markdown_text
        }

        # AUTO-SAVE: Automatically save to disk
        save_result = await auto_save_diagram(diagram_id)

        logger.info(f"Converted markdown to mindmap and auto-saved: {diagram_id}")
        return (
            f"Created mindmap '{diagram_id}'\n"
            f"🔄 AUTO-SAVE: {save_result}\n\n"
            f"Mermaid syntax:\n{mindmap_content}"
        )

    except Exception as e:
        logger.error(f"Failed to convert markdown to mindmap: {e}")
        raise

@mcp.tool()
async def update_diagram(
    ctx: Context,
    diagram_id: str,
    content: str
) -> str:
    """
    Update an existing diagram's content with AUTOMATIC SAVING.

    Args:
        diagram_id: ID of the diagram to update
        content: New Mermaid syntax content

    Returns:
        Updated diagram information with auto-save status
    """
    try:
        if diagram_id not in diagram_storage:
            return f"Diagram '{diagram_id}' not found"

        # Update the diagram
        diagram_storage[diagram_id]['content'] = content
        diagram_storage[diagram_id]['modified'] = datetime.now().isoformat()

        # AUTO-SAVE: Automatically save changes to disk
        save_result = await auto_save_diagram(diagram_id)

        logger.info(f"Updated and auto-saved diagram: {diagram_id}")
        return (
            f"Updated diagram '{diagram_id}'\n"
            f"🔄 AUTO-SAVE: {save_result}\n\n"
            f"New content:\n{content}"
        )

    except Exception as e:
        logger.error(f"Failed to update diagram: {e}")
        raise

@mcp.tool()
async def save_diagram(
    ctx: Context,
    diagram_id: str,
    filepath: str | None = None
) -> str:
    """
    Manually save a diagram to a specific file (in addition to auto-save).

    NOTE: Diagrams are now auto-saved when created/updated, but this tool
    allows saving to custom locations or re-saving existing diagrams.

    Args:
        diagram_id: ID of the diagram to save
        filepath: Optional filepath (defaults to ./diagrams/[id].mmd)

    Returns:
        Path where the diagram was saved
    """
    try:
        if diagram_id not in diagram_storage:
            return f"Diagram '{diagram_id}' not found"

        diagram = diagram_storage[diagram_id]

        if not filepath:
            DIAGRAMS_DIR.mkdir(exist_ok=True)
            filepath = str(DIAGRAMS_DIR / f"{diagram_id}.mmd")

        async with aiofiles.open(filepath, 'w') as f:
            await f.write(diagram['content'])

        # Also save metadata
        metadata_path = filepath.replace('.mmd', '_metadata.json')
        metadata = {
            "type": diagram["type"],
            "name": diagram["name"],
            "created": diagram["created"],
            "modified": diagram["modified"]
        }
        if "source_markdown" in diagram:
            metadata["source_markdown"] = diagram["source_markdown"]

        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata, indent=2))

        logger.info(f"Manually saved diagram {diagram_id} to {filepath}")
        return f"Saved diagram to {filepath} and metadata to {metadata_path}"

    except Exception as e:
        logger.error(f"Failed to save diagram: {e}")
        raise

@mcp.tool()
async def list_diagrams(ctx: Context) -> str:
    """
    List all diagrams both in memory and on disk.

    Returns:
        List of all diagrams with their metadata
    """
    try:
        result = ["📊 All Available Diagrams:\n"]
        total_count = 0

        # Get existing diagrams from disk
        existing_diagrams = await discover_existing_diagrams()

        # Show in-memory diagrams first
        if diagram_storage:
            result.append("🧠 **In Memory (Current Session):**")
            for diagram_id, diagram in diagram_storage.items():
                result.append(f"  • **{diagram['name']}** (`{diagram_id}`)")
                result.append(f"    Type: {diagram['type']}")
                result.append(f"    Created: {diagram['created']}")
                result.append(f"    Modified: {diagram['modified']}")
                if "source_file" in diagram:
                    result.append(f"    Source: {diagram['source_file']}")
                result.append("")
                total_count += 1

        # Show all diagrams saved to disk
        if existing_diagrams:
            result.append("💾 **Saved on Disk:**")
            for diagram_id, diagram in existing_diagrams.items():
                in_memory_note = " (also loaded in memory)" if diagram_id in diagram_storage else ""
                result.append(f"  • **{diagram['name']}** (`{diagram_id}`){in_memory_note}")
                result.append(f"    Type: {diagram['type']}")
                result.append(f"    Created: {diagram['created']}")
                result.append(f"    Modified: {diagram['modified']}")
                result.append(f"    File: {diagram['file_path']}")
                result.append("")
                total_count += 1

        # Check for PNG files too
        png_files = list(DIAGRAMS_DIR.glob("*.png")) if DIAGRAMS_DIR.exists() else []
        if png_files:
            result.append("🖼️  **PNG Images:**")
            for png_file in png_files:
                result.append(f"  • {png_file.name}")
            result.append("")

        if total_count == 0 and not png_files:
            return "No diagrams found in memory or on disk."

        result.insert(1, f"**Total: {total_count} diagrams** + {len(png_files)} PNG files\n")
        result.append("💡 Use `get_diagram(diagram_id)` to load any diagram into memory")

        return '\n'.join(result)

    except Exception as e:
        logger.error(f"Failed to list diagrams: {e}")
        raise

@mcp.tool()
async def get_diagram(
    ctx: Context,
    diagram_id: str
) -> str:
    """
    Get a specific diagram by ID. Loads from disk if not in memory.

    Args:
        diagram_id: ID of the diagram to retrieve

    Returns:
        Diagram content and metadata
    """
    try:
        # Check if diagram is in memory first
        if diagram_id in diagram_storage:
            diagram = diagram_storage[diagram_id]
            source = "memory"
        else:
            # Try to load from disk
            diagram = await load_diagram_from_disk(diagram_id)
            if not diagram:
                return f"Diagram '{diagram_id}' not found in memory or on disk"

            # Load it into memory for future access
            diagram_storage[diagram_id] = diagram
            source = "disk (loaded to memory)"

        result = [
            f"Diagram: {diagram_id}",
            f"Type: {diagram['type']}",
            f"Name: {diagram['name']}",
            f"Created: {diagram['created']}",
            f"Modified: {diagram['modified']}",
            f"Source: {source}",
            "",
            "Content:",
            diagram['content']
        ]

        return '\n'.join(result)

    except Exception as e:
        logger.error(f"Failed to get diagram: {e}")
        raise

@mcp.tool()
async def delete_diagram(
    ctx: Context,
    diagram_id: str
) -> str:
    """
    Delete a diagram from memory.

    Args:
        diagram_id: ID of the diagram to delete

    Returns:
        Deletion confirmation
    """
    try:
        if diagram_id not in diagram_storage:
            return f"Diagram '{diagram_id}' not found"

        deleted_diagram = diagram_storage.pop(diagram_id)
        logger.info(f"Deleted diagram: {diagram_id}")
        return (
            f"Deleted diagram '{diagram_id}' ({deleted_diagram['name']}) "
            f"of type '{deleted_diagram['type']}'"
        )

    except Exception as e:
        logger.error(f"Failed to delete diagram: {e}")
        raise

@mcp.tool()
async def list_templates(ctx: Context) -> str:
    """
    List all available diagram templates.

    Returns:
        List of available templates with descriptions
    """
    try:
        result = ["Available diagram templates:\n"]

        template_descriptions = {
            "flowchart": "Basic flowchart with decision points",
            "sequence": "Sequence diagram for interactions",
            "gantt": "Gantt chart for project scheduling",
            "class": "Class diagram for object-oriented design",
            "er": "Entity relationship diagram for databases",
            "git": "Git flow diagram for version control",
            "pie": "Pie chart for data visualization",
            "journey": "User journey mapping"
        }

        for template_name, template_content in DIAGRAM_TEMPLATES.items():
            description = template_descriptions.get(template_name, "")
            result.append(f"- **{template_name}**: {description}")

        result.append(
            "\nTo use a template, call create_diagram() with use_template=True"
        )
        return '\n'.join(result)

    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise

# FORMAT CONVERSION MCP TOOLS

@mcp.tool()
async def convert_format_to_diagram(
    ctx: Context,
    content: str,
    filename: str | None = None,
    target_type: str = 'auto',
    source_format: str = 'auto',
    name: str | None = None
) -> str:
    """
    Convert various file formats to Mermaid diagrams with AUTOMATIC SAVING.

    **Multi-Format Support**: JSON→Flowcharts, CSV→Org Charts, Python→Class Diagrams, etc.

    Args:
        content: The input content to convert
        filename: Optional filename for format detection
        target_type: Target diagram type (auto, flowchart, mindmap, class, organizational, etc.)
        source_format: Source format (auto, json, csv, python, markdown, plaintext)
        name: Optional name for the generated diagram

    Returns:
        Generated diagram with format detection info and auto-save status
    """
    try:
        # Convert using the format converter
        diagram_content, detected_format = format_converter.convert_to_diagram(
            content, filename, target_type, source_format
        )

        # Determine diagram type for storage
        if target_type == 'auto':
            if detected_format == 'json':
                diagram_type = 'flowchart'
            elif detected_format == 'csv':
                diagram_type = 'organizational'
            elif detected_format == 'python':
                diagram_type = 'class'
            else:
                diagram_type = 'mindmap'
        else:
            diagram_type = target_type

        # Generate diagram ID
        diagram_id = f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if name:
            diagram_id = f"{name}_{diagram_id}"

        # Store in memory
        diagram_storage[diagram_id] = {
            "type": diagram_type,
            "content": diagram_content,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "name": name or f"Converted {detected_format.title()}",
            "source_format": detected_format,
            "target_type": target_type,
            "source_content": content[:500] + "..." if len(content) > 500 else content  # Store truncated source
        }

        # AUTO-SAVE: Automatically save to disk
        save_result = await auto_save_diagram(diagram_id)

        logger.info(f"Converted {detected_format} to {diagram_type} and auto-saved: {diagram_id}")
        return (
            f"✅ Converted {detected_format} to {diagram_type} diagram: '{diagram_id}'\n"
            f"🔄 AUTO-SAVE: {save_result}\n\n"
            f"📊 Generated Mermaid Diagram:\n{diagram_content}"
        )

    except Exception as e:
        logger.error(f"Failed to convert format to diagram: {e}")
        raise

@mcp.tool()
async def json_to_flowchart(
    ctx: Context,
    json_content: str,
    name: str | None = None
) -> str:
    """
    Convert JSON structure to a flowchart diagram with AUTOMATIC SAVING.

    Perfect for visualizing data structures, API responses, or configuration files.

    Args:
        json_content: JSON string or content to convert
        name: Optional name for the flowchart

    Returns:
        Generated flowchart with auto-save status
    """
    try:
        return await convert_format_to_diagram(
            ctx, json_content, None, 'flowchart', 'json', name
        )
    except Exception as e:
        logger.error(f"Failed to convert JSON to flowchart: {e}")
        raise

@mcp.tool()
async def csv_to_org_chart(
    ctx: Context,
    csv_content: str,
    name: str | None = None,
    chart_type: str = 'organizational'
) -> str:
    """
    Convert CSV data to organizational or relationship chart with AUTOMATIC SAVING.

    Args:
        csv_content: CSV data (expects columns like Name, Role, Department, etc.)
        name: Optional name for the chart
        chart_type: Type of chart (organizational or relationship)

    Returns:
        Generated organizational chart with auto-save status
    """
    try:
        return await convert_format_to_diagram(
            ctx, csv_content, None, chart_type, 'csv', name
        )
    except Exception as e:
        logger.error(f"Failed to convert CSV to org chart: {e}")
        raise

@mcp.tool()
async def python_to_class_diagram(
    ctx: Context,
    python_code: str,
    name: str | None = None
) -> str:
    """
    Convert Python source code to class diagram with AUTOMATIC SAVING.

    Automatically parses classes, methods, and relationships from Python code.

    Args:
        python_code: Python source code to analyze
        name: Optional name for the class diagram

    Returns:
        Generated class diagram with auto-save status
    """
    try:
        return await convert_format_to_diagram(
            ctx, python_code, None, 'class', 'python', name
        )
    except Exception as e:
        logger.error(f"Failed to convert Python to class diagram: {e}")
        raise

@mcp.tool()
async def detect_file_format(
    ctx: Context,
    content: str,
    filename: str | None = None
) -> str:
    """
    Detect the format of input content.

    Args:
        content: Content to analyze
        filename: Optional filename for additional context

    Returns:
        Detected format and analysis info
    """
    try:
        detected_format = format_converter.format_detector.detect_format(content, filename)

        analysis = [
            "🔍 **Format Detection Results**",
            f"Detected Format: **{detected_format}**",
            f"Content Length: {len(content)} characters"
        ]

        if filename:
            analysis.append(f"Filename: {filename}")
            analysis.append(f"File Extension: {Path(filename).suffix}")

        # Add format-specific info
        if detected_format == 'json':
            try:
                import json
                parsed = json.loads(content)
                analysis.append(f"JSON Keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'Array'}")
            except Exception:
                analysis.append("JSON: Invalid or partial JSON detected")

        elif detected_format == 'csv':
            lines = content.strip().split('\n')
            analysis.append(f"CSV Rows: ~{len(lines)}")
            if lines:
                analysis.append(f"Columns: {lines[0].count(',') + 1}")

        elif detected_format == 'python':
            analysis.append("Python: Code analysis available for class diagram conversion")

        # Add recommended conversions
        recommendations = {
            'json': 'json_to_flowchart for structure visualization',
            'csv': 'csv_to_org_chart for organizational/relationship charts',
            'python': 'python_to_class_diagram for code architecture',
            'markdown': 'markdown_to_mindmap for concept mapping',
            'plaintext': 'convert_format_to_diagram with target_type="mindmap"'
        }

        if detected_format in recommendations:
            analysis.append(f"💡 Recommended: {recommendations[detected_format]}")

        return '\n'.join(analysis)

    except Exception as e:
        logger.error(f"Failed to detect file format: {e}")
        raise

# Initialization function to run at server startup
def init_server():
    """Initialize the server by discovering existing diagrams"""
    try:
        logger.info("Starting MCP Diagram Server with AUTO-SAVE functionality")
        logger.info("🔄 All diagrams will now be automatically saved when created or modified")
        logger.info(f"📁 Diagrams saved to: {DIAGRAMS_DIR.absolute()}")

        # Run initialization in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(initialize_diagram_storage())
        loop.close()

    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")

# Main execution
if __name__ == "__main__":
    try:
        init_server()
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        cleanup_tasks()
@mcp.tool()
async def load_diagram(
    ctx: Context,
    filepath: str
) -> str:
    """
    Load a diagram from a file.

    Args:
        filepath: Path to the diagram file (.mmd)

    Returns:
        Loaded diagram content and ID
    """
    try:
        if not os.path.exists(filepath):
            return f"File '{filepath}' not found"

        async with aiofiles.open(filepath) as f:
            content = await f.read()

        # Try to load metadata if it exists
        metadata_path = filepath.replace('.mmd', '_metadata.json')
        metadata = {}
        if os.path.exists(metadata_path):
            async with aiofiles.open(metadata_path) as f:
                metadata = json.loads(await f.read())

        # Generate new ID for loaded diagram
        diagram_id = f"loaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        name = Path(filepath).stem

        diagram_storage[diagram_id] = {
            "type": metadata.get("type", "flowchart"),
            "content": content,
            "created": metadata.get("created", datetime.now().isoformat()),
            "modified": datetime.now().isoformat(),
            "name": metadata.get("name", name),
            "source_file": filepath
        }

        # Preserve source_markdown if it exists
        if "source_markdown" in metadata:
            diagram_storage[diagram_id]["source_markdown"] = metadata["source_markdown"]

        logger.info(f"Loaded diagram from {filepath} as {diagram_id}")
        return f"Loaded diagram '{diagram_id}' from {filepath}\n\nContent:\n{content}"

    except Exception as e:
        logger.error(f"Failed to load diagram: {e}")
        raise

