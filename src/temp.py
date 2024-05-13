def generate_aws_infrastructure_diagram():
    from diagrams import Diagram, Cluster
    from diagrams.aws.network import Route53, ELB
    from diagrams.aws.compute import ECS
    from diagrams.aws.database import RDS
    from diagrams.aws.storage import S3
    from diagrams.aws.database import ElasticacheForRedis

    with Diagram("Infra Diagram", show=False, filename='outputs/aws_infrastructure') as diag:
        with Cluster("VPC"):
            dns = Route53("Route53")
            lb = ELB("Load Balancer")
            with Cluster("ECS Services"):
                ecs_services = [ECS("ECS Service") for _ in range(3)]
                ecr = S3("ECR Repository")
                lb >> ecs_services
                ecs_services >> ecr

            db = RDS("RDS Database")
            cache = ElasticacheForRedis("ElasticacheForRedis")

            ecs_services >> db
            ecs_services >> cache

    return diag


generate_aws_infrastructure_diagram()