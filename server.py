import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_supabase_client():
    return supabase

# Get initialized client
supabase = get_supabase_client()

def read_rows(table_name: str, limit: int = 10):
    """
    Reads rows from a specified Supabase table.

    This tool allows you to retrieve data from a specific table in your Supabase database.
    You must specify the table name. You can optionally limit the number of rows returned.

    Args:
        table_name (str): The name of the table to read from. This is a required parameter.
        limit (int): The maximum number of rows to return. Defaults to 10. This is an optional parameter.

    Returns:
        list: A list of rows from the table, or an error dictionary if unsuccessful.
              Each row is a dictionary containing the data for that row.

    Usage:
        To read the first 10 rows from a table named "products", call with table_name="products".
        To read the first 20 rows from the same table, call with table_name="products" and limit=20.
    """
    try:
        if not table_name or not isinstance(table_name, str):
             return {"error": "Invalid table_name provided. Must be a non-empty string."}
        if not isinstance(limit, int) or limit <= 0:
             return {"error": "Invalid limit provided. Must be a positive integer."}
             
        response = supabase.table(table_name).select("*").limit(limit).execute()
        # TODO: Add more specific error checking based on response structure if needed
        return response.data
    except Exception as e:
        return {"error": f"An error occurred while reading rows from table '{table_name}': {str(e)}"}

def create_record(table_name: str, record: dict):
    """
    Creates a new record in a Supabase table.

    This tool allows you to create a new record in a specified table in your Supabase database.
    You must provide the table name and a dictionary containing the data for the new record.

    Args:
        table_name (str): The name of the table to create the record in. This is a required parameter.
        record (dict): A dictionary containing the data for the new record. This is a required parameter.

    Returns:
        dict: The newly created record.

    Usage:
        To create a new record in a table named "products" with data {"name": "Example Product", "price": 9.99},
        you would call this tool with table_name="products" and record={"name": "Example Product", "price": 9.99}.
    """
    try:
        if not table_name or not isinstance(table_name, str):
             return {"error": "Invalid table_name provided. Must be a non-empty string."}
        if not record or not isinstance(record, dict):
             return {"error": "Invalid record provided. Must be a non-empty dictionary."}

        response = supabase.table(table_name).insert(record).execute()
        # TODO: Add more specific error checking based on response structure if needed
        return response.data
    except Exception as e:
        return {"error": f"An error occurred while creating a record in table '{table_name}': {str(e)}"}


def update_record(table_name: str, record_id: int, updates: dict):
    """
    Updates an existing record in a Supabase table.

    This tool allows you to update an existing record in a specified table in your Supabase database.
    You must provide the table name, the ID of the record to update, and a dictionary containing the updates to apply.

    Args:
        table_name (str): The name of the table to update the record in. This is a required parameter.
        record_id (int): The ID of the record to update. This is a required parameter.
        updates (dict): A dictionary containing the updates to apply to the record. This is a required parameter.

    Returns:
        dict: The updated record.

    Usage:
        To update the record with ID 1 in a table named "products" to change the price to 19.99,
        you would call this tool with table_name="products", record_id=1, and updates={"price": 19.99}.
    """
    try:
        if not table_name or not isinstance(table_name, str):
             return {"error": "Invalid table_name provided. Must be a non-empty string."}
        # Assuming record_id should be an integer, add type check if necessary
        if not isinstance(record_id, int):
             return {"error": "Invalid record_id provided. Must be an integer."}
        if not updates or not isinstance(updates, dict):
             return {"error": "Invalid updates provided. Must be a non-empty dictionary."}

        response = supabase.table(table_name).update(updates).eq("id", record_id).execute()
        # TODO: Add more specific error checking based on response structure if needed
        return response.data
    except Exception as e:
        return {"error": f"An error occurred while updating record ID {record_id} in table '{table_name}': {str(e)}"}


def delete_record(table_name: str, record_id: int):
    """
    Deletes a record from a Supabase table.

    This tool allows you to delete a record from a specified table in your Supabase database.
    You must provide the table name and the ID of the record to delete.

    Args:
        table_name (str): The name of the table to delete the record from. This is a required parameter.
        record_id (int): The ID of the record to delete. This is a required parameter.

    Returns:
        dict: The deleted record.

    Usage:
        To delete the record with ID 1 from a table named "products",
        you would call this tool with table_name="products" and record_id=1.
    """
    try:
        if not table_name or not isinstance(table_name, str):
             return {"error": "Invalid table_name provided. Must be a non-empty string."}
        # Assuming record_id should be an integer, add type check if necessary
        if not isinstance(record_id, int):
             return {"error": "Invalid record_id provided. Must be an integer."}

        response = supabase.table(table_name).delete().eq("id", record_id).execute()
        # TODO: Add more specific error checking based on response structure if needed
        # Check if delete was successful, response.data might be empty on success
        # Consider returning a success message or status
        return response.data # May need adjustment based on actual successful delete response
    except Exception as e:
        return {"error": f"An error occurred while deleting record ID {record_id} from table '{table_name}': {str(e)}"}


