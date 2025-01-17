from aws_cdk import (
    Duration,
    Stack,
    aws_lambda,
    aws_dynamodb,
    RemovalPolicy,
    aws_apigateway,
    aws_iam,
    aws_wafv2,
    aws_cloudfront,
    # aws_sqs as sqs,
)
from aws_cdk.aws_cloudfront_origins import HttpOrigin
from constructs import Construct

class PropetiesAPIStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        properties_lambda_function = aws_lambda.Function(
            self,
            id="lambda_properties_id",
            handler="properties.lambda_handler",
            code=aws_lambda.Code.from_asset("./infra/api"),
            timeout=Duration.seconds(20),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
        )

        clients_lambda_function = aws_lambda.Function(
            self,
            id="lambda_clients_id",
            handler="clients.lambda_handler",
            code=aws_lambda.Code.from_asset("./infra/api"),
            timeout=Duration.seconds(60),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
        )

        offers_lambda_function = aws_lambda.Function(
            self,
            id="lambda_offers_id",
            handler="offers.lambda_handler",
            code=aws_lambda.Code.from_asset("./infra/api"),
            timeout=Duration.seconds(60),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
        )

        properties_table = aws_dynamodb.TableV2(
            self,
            id="LeaseMatch_properties_table_id",
            table_name="LeaseMatch_properties_table",
            billing=aws_dynamodb.Billing.on_demand(),
            partition_key=aws_dynamodb.Attribute(
                name="id", type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        clients_table = aws_dynamodb.TableV2(
            self,
            id="LeaseMatch_clients_table_id",
            table_name="LeaseMatch_clients_table",
            billing=aws_dynamodb.Billing.on_demand(),
            partition_key=aws_dynamodb.Attribute(
                name="id", type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        offers_table = aws_dynamodb.TableV2(
            self,
            id="LeaseMatch_offers_table_id",
            table_name="LeaseMatch_offers_table",
            billing=aws_dynamodb.Billing.on_demand(),
            partition_key=aws_dynamodb.Attribute(
                name="id", type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        # Otorgar permisos a las Lambdas para interactuar con DynamoDB
        properties_table.grant_read_write_data(properties_lambda_function)
        clients_table.grant_read_write_data(clients_lambda_function)
        offers_table.grant_read_write_data(offers_lambda_function)

        propierties_api = aws_apigateway.RestApi(self, id="LeaseMatch_rest_api_id", rest_api_name="LeaseMatch_Api")

        properties_resource = propierties_api.root.add_resource("properties")
        clients_resource = propierties_api.root.add_resource("clients")
        offers_resource = propierties_api.root.add_resource("offers")

        integration_fn_properties = aws_apigateway.LambdaIntegration(properties_lambda_function)
        integration_fn_clients = aws_apigateway.LambdaIntegration(clients_lambda_function)

        properties_resource.add_method("GET", integration_fn_properties)
        clients_resource.add_method("GET", integration_fn_clients,authorization_type=aws_apigateway.AuthorizationType.NONE)
        clients_resource.add_method("POST", integration_fn_clients,authorization_type=aws_apigateway.AuthorizationType.NONE)
        offers_resource.add_method("GET", integration_fn_clients,authorization_type=aws_apigateway.AuthorizationType.NONE)
        offers_resource.add_method("POST", integration_fn_clients,authorization_type=aws_apigateway.AuthorizationType.NONE)

        clients_resource.add_method(
            "OPTIONS",
            aws_apigateway.MockIntegration(
                passthrough_behavior=aws_apigateway.PassthroughBehavior.NEVER,
                request_templates={"application/json": '{"statusCode": 200}'},
                integration_responses=[
                    aws_apigateway.IntegrationResponse(
                        status_code="200",
                        response_parameters={
                            "method.response.header.Access-Control-Allow-Origin": "'*'",
                            "method.response.header.Access-Control-Allow-Methods": "'GET, POST, PUT, OPTIONS'",
                            "method.response.header.Access-Control-Allow-Headers": "'Content-Type'",
                        },
                    )
                ],
            ),
            method_responses=[
                aws_apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True,
                        "method.response.header.Access-Control-Allow-Methods": True,
                        "method.response.header.Access-Control-Allow-Headers": True,
                    },
                )
            ],
        )
   