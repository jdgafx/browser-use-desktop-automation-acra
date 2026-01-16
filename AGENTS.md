# AGENTS.md - MCP Server Project

## Build Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev              # Check package.json for specific command

# Build (if applicable)
npm run build

# Run tests
npm run test
```

## Code Style Guidelines

### Imports
```typescript
// ES modules
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
```

### MCP Server Pattern
```typescript
// Standard MCP server structure
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const server = new Server({
  name: 'mcp-server-name',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
  },
});

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'tool-name',
        description: 'What this tool does',
        inputSchema: {
          type: 'object',
          properties: {
            param1: { type: 'string', description: 'Parameter description' },
          },
          required: ['param1'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  // Implement tool logic
});
```

### Naming Conventions
```typescript
// Tools: snake_case (MCP convention)
const TOOL_NAME = 'search_documents';

// Variables: camelCase
const isProcessing = true;

// Constants: UPPER_SNAKE_CASE
const MAX_RESULTS = 100;
```

### Error Handling
```typescript
// ✅ Correct - Return error responses properly
if (!input.url) {
  return {
    content: [
      {
        type: 'text',
        text: 'Error: URL is required',
        isError: true,
      },
    ],
  };
}
```

## Project Structure

```
/src
  index.ts             # Main entry point
  /tools              # Tool implementations
  /utils              # Utility functions
/tests                # Test files
```

## Environment Variables

```bash
# Add relevant environment variables
API_KEY="your-api-key"
ENDPOINT_URL="https://api.example.com"
```
