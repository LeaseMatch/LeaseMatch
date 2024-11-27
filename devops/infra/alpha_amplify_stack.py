from aws_cdk import Stack, SecretValue
from aws_cdk import aws_amplify_alpha as amplify_alpha
from constructs import Construct


class AlphaAmplifyStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the Amplify App
        amplify_app = amplify_alpha.App(
            self,
            "LeaseMatch",
            source_code_provider=amplify_alpha.GitHubSourceCodeProvider(
                owner="NeckerFree",
                repository="LeaseMatchFrontend",
                oauth_token=SecretValue.secrets_manager("github-token-cdk"),
            ),
        )

        # Add a branch to the Amplify App
        amplify_app.add_branch("cognito-auth")

        # Add a build specification (if needed)
        amplify_app.add_environment(
            name="BUILD_SPEC",
            value=self.get_build_spec(),
        )

    def get_build_spec(self):
        # BuildSpec formatted for Amplify fullstack or specific needs
        return {
            "version": "1.0",
            "frontend": {
                "phases": {
                    "preBuild": {
                        "commands": ["npm install"]
                    },
                    "build": {
                        "commands": ["npm run build"]
                    },
                },
                "artifacts": {
                    "baseDirectory": "dist",
                    "files": ["**/*"]
                },
                "cache": {
                    "paths": ["node_modules/**/*"]
                }
            }
        }
