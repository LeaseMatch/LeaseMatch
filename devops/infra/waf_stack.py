from aws_cdk import (
    Stack,
    aws_wafv2,
    aws_cloudfront,
)
from constructs import Construct


class WafStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Geo Match Rule
        geo_rule = aws_wafv2.CfnWebACL.RuleProperty(
            name="AllowGeoLocation",
            priority=1,
            action=aws_wafv2.CfnWebACL.RuleActionProperty(allow={}),
            statement=aws_wafv2.CfnWebACL.StatementProperty(
                geo_match_statement=aws_wafv2.CfnWebACL.GeoMatchStatementProperty(
                    country_codes=["CO"]  # Allow traffic from Colombia
                )
            ),
            visibility_config=aws_wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="GeoLocationMetric",
                sampled_requests_enabled=True,
            ),
        )

        # WAF Web ACL
        web_acl = aws_wafv2.CfnWebACL(
            self,
            id="WebACL",
            name="AmplifyAppWAF",
            default_action=aws_wafv2.CfnWebACL.DefaultActionProperty(block={}),
            scope="CLOUDFRONT",
            visibility_config=aws_wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="WebACLMetric",
                sampled_requests_enabled=True,
            ),
            rules=[geo_rule],
            description="Web ACL for Amplify App to restrict IPs and Geo location",
        )

        # CloudFront Distribution
        distribution = aws_cloudfront.CfnDistribution(
            self,
            id="CloudFrontDistribution",
            distribution_config=aws_cloudfront.CfnDistribution.DistributionConfigProperty(
                origins=[
                    aws_cloudfront.CfnDistribution.OriginProperty(
                        domain_name="development.d3u15bor4oundq.amplifyapp.com",  # Replace with your Amplify domain
                        id="AmplifyOrigin",
                        custom_origin_config=aws_cloudfront.CfnDistribution.CustomOriginConfigProperty(
                            http_port=80,
                            https_port=443,
                            origin_protocol_policy="https-only",
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
                web_acl_id=web_acl.attr_arn,  # Attach WAF to CloudFront
            ),
        )
