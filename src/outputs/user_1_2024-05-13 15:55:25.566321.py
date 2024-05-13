def generate_aws_infrastructure_diagram():
    from diagrams import Diagram, Cluster
    from diagrams.aws.network import Route53, ELB
    from diagrams.aws.compute import EC2
    from diagrams.aws.database import RDS
    from diagrams.aws.database import ElastiCache
    from diagrams.aws.network import VPC
    
    with Diagram("Infra Diagram", show=False, filename='outputs/aws_infrastructure') as diag:
        with Cluster("VPC"):
            dns = Route53("Route53")
            lb = ELB("Load Balancer")
            with Cluster("EC2 Instances"):
                ec2_instances = [EC2("App Server 1"), EC2("App Server 2"), EC2("App Server 3")]
            db = RDS("RDS Database")
            cache = ElastiCache("Elastic Cache")
            
            dns >> lb >> ec2_instances
            ec2_instances >> db
            ec2_instances >> cache
    
    return diag