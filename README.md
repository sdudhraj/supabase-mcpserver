# Supabase MCP Server

This project implements a Model Context Protocol (MCP) server that provides tools for interacting with a Supabase database. The server enables AI assistants to perform database operations through a standardized interface.

## Setup

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3.  Create a `.env` file with your Supabase project URL and service role key:

    ```
    SUPABASE_URL=your_supabase_url
    SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
    ```

4.  Run the server:

    ```bash
    python server.py
    ```

## Docker

1.  Build the Docker container:

    ```bash
    docker build -t mcp-server .
    ```

2.  Run the container:

    ```bash
    docker run -p 8000:8000 mcp-server
    ```

    This will build an image named `mcp-server` and then run it, mapping port 8000 on your host to port 8000 in the container.

## GitHub Repository

To push the files to a GitHub repository, follow these steps:

1.  Initialize a Git repository in the current directory:

    ```bash
    git init
    ```

2.  Add all the files to the staging area:

    ```bash
    git add .
    ```

3.  Commit the changes:

    ```bash
    git commit -m "Initial commit"
    ```

4.  Rename the branch to main:

    ```bash
    git branch -M main
    ```

5.  Add the remote repository:

    ```bash
    git remote add origin https://github.com/amraly83/supabase-mcp-server.git
    ```

6.  Push the files to the repository:

    ```bash
    git push -u origin main
    ```

    You may be prompted for your GitHub username and password. If you have 2FA enabled, you'll need to use a personal access token instead of your password.

## Usage

The server provides the following tools:

-   `read_rows(table_name: str = None, limit: int = 10)`: Reads rows from a Supabase table.
    -   `table_name`: The name of the table to read from. This is an optional parameter. If no table name is provided, it will return rows from all tables.
    -   `limit`: The maximum number of rows to return. Defaults to 10. This is an optional parameter.
-   `create_record(table_name: str, record: dict)`: Creates a new record in a Supabase table.
    -   `table_name`: The name of the table to create the record in.
    -   `record`: A dictionary containing the data for the new record.
-   `update_record(table_name: str, record_id: int, updates: dict)`: Updates an existing record in a Supabase table.
    -   `table_name`: The name of the table to update the record in.
    -   `record_id`: The ID of the record to update.
    -   `updates`: A dictionary containing the updates to apply to the record.
-   `delete_record(table_name: str, record_id: int)`: Deletes a record from a Supabase table.
    -   `table_name`: The name of the table to delete the record from.
    -   `record_id`: The ID of the record to delete.
-   `list_tables()`: Lists all tables in the Supabase database.
-   `create_table(table_name: str, schema: list)`: Creates a new table in the Supabase database.
    -   `table_name`: The name of the table to create.
    -   `schema`: A list of dictionaries, where each dictionary represents a column in the table. Each dictionary must have the keys "name" and "type".

## Example

To use the server, you can send JSON requests to the server's standard input. For example, to read the first 5 rows from a table named "products", you would send the following JSON:

```json
{
    "tool": "read_rows",
    "arguments": {
        "table_name": "products",
        "limit": 5
    }
}
```

To list all tables in the Supabase database, you would send the following JSON:

```json
{
    "tool": "list_tables",
    "arguments": {}
}
```

To create a new table named "users" with columns "id" (SERIAL PRIMARY KEY) and "name" (TEXT), you would send the following JSON:

```json
{
    "tool": "create_table",
    "arguments": {
        "table_name": "users",
        "schema": [
            {"name": "id", "type": "SERIAL PRIMARY KEY"},
            {"name": "name", "type": "TEXT"}
        ]
    }
}
