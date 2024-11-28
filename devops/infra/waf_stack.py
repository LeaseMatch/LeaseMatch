from aws_cdk import (
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

class WafStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ### WAF para CloudFront ###
        # IP Set para bloqueo de IPs
        ipSet = aws_wafv2.CfnIPSet(
            self,
            id="ip_set",
            name="IpSet",
            addresses=[
                #"103.10.10.10/32",
                # "186.155.18.40/32",
            ],
            ip_address_version="IPV4",
            scope="CLOUDFRONT",
            description="IpSet para bloquear ip en especifico y segmentos de red",
        )

        # Regla de bloqueo basada en el IP Set
        RuleIpSet = aws_wafv2.CfnWebACL.RuleProperty(
            name="Rule_Allow_ip_set",
            priority=102,  # se evalua las diferentes reglas en funcion a la prioridad, todas las reglas deberian tener prioridades diferentes
            action=aws_wafv2.CfnWebACL.RuleActionProperty(allow={}),
            statement=aws_wafv2.CfnWebACL.StatementProperty(
                ip_set_reference_statement=aws_wafv2.CfnWebACL.IPSetReferenceStatementProperty(
                    arn=ipSet.attr_arn
                )
            ),
            visibility_config=aws_wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="metricas-ipset-rule",
                sampled_requests_enabled=True,
            ),
        )
        
        countryCodes = ["CO"]
        
        GeoRule = aws_wafv2.CfnWebACL.RuleProperty(
            name="Rule_Geo_match_property",
            priority=101,
            action=aws_wafv2.CfnWebACL.RuleActionProperty(allow={}),
            statement=aws_wafv2.CfnWebACL.StatementProperty(
                geo_match_statement=aws_wafv2.CfnWebACL.GeoMatchStatementProperty(
                    country_codes=countryCodes
                )
            ),
            visibility_config=aws_wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="metricas-Geo-rule",
                sampled_requests_enabled=True,
            ),
        )

        # WAF asociado a CloudFront
        acl = aws_wafv2.CfnWebACL(
            self,
            id="CloudFrontWAF",
            name="Firewall-class",
            default_action=aws_wafv2.CfnWebACL.DefaultActionProperty(block={}),
            scope="CLOUDFRONT",
            visibility_config=aws_wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="metricas",
                sampled_requests_enabled=True,
            ),
            description="corta descripcion",
            rules=[RuleIpSet,GeoRule],
        )

        # Distribución de CloudFront asociada al WAF 
        distribution = aws_cloudfront.CfnDistribution(
        self,
        id="MyDistribution-292",
        distribution_config=aws_cloudfront.CfnDistribution.DistributionConfigProperty(
            origins=[
                aws_cloudfront.CfnDistribution.OriginProperty(
                    domain_name="development.d3u15bor4oundq.amplifyapp.com",
                    id="AmplifyOrigin",
                    custom_origin_config=aws_cloudfront.CfnDistribution.CustomOriginConfigProperty(
                        http_port=80,
                        https_port=443,
                        origin_protocol_policy="https-only",  # Forces HTTPS connection
                    ),
                )
            ],
            default_cache_behavior=aws_cloudfront.CfnDistribution.DefaultCacheBehaviorProperty(
                target_origin_id="AmplifyOrigin",
                viewer_protocol_policy="redirect-to-https",
                allowed_methods=["GET", "HEAD"],
                cached_methods=["GET", "HEAD"],
                forwarded_values=aws_cloudfront.CfnDistribution.ForwardedValuesProperty(
                    query_string=False,
                    cookies=aws_cloudfront.CfnDistribution.CookiesProperty(forward="none"),
                ),
            ),
           custom_error_responses=[
                aws_cloudfront.CfnDistribution.CustomErrorResponseProperty(
                    error_code=404,
                    response_code=404,
                    response_page_path="/404.html",
                ),
                aws_cloudfront.CfnDistribution.CustomErrorResponseProperty(
                    error_code=403,
                    response_code=403,
                    response_page_path="/404.html",
                ),
            ],
            enabled=True,
            web_acl_id=acl.attr_arn,
            ),
        )

