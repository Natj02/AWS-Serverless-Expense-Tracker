import boto3, csv, logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Expenses')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    logger.info(f"Reading s3://{bucket}/{key}")

    obj = s3.get_object(Bucket=bucket, Key=key)
    lines = obj['Body'].read().decode('utf-8').splitlines()
    reader = csv.DictReader(lines)

    count = 0
    for row in reader:
        try:
            item = {
                'id': row['id'].strip(),
                'date': row['date'].strip(),
                'category': row['category'].strip(),
                'amount': Decimal(str(row['amount']).strip() or "0")
            }
            table.put_item(Item=item)
            count += 1
        except Exception as e:
            logger.error(f"Failed row: {row} error: {e}")
            raise

    logger.info(f"Inserted {count} items into Expenses")
    return {'statusCode': 200, 'body': f'Inserted {count} items'}
