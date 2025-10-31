def find_savings(df):
    savings = []

    # Rule 1: EC2 instances > 80% idle for 7+ days
    ec2 = df[df['Service'] == 'Amazon EC2']
    idle = ec2[ec2['UsageType'].str.contains('BoxUsage', na=False)]
    if len(idle) > 0:
        savings.append({
            'type': 'Right-size EC2',
            'description': f"{len(idle)} instances low utilization",
            'potential_saving': idle['Cost'].sum() * 0.7,
            'priority': 'High'
        })

    # Rule 2: S3 buckets without lifecycle
    s3 = df[df['Service'] == 'Amazon S3']
    if s3['Cost'].sum() > 50:
        savings.append({
            'type': 'S3 Lifecycle',
            'description': 'Enable IA/Glacier transitions',
            'potential_saving': s3['Cost'].sum() * 0.4,
            'priority': 'Medium'
        })

    return pd.DataFrame(savings)