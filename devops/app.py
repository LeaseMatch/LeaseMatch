#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infra.api_stack import PropetiesAPIStack

app = cdk.App()
PropetiesAPIStack(app, "api")

app.synth()

