import snowflake.connector

# Function to connect to Snowflake and get response from the model
def get_response_from_model(prompt_array):
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user='POKHARELSRJ',
        password='Ax+by+cz=1',
        account='UHCMWNV.VBB10105',
        warehouse='COMPUTE_WH',
        database='your_database',
        schema='your_schema'
    )

    try:
        # Convert the prompt array to a string format suitable for SQL
        prompt_str = ",".join([f"'{msg}'" for msg in prompt_array])

        # Formulate the SQL query
        query = f"""
        SELECT COMPLETE(arctic_instruct_model, ARRAY_CONSTRUCT({prompt_str})) AS response
        """

        # Execute the query
        cursor = conn.cursor()
        cursor.execute(query)

        # Fetch the response
        result = cursor.fetchone()

        # Return the response
        return result[0]

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

# Example usage
prompt_array = ["User: Hello", "System: Hi there! How can I help you today?", "User: I need help with my booking."]
response = get_response_from_model(prompt_array)
print("Model Response:", response)
