import boto3
import pandas as pd
from datetime import datetime, timedelta

def get_aws_costs(days=30):
    client = boto3.client('ce')
    end = datetime.utcnow().strftime('%Y-%m-%d')
    start = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')

    response = client.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )

    records = []
    for day in response['ResultsByTime']:
        for group in day['Groups']:
            records.append({
                'Date': day['TimePeriod']['Start'],
                'Service': group['Keys'][0],
                'Cost': float(group['Metrics']['UnblendedCost']['Amount'])
            })
    return pd.DataFrame(records)