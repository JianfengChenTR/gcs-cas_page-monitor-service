import boto3

ssm_client = boto3.client('ssm')


def get_parameter_value(key: str) -> str:
    return ssm_client.get_parameter(Name=key, WithDecryption=True)['Parameter']['Value']
