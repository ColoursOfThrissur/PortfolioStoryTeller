"""List all yfmcp tools and their schemas"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def list_tools():
    server_params = StdioServerParameters(
        command="uvx",
        args=["yfmcp@latest"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("✓ yfmcp session initialized\n")
            print("="*80)
            print("AVAILABLE TOOLS")
            print("="*80)
            
            tools = await session.list_tools()
            
            for tool in tools.tools:
                print(f"\n{'='*80}")
                print(f"TOOL: {tool.name}")
                print(f"{'='*80}")
                print(f"\nDescription: {tool.description}\n")
                
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    schema = tool.inputSchema
                    
                    # Print properties (arguments)
                    if 'properties' in schema:
                        print("Arguments:")
                        for prop_name, prop_info in schema['properties'].items():
                            prop_type = prop_info.get('type', 'unknown')
                            prop_desc = prop_info.get('description', 'No description')
                            
                            # Check if optional
                            required = schema.get('required', [])
                            optional = " (optional)" if prop_name not in required else " (required)"
                            
                            # Check for enum values
                            if 'enum' in prop_info:
                                enum_vals = ', '.join([f'"{v}"' for v in prop_info['enum']])
                                print(f"  - {prop_name} ({prop_type}){optional}: {prop_desc}")
                                print(f"    Options: {enum_vals}")
                            else:
                                print(f"  - {prop_name} ({prop_type}){optional}: {prop_desc}")
                    
                    # Print full schema for reference
                    print(f"\nFull Schema:")
                    print(json.dumps(schema, indent=2))


if __name__ == "__main__":
    asyncio.run(list_tools())
