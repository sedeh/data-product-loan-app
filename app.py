import json
import pickle
import traceback
import boto3
import numpy as np

S3 = boto3.resource('s3')
KEY = 'models/loanapp.pkl'
BUCKET = 'sedeh-loanapp'
MODEL = pickle.loads(S3.Bucket(BUCKET).Object(KEY).get()['Body'].read())
FEATURES = ['loan_amnt', 'term_in_months', 'payment', 'employment_length',
            'home_owner', 'income', 'verified', 'default', 'open_accts',
            'credit_debt', 'interest_rate_by_grade']


def handler(event, context):
    """Handles API requests."""
    try:
        body = event['body']
    except KeyError:
        output = {'Bad Request': 'Request payload is missing a body'}
        return {'statusCode': 400, 'body': json.dumps(output)}
    try:
        body = json.loads(body)
        data = np.array([body[feature] for feature in FEATURES]).reshape(1, -1)
        prediction = float(MODEL.predict(data))
        return {'statusCode': 200, 'body': json.dumps(prediction)}
    except json.JSONDecodeError:
        output = {'Bad Request': 'Request is not in JSON format'}
        return {'statusCode': 400, 'body': json.dumps(output)}
    except TypeError:
        output = {'Bad Request': 'Request body is invalid'}
        return {'statusCode': 400, 'body': json.dumps(output)}
    except KeyError:
        missing = ','.join(list(set(FEATURES) - set(body.keys())))
        output = {'Bad Request': f'Request payload is missing {missing}'}
        return {'statusCode': 400, 'body': json.dumps(output)}
    except ValueError:
        output = {'Bad Request': 'Request JSON may not contain a non-numeric value'}
        return {'statusCode': 400, 'body': json.dumps(output)}
    except Exception as exception:
        tb_lines = traceback.format_exception(exception.__class__, exception, exception.__traceback__)
        print(''.join(tb_lines))
        output = {'Internal Server Error': 'Unexpected error occurred'}
        return {'statusCode': 500, 'body': json.dumps(output)}
