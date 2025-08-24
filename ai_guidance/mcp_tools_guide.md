# MCP Diagram Server - AI Tools Usage Guide

## Overview
This MCP server provides powerful tools for creating, manipulating, and analyzing Mermaid diagrams. Use these tools to help users visualize processes, data structures, user journeys, and more.

## Core Tools

### 1. create_diagram
**Purpose**: Create new Mermaid diagrams from scratch or using templates

**Parameters**:
- `diagram_type`: flowchart, sequence, gantt, class, er, git, pie, journey, mindmap, timeline
- `content`: Optional Mermaid syntax (if not provided, uses template or generates default)
- `name`: Optional human-readable name for the diagram
- `use_template`: Boolean to use predefined templates

**Best Practices**:
- Always ask the user what type of diagram they want to create
- For complex processes, suggest flowcharts or sequence diagrams
- For project planning, recommend gantt charts
- For brainstorming or knowledge mapping, suggest mindmaps
- When users are unsure, offer to show available templates

**Example Usage**:
```
User: "I need to visualize a user login process"
Response: I'll create a flowchart diagram for the user login process.
Tool Call: create_diagram(diagram_type="flowchart", name="user_login", use_template=False, content="flowchart TD...")
```

### 2. markdown_to_mindmap
**Purpose**: Convert structured markdown text into visual mind maps

**Parameters**:
- `markdown_text`: Markdown formatted text with headings and bullet points
- `name`: Optional name for the resulting mindmap

**Best Practices**:
- Perfect for converting meeting notes, outlines, or structured documents
- Works well with hierarchical information
- Suggest this when users have existing markdown content they want to visualize

### 3. analyze_diagram
**Purpose**: Get AI-powered insights and analysis of existing diagrams

**Parameters**:
- `diagram_id`: ID of the diagram to analyze

**Best Practices**:
- Use this to help users understand complex diagrams
- Provide insights about structure, flow, and potential issues
- Suggest improvements or optimizations
- Help identify missing connections or unclear relationships

### 4. suggest_diagram_improvements
**Purpose**: Get specific improvement suggestions for diagrams

**Parameters**:
- `diagram_id`: ID of the diagram to improve  
- `improvement_type`: general, clarity, performance, visual, structure

**Best Practices**:
- Use after analyzing a diagram to provide actionable improvements
- Focus on the specific type of improvement the user needs
- Provide updated Mermaid code along with explanations

## Workflow Patterns

### Pattern 1: From Scratch Creation
1. Ask user about their visualization needs
2. Suggest appropriate diagram type
3. Create initial diagram using `create_diagram`
4. Analyze with `analyze_diagram` if needed
5. Refine with `suggest_diagram_improvements`

### Pattern 2: Document Conversion
1. Identify structured content (markdown, outlines)
2. Use `markdown_to_mindmap` for hierarchical content
3. Save the result with `save_diagram`
4. Offer analysis and improvements

### Pattern 3: Diagram Review & Enhancement
1. Load existing diagram with `load_diagram`
2. Analyze current state with `analyze_diagram`
3. Get specific improvements with `suggest_diagram_improvements`
4. Update diagram with `update_diagram`

## Diagram Types Guide

### Flowcharts
- **Use for**: Processes, decision trees, workflows
- **Key elements**: Start/End nodes, decision diamonds, process rectangles
- **Common mistakes**: Missing end nodes, unclear decision criteria

### Sequence Diagrams
- **Use for**: System interactions, API flows, communication patterns
- **Key elements**: Participants, messages, activation boxes
- **Common mistakes**: Missing return messages, unclear timing

### Mind Maps
- **Use for**: Brainstorming, knowledge organization, concept mapping
- **Key elements**: Central topic, branching structure, hierarchical relationships
- **Common mistakes**: Too many levels, unclear connections

### Gantt Charts
- **Use for**: Project timelines, task scheduling, milestone tracking
- **Key elements**: Tasks, dependencies, time ranges
- **Common mistakes**: Missing dependencies, unrealistic timelines

## Error Handling

### Common Issues:
1. **Invalid Mermaid Syntax**: Guide users to fix syntax errors
2. **Diagram Not Found**: Check diagram IDs and suggest listing available diagrams
3. **Complex Diagrams**: Break down into smaller, manageable pieces
4. **Performance Issues**: Suggest simpler alternatives for very large diagrams

### Recovery Strategies:
1. Use `list_diagrams` to show available options
2. Load templates with `list_templates` for reference
3. Start with simple examples and build complexity gradually
4. Use analysis tools to understand existing diagrams before modifications

## Advanced Usage

### Combining Tools:
- Create → Analyze → Improve → Save (complete workflow)
- Load → Update → Analyze (revision workflow)
- Template → Customize → Share (quick start workflow)

### Integration Tips:
- Save important diagrams to files for persistence
- Use meaningful names for easy identification  
- Regularly analyze complex diagrams for clarity
- Leverage AI suggestions for continuous improvement

## User Communication

### Best Responses:
- Always explain what type of diagram you're creating and why
- Describe key elements and relationships in the diagram
- Offer to make modifications or improvements
- Suggest related diagram types that might be helpful

### Avoid:
- Creating diagrams without explanation
- Using technical jargon without context
- Overwhelming users with too many options
- Ignoring user feedback on diagram effectiveness
