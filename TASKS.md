# Supabase MCP Server - Task List

## Backlog
- [x] Create initial project structure
- [x] Implement MCP server with Stdio transport
- [x] Implement Supabase client integration
- [x] Create tool for reading records from tables
- [x] Create tool for creating records in tables
- [x] Create tool for updating records in tables
- [x] Create tool for deleting records from tables
- [x] Update README.md with setup and usage instructions
- [x] Add unit tests for all tools
- [x] Implement error handling and logging
- [x] Create a Dockerfile for the MCP server
- [x] Push the files to a GitHub repository
- [ ] Add support for pagination in read operations
- [ ] Add support for filtering in read operations
- [ ] Add support for sorting in read operations
- [ ] Add support for joins in read operations
- [ ] Implement schema validation for input data
- [ ] Consider adding a tool for executing raw SQL queries
- [ ] Consider adding a tool for listing available tables
- [ ] Consider adding a tool for reading table schemas
- [ ] Troubleshoot "Invalid API key" error in Supabase client initialization (Added on 2025-04-22)

## Tasks in Progress
- [x] Create an MCP server written in Python (using FastMCP) to interact with a Supabase database. The server should use the Stdio transport and have the following tools:
    - Read rows in a table
    - Create a record (or multiple) in a table
    - Update a record (or multiple) in a table
    - Delete a record (or multiple) in a table
    The environment variables for this MCP server need to be the Supabase project URL and service role key.
- [x] Please review the entire codebase first to understand the main objective of this project.
- [x] can you help me troubleshoot create a new table task. please reveiw the test files before proceeding
