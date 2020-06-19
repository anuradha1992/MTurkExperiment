import boto3
import csv
import json
import datetime

# --------------------- HELPER METHODS --------------------- 

# Quick method to encode url parameters
def encode_get_parameters(baseurl, arg_dict):
    queryString = baseurl + "?"
    for indx, key in enumerate(arg_dict):
        queryString += str(key) + "=" + str(arg_dict[key])
        if indx < len(arg_dict)-1:
            queryString += "&"
    return queryString

# --------------------- MAIN CODE --------------------- 

aws_access_key_id = 'YOUR_ACCESS_ID'
aws_secret_access_key = 'YOUR_SECRET_KEY'

with open('./rootkey.csv', 'r') as infile:
  readCSV = csv.reader(infile, delimiter=',')
  count = 0
  for row in readCSV:
    if count == 0:
      aws_access_key_id = row[0].strip().split('=')[1]
    elif count == 1:
      aws_secret_access_key = row[0].strip().split('=')[1]
    count += 1

config = json.load(open("config.json"))
HIT = config["HIT"]
params_to_encode = {}

if HIT["USE_SANDBOX"]:
    print("review HIT on sandbox")
    endpoint_url = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
    mturk_form_action = "https://workersandbox.mturk.com/mturk/externalSubmit"
    mturk_url = "https://workersandbox.mturk.com/"
    external_submit_endpoint = "https://workersandbox.mturk.com/mturk/externalSubmit"
else:
    print("review HIT on mturk")
    endpoint_url = "https://mturk-requester.us-east-1.amazonaws.com"
    mturk_form_action = "https://www.mturk.com/mturk/externalSubmit"
    mturk_url = "https://worker.mturk.com/"
    external_submit_endpoint = "https://www.mturk.com/mturk/externalSubmit"

client = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=HIT["REGION_NAME"],
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# This will return $10,000.00 in the MTurk Developer Sandbox
print(client.get_account_balance()['AvailableBalance'])

# create HITs
print("Deleting HITs...")

hitids = [
    '36D1BWBEHN2TYQL27Z284N8TTTAM29',
    '3OZ4VAIBEXGCU9DJSC9RQ0DNMX8JVA',
    '3HUR21WDDUQUTNDDERBCO8PWFCPXYL',
    '3CRWSLD91K575XA7UX05B0BWUY6OMH',
    '32LAQ1JNT9Q6VXKOZGDQWKYD6SQTU0',
    '3YO4AH2FPDLDNVGGK55B28ZJ6WO0QR',
    '3VMV5CHJZ8GNQFJTFBO9S5XMXKBGTN',
    '385MDVINFCGP9YDOIMENC2W1T6AJWK',
    '3ZFRE2BDQ9FUYDNIADDV2FYYL6TXZC',
    '3P4ZBJFX2V494WRSZWN2X4490ZTWFU'
]

for ids in hitids:
    response = client.update_expiration_for_hit(
        HITId=ids,
        ExpireAt=datetime.datetime(2015, 1, 1)
    )
    print(response)

print("===")

for ids in hitids:
    response = client.delete_hit(
        HITId=ids
    )
    print(response)