import replicate
from dotenv import load_dotenv
import json
load_dotenv()

def get_completion(prompt='', messages=[]):
    input = {
        "prompt":  f"""You are a helpful assistant with immense knowlege of devops, 
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
         
         
         QUES: {prompt}.
         """,
        "temperature": 0.2
    }

    out = replicate.run(
        "snowflake/snowflake-arctic-instruct",
        input=input
    )

    output = "".join(out)

    return {
        "func": output,
        "fname": "generate_infra_diagram"
    }

# get_completion(prompt="An EC2 instance group with a load balancer infront", messages=[])