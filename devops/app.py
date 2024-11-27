#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infra.api_stack import PropetiesAPIStack
from infra.alpha_amplify_stack import AlphaAmplifyStack

app = cdk.App()
PropetiesAPIStack(app, "api")
AlphaAmplifyStack(app, "frontend")
app.synth()