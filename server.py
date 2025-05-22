import os
import json
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from dotenv import load_dotenv
from supabase import create_client, Client
from mcp.server.fastmcp import FastMCP, Context

# Load environment variables from .env file
load_dotenv()

# Create a dataclass for our application context
@dataclass
class SupabaseContext:
    """Context for the Supabase MCP server."""
    client: Client

@asynccontextmanager
async def supabase_lifespan(server: FastMCP) -> AsyncIterator[SupabaseContext]:
    """
    Manages the Supabase client lifecycle.

    Args:
        server: The FastMCP server instance

    Yields:
        SupabaseContext: The context containing the Supabase client
    """
    # Try to get from client request first
    supabase_url = server.client_request.get('supabase_url') if hasattr(server, 'client_request') and server.client_request else None
    supabase_key = server.client_request.get('supabase_key') if hasattr(server, 'client_request') and server.client_request else None

    # Fallback to environment variables
    if not supabase_url:
        supabase_url = os.getenv('SUPABASE_URL')
    if not supabase_key:
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials. Ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set as environment variables or included in the client request under 'supabase_url' and 'supabase_key' keys. For environment variables, you can set them in a .env file or directly in your terminal before running the server.")

    # Initialize Supabase client
    supabase_client = create_client(supabase_url, supabase_key)

    try:
        yield SupabaseContext(client=supabase_client)
    finally:
        # No explicit cleanup needed for Supabase client
        pass

# Create the MCP server instance using the lifespan manager
mcp = FastMCP(
    "supabase_mcp_server",
    description="MCP server for interacting with Supabase databases using FastMCP patterns",
    lifespan=supabase_lifespan
)

@mcp.tool()
def read_table_rows(
    ctx: Context,
    table_name: str,
    columns: str = "*",
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    order_by: Optional[str] = None,
    ascending: bool = True
) -> List[Dict[str, Any]]:
    """
    Reads rows from a specified Supabase table with optional filtering, ordering, and limiting.

    Args:
        ctx: The MCP context.
        table_name (str): The name of the table to read from.
        columns (str): Comma-separated list of columns to select (default: "*" for all columns).
        filters (Optional[Dict[str, Any]]): Dictionary of column-value pairs to filter rows (e.g., {"is_active": True}).
        limit (Optional[int]): The maximum number of rows to return.
        order_by (Optional[str]): Column name to order results by.
        ascending (bool): Whether to sort in ascending order (default: True).

    Returns:
        List[Dict[str, Any]]: A list of rows (as dictionaries) from the table, or raises an error on failure.
    """
    supabase = ctx.request_context.lifespan_context.client
    try:
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Invalid table_name provided. Must be a non-empty string.")
        if limit is not None and (not isinstance(limit, int) or limit <= 0):
            raise ValueError("Invalid limit provided. Must be a positive integer.")

        query = supabase.table(table_name).select(columns)
        if filters:
            if not isinstance(filters, dict):
                raise ValueError("Invalid filters provided. Must be a dictionary.")
            for column, value in filters.items():
                query = query.eq(column, value)
        if order_by:
            if not isinstance(order_by, str):
                raise ValueError("Invalid order_by provided. Must be a string.")
            query = query.order(order_by, descending=not ascending)
        if limit:
            query = query.limit(limit)
        response = query.execute()
        return response.data
    except Exception as e:
        raise Exception(f"An error occurred while reading rows from table '{table_name}': {str(e)}") from e

# @mcp.tool()
# def create_table_records(
#     ctx: Context,
#     table_name: str,
#     records: Union[Dict[str, Any], List[Dict[str, Any]]]
# ) -> Dict[str, Any]:
#     """
#     Creates one or multiple new records in a Supabase table.

#     Args:
#         ctx: The MCP context.
#         table_name (str): The name of the table to create the record(s) in.
#         records (Union[Dict[str, Any], List[Dict[str, Any]]]): A dictionary for a single record or a list of dictionaries for multiple records.

#     Returns:
#         Dict[str, Any]: Dictionary containing the created records' data, count, and status.
#     """
#     supabase = ctx.request_context.lifespan_context.client
#     try:
#         if not table_name or not isinstance(table_name, str):
#             raise ValueError("Invalid table_name provided. Must be a non-empty string.")
#         if not records or not (isinstance(records, dict) or isinstance(records, list)):
#             raise ValueError("Invalid records provided. Must be a non-empty dictionary or list.")
#         if isinstance(records, list) and not all(isinstance(r, dict) for r in records):
#             raise ValueError("Invalid records list provided. All items must be dictionaries.")
#         response = supabase.table(table_name).insert(records).execute()
#         data = response.data
#         count = len(data) if data else 0
#         return {"data": data, "count": count, "status": "success" if count > 0 else "no records created or error"}
#     except Exception as e:
#         raise Exception(f"An error occurred while creating record(s) in table '{table_name}': {str(e)}") from e

# @mcp.tool()
# def update_table_records(
#     ctx: Context,
#     table_name: str,
#     updates: Dict[str, Any],
#     filters: Dict[str, Any]
# ) -> Dict[str, Any]:
#     """
#     Updates existing records in a Supabase table based on filters.

#     Args:
#         ctx: The MCP context.
#         table_name (str): The name of the table to update records in.
#         updates (Dict[str, Any]): A dictionary containing the updates to apply.
#         filters (Dict[str, Any]): A dictionary of column-value pairs to filter which rows to update.

