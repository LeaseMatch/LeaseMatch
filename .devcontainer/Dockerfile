FROM python:3.9-slim

RUN apt-get update

RUN apt-get install -y curl git

RUN pip install aws-cdk-lib>=2.0.0 constructs>=10.0.0 boto3==1.34.125 black

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
  && apt-get install -y nodejs

RUN npm install -g aws-cdk  @aws-sdk/client-s3 --unsafe-perm true

WORKDIR /workspace

CMD ["bash"]
