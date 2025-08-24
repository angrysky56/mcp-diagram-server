#!/usr/bin/env python
"""
Test script for MCP Diagram Server
Run this to verify the server is working correctly
"""

import asyncio
import json
from main import (
    create_diagram,
    markdown_to_mindmap,
    list_diagrams,
    get_diagram,
    analyze_diagram,
    save_diagram,
    diagram_storage,
    cleanup_processes
)

# Mock context for testing
class MockContext:
    def info(self, message):
        print(f"INFO: {message}")
    
    async def sample(self, prompt):
        return f"AI Analysis: This is a mock response for testing. In production, this would use actual AI sampling.\nPrompt was: {prompt[:100]}..."

async def test_server():
    """Test basic server functionality"""
    print("🧪 Testing MCP Diagram Server\n")
    
    ctx = MockContext()
    
    # Test 1: Create a flowchart
    print("1️⃣ Creating flowchart...")
    result = await create_diagram(
        ctx=ctx,
        diagram_type="flowchart",
        use_template=True,
        name="test_flow"
    )
    print(f"✅ {result}\n")
    
    # Test 2: Convert markdown to mindmap
    print("2️⃣ Converting markdown to mindmap...")
    markdown = """# Project Planning
## Phase 1
- Requirements gathering
- Stakeholder interviews
## Phase 2
- Design
- Development
## Phase 3
- Testing
- Deployment"""
    
    result = await markdown_to_mindmap(
        ctx=ctx,
        markdown_text=markdown,
        name="project_mindmap"
    )
    print(f"✅ {result}\n")
    
    # Test 3: List diagrams
    print("3️⃣ Listing all diagrams...")
    result = await list_diagrams(ctx)
    print(f"✅ {result}\n")
    
    # Test 4: Get specific diagram
    print("4️⃣ Getting specific diagram...")
    diagram_ids = list(diagram_storage.keys())
    if diagram_ids:
        result = await get_diagram(ctx, diagram_ids[0])
        print(f"✅ {result}\n")
    
    # Test 5: Analyze diagram (mock)
    print("5️⃣ Analyzing diagram...")
    if diagram_ids:
        result = await analyze_diagram(ctx, diagram_ids[0])
        print(f"✅ {result}\n")
    
    # Test 6: Save diagram
    print("6️⃣ Saving diagram to file...")
    if diagram_ids:
        result = await save_diagram(ctx, diagram_ids[0])
        print(f"✅ {result}\n")
    
    print("✨ All tests completed successfully!")
    print(f"📊 Total diagrams created: {len(diagram_storage)}")
    
    # Cleanup
    cleanup_processes()

if __name__ == "__main__":
    print("=" * 50)
    print("MCP DIAGRAM SERVER TEST SUITE")
    print("=" * 50)
    print()
    
    try:
        asyncio.run(test_server())
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup_processes()