#     Returns:
#         Dict[str, Any]: Dictionary containing the updated records' data, count, and status.
#     """
#     supabase = ctx.request_context.lifespan_context.client
#     try:
#         if not table_name or not isinstance(table_name, str):
#             raise ValueError("Invalid table_name provided. Must be a non-empty string.")
#         if not updates or not isinstance(updates, dict):
#             raise ValueError("Invalid updates provided. Must be a non-empty dictionary.")
#         if not filters or not isinstance(filters, dict):
#             raise ValueError("Invalid filters provided. Must be a non-empty dictionary.")
#         query = supabase.table(table_name).update(updates)
#         for column, value in filters.items():
#             query = query.eq(column, value)
#         response = query.execute()
#         data = response.data
#         count = len(data) if data else 0
#         return {"data": data, "count": count, "status": "success" if count > 0 else "no records updated or error"}
#     except Exception as e:
#         raise Exception(f"An error occurred while updating records in table '{table_name}': {str(e)}") from e

# @mcp.tool()
# def delete_table_records(
#     ctx: Context,
#     table_name: str,
#     filters: Dict[str, Any]
# ) -> Dict[str, Any]:
#     """
#     Deletes records from a Supabase table based on filters.

#     Args:
#         ctx: The MCP context.
#         table_name (str): The name of the table to delete records from.
#         filters (Dict[str, Any]): A dictionary of column-value pairs to filter which rows to delete.

#     Returns:
#         Dict[str, Any]: Dictionary containing the deleted records' data, count, and status.
#     """
#     supabase = ctx.request_context.lifespan_context.client
#     try:
#         if not table_name or not isinstance(table_name, str):
#             raise ValueError("Invalid table_name provided. Must be a non-empty string.")
#         if not filters or not isinstance(filters, dict):
#             raise ValueError("Invalid filters provided. Must be a non-empty dictionary.")
#         query = supabase.table(table_name).delete()
#         for column, value in filters.items():
#             query = query.eq(column, value)
#         response = query.execute()
#         data = response.data
#         count = len(data) if data else 0
#         return {"data": data, "count": count, "status": "success" if count > 0 else "no records deleted or error"}
#     except Exception as e:
#         raise Exception(f"An error occurred while deleting records from table '{table_name}': {str(e)}") from e

# @mcp.tool()
# def create_table(ctx: Context, table_name: str, schema: list) -> dict:
#     """
#     Creates a new table in the Supabase database using an RPC call.

#     Note: This requires the PostgreSQL function 'create_new_table(p_table_name TEXT, p_columns JSONB)'
#     to be defined in your Supabase SQL editor.

#     Args:
#         ctx: The MCP context.
#         table_name (str): The name of the table to create. Must be a valid PostgreSQL identifier.
#         schema (list): A list of column definitions. Each item must be a dictionary
#                        containing 'name' (str), 'type' (str, e.g., 'TEXT', 'INT'),
#                        and optionally 'constraints' (str, e.g., 'PRIMARY KEY', 'NOT NULL').

#     Returns:
#         dict: Contains 'success' (bool) and 'message' (str) indicating the result from the RPC call.
#     """
#     supabase = ctx.request_context.lifespan_context.client
#     try:
#         if not table_name or not isinstance(table_name, str):
#             return {'success': False, 'message': "Invalid table name - must be a non-empty string."}
#         if not schema or not isinstance(schema, list):
#             return {'success': False, 'message': "Invalid schema - must be a non-empty list of column definitions."}
#         for col in schema:
#             if not isinstance(col, dict) or 'name' not in col or 'type' not in col:
#                 return {'success': False, 'message': "Invalid column definition: Each column must be a dict with 'name' and 'type'."}
#             if not isinstance(col['name'], str) or not col['name']:
#                 return {'success': False, 'message': f"Invalid column name: '{col['name']}' must be a non-empty string."}
#             if not isinstance(col['type'], str) or not col['type']:
#                 return {'success': False, 'message': f"Invalid column type for '{col['name']}': Type must be a non-empty string."}
#             if 'constraints' in col and not isinstance(col.get('constraints'), str):
#                 return {'success': False, 'message': f"Invalid constraints for '{col['name']}': Constraints must be a string."}
#         response = supabase.rpc('create_new_table', {'p_table_name': table_name, 'p_columns': schema}).execute()
#         message = response.data if response.data else "No response message from RPC."
#         success = "successfully" in str(message).lower() or "table created successfully" in str(message).lower()
#         return {'success': success, 'message': str(message)}
#     except Exception as e:
#         return {'success': False, 'message': f"An error occurred during create_table: {str(e)}"}

@mcp.tool()
def list_tables(ctx: Context) -> list:
    """
    Lists all tables in the 'public' schema of the Supabase database using an RPC call.

    Note: This requires the PostgreSQL function 'list_tables_in_schema(schema_name TEXT DEFAULT 'public')'
    to be defined in your Supabase SQL editor.

    Args:
        ctx: The MCP context.

    Returns:
        list: A list of table names in the public schema.
    """
    supabase = ctx.request_context.lifespan_context.client
    try:
        response = supabase.rpc('list_tables_in_schema', {'schema_name': 'public'}).execute()
        if response.data:
            return [table['table_name'] for table in response.data if isinstance(table, dict) and 'table_name' in table]
        return []
    except Exception as e:
        raise Exception(f"An error occurred while listing tables: {str(e)}") from e

if __name__ == "__main__":
    mcp.run()
