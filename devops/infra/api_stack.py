from aws_cdk import (
    Duration,
    Stack,
    aws_lambda,
    aws_dynamodb,
    RemovalPolicy,
    aws_apigateway
    # aws_sqs as sqs,
)
from constructs import Construct

class PropetiesAPIStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        properties_lambda_function = aws_lambda.Function(
            self,
            id="properties",
            handler="properties.lambda_handler",
            code=aws_lambda.Code.from_asset("./api"),
            timeout=Duration.seconds(2),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
        )

        global_table = aws_dynamodb.TableV2(
            self,
            id="LeaseMatch",
            table_name="LeaseMatch",
            billing=aws_dynamodb.Billing.on_demand(),
            partition_key=aws_dynamodb.Attribute(
                name="id", type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )


        propierties_api = aws_apigateway.RestApi(self, id="LeaseMatch", rest_api_name="LeaseMatch-Api")


        properties_table = propierties_api.root.add_resource("properties")

        integration_fn_properties = aws_apigateway.LambdaIntegration(properties_lambda_function)

        properties_table.add_method("GET", integration_fn_properties)

        properties_table.add_method(
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