import json # Add json import for schema conversion

def create_table(table_name: str, schema: list):
    """
    Creates a new table in the Supabase database using an RPC call.

    Note: This requires the PostgreSQL function 'create_new_table(p_table_name TEXT, p_columns JSONB)'
    to be defined in your Supabase SQL editor. See implementation comments for the function definition.

    Args:
        table_name (str): The name of the table to create. Must be a valid PostgreSQL identifier.
        schema (list): A list of column definitions. Each item must be a dictionary
                       containing 'name' (str), 'type' (str, e.g., 'TEXT', 'INT'),
                       and optionally 'constraints' (str, e.g., 'PRIMARY KEY', 'NOT NULL').

    Returns:
        dict: Contains 'success' (bool) and 'message' (str) indicating the result from the RPC call.
    """
    try:
        # Basic input validation
        if not table_name or not isinstance(table_name, str):
            return {'success': False, 'message': "Invalid table name - must be a non-empty string."}
        if not schema or not isinstance(schema, list):
            return {'success': False, 'message': "Invalid schema - must be a non-empty list of column definitions."}

        # Validate schema structure
        for col in schema:
            if not isinstance(col, dict) or 'name' not in col or 'type' not in col:
                 return {'success': False, 'message': "Invalid column definition: Each column must be a dict with 'name' and 'type'."}
            if not isinstance(col['name'], str) or not col['name']:
                 return {'success': False, 'message': f"Invalid column name: '{col['name']}' must be a non-empty string."}
            if not isinstance(col['type'], str) or not col['type']:
                 return {'success': False, 'message': f"Invalid column type for '{col['name']}': Type must be a non-empty string."}
            if 'constraints' in col and not isinstance(col.get('constraints'), str):
                 return {'success': False, 'message': f"Invalid constraints for '{col['name']}': Constraints must be a string."}


        # Call the RPC function
        # Convert schema list to JSONB parameter
        response = supabase.rpc('create_new_table', {'p_table_name': table_name, 'p_columns': schema}).execute()

        print(f"RPC response: {response}")

        # The RPC function returns a single text message
        message = response.data if response.data else "No response message from RPC."

        # Determine success based on the message content (adjust as needed based on SQL function)
        success = "successfully" in message.lower() or "table created successfully" in message.lower() and "error" not in message.lower()

        return {'success': success, 'message': message}

    except Exception as e:
        # Handle exceptions during RPC call or validation
        return {'success': False, 'message': f"An error occurred: {str(e)}"}


def list_tables():
    """
    Lists all tables in the Supabase database.

    This tool allows you to retrieve a list of all table names in your Supabase database.

    Args:
        None

    Returns:
        list: A list of table names.

    Usage:
        To list all tables in the Supabase database, you would call this tool with no arguments.
    """
    try:
        # Attempt to call a hypothetical RPC function to get tables from the 'public' schema
        # This assumes a function named 'list_public_tables' exists in Supabase that returns table names.
        # If this function doesn't exist, this call will fail.
        # A more robust approach might involve creating such a function in Supabase
        # or finding if Supabase/PostgREST offers a direct metadata endpoint.
        # For now, we query information_schema directly via RPC.
        # Note: This requires the function 'list_tables_in_schema' to be defined in your Supabase SQL editor:
        # CREATE OR REPLACE FUNCTION list_tables_in_schema(schema_name TEXT DEFAULT 'public')
        # RETURNS TABLE(table_name TEXT) AS $$
        # BEGIN
        #   RETURN QUERY
        #   SELECT tablename::TEXT FROM pg_catalog.pg_tables WHERE schemaname = schema_name;
        # END;
        # $$ LANGUAGE plpgsql; # End of SQL function definition

        response = supabase.rpc('list_tables_in_schema', {'schema_name': 'public'}).execute()

        # Check for errors returned by the RPC call itself or during execution
        # Note: supabase-py might raise exceptions for network/API errors, caught below.
        # This checks for logical errors returned in the data payload.
        if hasattr(response, 'error') and response.error:
             # Handle PostgREST errors if they are returned in an 'error' attribute
             return {"error": f"RPC error listing tables: {response.error}"}
             
        if response.data:
             # Check if the data itself indicates an error from the SQL function
             if isinstance(response.data, list) and len(response.data) > 0 and isinstance(response.data[0], dict) and 'error' in response.data[0]:
                  return {"error": response.data[0]['error']} # Propagate error message from SQL function
             # Otherwise, assume success and extract table names
             return [table['table_name'] for table in response.data if isinstance(table, dict) and 'table_name' in table]
        else:
            # Handle potential errors or empty results from RPC
            # Check response.error if available, though supabase-py might raise exceptions
            return {"error": "Failed to list tables or no tables found."}
            
    except Exception as e:
        # Basic error handling
        return {"error": f"An error occurred while listing tables: {str(e)}"}


tools = [
    read_rows,
    create_record,
    update_record,
    delete_record,
    list_tables,
    create_table,
]

if __name__ == "__main__":
    mcp = FastMCP("Supabase MCP Server", tools=tools)
    mcp.run()
