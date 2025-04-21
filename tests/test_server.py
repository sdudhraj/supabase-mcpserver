import os
import pytest
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import read_rows, create_record, update_record, delete_record, list_tables, create_table
from supabase_client import get_supabase_client
from dotenv import load_dotenv

os.environ["SUPABASE_URL"] = "https://db.appautomation.cloud"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc0NDc5NzI0MCwiZXhwIjo0OTAwNDcwODQwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.E9gj8aHKWMzx_XhdFyYJIOqVV0jr2WrCwu-xSUliLgY"

load_dotenv()

supabase = get_supabase_client()

# Fixture to provide the name of the table used for testing
# Assumes 'test_table' exists in the Supabase instance defined by env vars
@pytest.fixture
def test_table_name():
    return "test_table"

# Helper fixture to ensure at least one record exists for read/update/delete tests
# This is kept separate to allow testing create on an empty table state if needed
@pytest.fixture
def ensure_test_record(test_table_name):
    # Check if record exists, create if not
    response = supabase.table(test_table_name).select("id").limit(1).execute()
    if not response.data:
         supabase.table(test_table_name).insert({"name": "Fixture Record"}).execute()
    # Yield the name, no specific cleanup here, assume test_table persists
    yield test_table_name


def test_read_rows(ensure_test_record):
    table_name = ensure_test_record
    rows = read_rows(table_name, limit=5)
    # Basic check: Ensure it returns a list (success) and not an error dict
    assert isinstance(rows, list)
    # We expect at least the fixture record
    assert len(rows) > 0

def test_create_record(test_table_name):
    rows = read_rows(test_table, limit=5)
    assert len(rows) > 0

    table_name = test_table_name
    new_record_data = {"name": "New Record"}
    created_record_list = create_record(table_name, new_record_data)
    
    # Check for success (returns list) vs error (returns dict)
    assert isinstance(created_record_list, list)
    assert len(created_record_list) == 1
    created_record = created_record_list[0]
    assert created_record is not None
    assert created_record["name"] == new_record_data["name"]
    
    # Cleanup the created record
    record_id = created_record["id"]
    delete_record(table_name, record_id)


def test_update_record(ensure_test_record):
    table_name = ensure_test_record
    # Get a record to update (the one ensured by the fixture)
    existing_records = read_rows(table_name, limit=1)
    assert isinstance(existing_records, list) and len(existing_records) > 0
    record_to_update = existing_records[0]
    record_id = record_to_update["id"]
    
    updates = {"name": "Updated Record Name"}
    updated_record_list = update_record(table_name, record_id, updates)
    
    assert isinstance(updated_record_list, list)
    assert len(updated_record_list) == 1
    updated_record = updated_record_list[0]
    assert updated_record is not None
    assert updated_record["name"] == updates["name"]
    # Optional: Revert change or verify further if needed


def test_delete_record(test_table_name):
    table_name = test_table_name
    # Create a record specifically for deletion
    record_to_delete_data = {"name": "Record To Delete"}
    created_list = create_record(table_name, record_to_delete_data)
    assert isinstance(created_list, list) and len(created_list) > 0
    record_id = created_list[0]["id"]
    
    deleted_result = delete_record(table_name, record_id)
    
    # Check response - successful delete often returns the deleted record(s)
    assert isinstance(deleted_result, list) 
    assert len(deleted_result) > 0 # Should return the record that was deleted
    assert deleted_result[0]["id"] == record_id

    # Verify it's actually gone (optional but good)
    verify_deleted = supabase.table(table_name).select("id").eq("id", record_id).execute()
    assert len(verify_deleted.data) == 0


def test_list_tables(test_table_name): # Pass fixture to ensure test_table exists when list is called
    tables_result = list_tables()
    # Check if it returned a list (success) or error dict
    assert isinstance(tables_result, list) 
    assert len(tables_result) > 0
    # Check if the known test table is in the list
    assert test_table_name in tables_result


# test_read_rows_no_table is removed as table_name is now required


import uuid

def test_create_table():
    # Note: This test requires the 'create_new_table' RPC function to exist in Supabase.
    table_name = f"test_create_table_{uuid.uuid4().hex}"  # Use a unique name
    schema = [
        {"name": "id", "type": "SERIAL", "constraints": "PRIMARY KEY"}
    ]
    result = create_table(table_name, schema)
    assert isinstance(result, dict)
    assert "success" in result
    assert result["success"] is True
