import os

import snowflake.connector
from snowflake.connector.errors import OperationalError
import json

# Function to connect to Snowflake and get response from the model
    # Connect to Snowflake
SYSTEM_PROMPT = """
        You are a helpful assistant with immense knowlege of devops,
        infrastructure. Use the pip package, `diagrams`, and generate the code for an infrastructure. diagram
            for the infra described below after QUES:
            Remember in `diagrams` cloud provider imports are lower case. aws not AWS etc. Every grouping of elements is a
        Cluster (with Cluster("VPC"): etc
        IMPORTANT & CRITICAL NOTE:
        1) The code and imports should be INSIDE a well formatted python function. SAMPLE OUTPUT
        :
        def generate_infra_diagram():
            from diagrams import Cluster, Diagram
            from diagrams.aws.compute import EC2
            from diagrams.aws.network import ELB
            with Diagram("Infra Diagram", show=False, filename='outputs/filename') as diag:
                dns = Route53("Route53")
            return diag
        
            DO NOT MENTION THE LANGUAGE OR ANYTHING
        2) The response should ONLY be the function code and name should always be generate_infra_diagram
        3) The name of the diagram should always be Infra Diagram.
        4) ALL IMPORTS MUST BE INSIDE the FUNCTION
        5) The function should return the diagram object (Eg:
        with Diagram("Infra Diagram", show=False, filename='outputs/filebro') as diag:
            dns = Route53("Route53")
        return diag
        6) func: Should only be a python method WITH NO INDENT
     """


def get_completion(messages=[{"role": "system", "content": "You are a helpful assistant that replies with valid json"}], model="snowflake-arctic"):

    user = os.environ.get('SNOWFLAKE_USER')
    password = os.environ.get('SNOWFLAKE_PASSWORD')
    account = os.environ.get('SNOWFLAKE_ACCOUNT')
    warehouse = os.environ.get('SNOWFLAKE_WAREHOUSE')

    try:
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse
        )
        cursor = conn.cursor()


        # Convert the prompts to a JSON string
        prompts_json = json.dumps(messages)

        # Define your query
        query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'snowflake-arctic',
            PARSE_JSON(%(prompts)s)
        ) AS response;
        """
        # Execute the query
        cursor = conn.cursor()
        cursor.execute(query, {'prompts': prompts_json})

        # Fetch and print the results
        result = cursor.fetchone()
        return json.dumps({
            'func': result[0].strip(),
            'fname': 'generate_infra_diagram'
        })

    except OperationalError as e:
        print("OperationalError:", e)
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()