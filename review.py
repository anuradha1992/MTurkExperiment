import boto3
import csv
import json
from datetime import datetime
import numpy as np

import xml.etree.ElementTree as ET

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
print("Reviewing HITs...")

'''HITIds = [
    '3ZVPAMTJWN4AA061BMJESQW49ZERGL',
    '3JGHED38EDS0E87MWE7EU9C8DJAY7R',
    '360ZO6N6J1K4YA61S8HNEAG7ZZKM91',
    '3UAU495MIITQI5FG3ZRR2ASQ7K9OU9',
    '35ZRNT9RUIZ6JB2XOFVQF12QU7Q3OH',
    '32CXT5U14G4NXDS0WI2V5O2QSF5U8C',
    '3L2OEKSTW9B4EMC56JZK8983O3GY8E',
    '3TTPFEFXCTLVOD3S34YY2VH9SCDH6C',
    '3IZPORCT1FAOAW1CVS1WDQ85OZRRHK',
    '31KSVEGZ34T67MW1QRNWETIS3N4WRP'
]'''

'''HITIds = [
    '3IH9TRB0FB00DMDF3G427BR7KEDI19'
]'''

HITIds = [
    #'3X4Q1O9UBHNOKU3KQRYGSIE6Z9C7OQ',
    '3M67TQBQQHP3W9XCV5RI5JL75IWA96',
    '3YZ7A3YHR5UOVIHU9F0SE3AB5SK5S6',
    '3L55D8AUFAY6QP2INVFPAV4MEU2CYZ',
    '3JAOYN9IHL3HXM9B5HBYRY4FZGU33M',
    '39O0SQZVJN8RH7V0IJFKMDJBAWW7RZ',
    '3IHWR4LC7DEIOMX021DHMLEFYKJI8T',
    '3OYHVNTV5TZCF9A49LNPWNJS5TCKO9',
    '3YD0MU1NC22ZIQ9JG8TYRNU1AS8A7U',
    '3G4VVJO6PZHU09M5OL04LNOIFY8KPQ',
    '34OWYT6U3WII2RGA7TJVMH9QIQ1I9I'
]
    
total = 0
avg_time = 0
all_durations = []

worker_dict = {}

for hit in HITIds:

    response = client.list_assignments_for_hit(
        #HITId='3VMHWJRYHVHOTWWI91I47CDPUQBFXB',
        HITId=hit,
        MaxResults=10,
        AssignmentStatuses=[
            'Submitted',
        ]
    )
    #print(response)
    #print()
    #print("---")
    #print()
    total += int(response['NumResults'])

    print("HIT: " + hit)

    #print(response)
    duration_arr = []

    for assignment in response['Assignments']:
        #print("Assignment: ")
        #print(assignment['AssignmentId'], assignment['WorkerId'], assignment['HITId'])
        #print(assignment['AcceptTime'], assignment['SubmitTime'])

        duration = ( assignment['SubmitTime'].timestamp() - assignment['AcceptTime'].timestamp() ) / 60
        duration_arr.append(duration)
        all_durations.append(duration)
        #print(duration)
        avg_time += duration

        answer_obj = {}

        root = ET.fromstring(assignment['Answer'])
        print(root.tag)
        for child in root:
            key = ''
            for sub in child:
                if 'QuestionIdentifier' in sub.tag:
                    key = sub.text
                if 'FreeText' in sub.tag:
                    answer_obj[key] = sub.text

        #print(answer_obj)

        bonus_earned = False
        print(float(answer_obj['earnings']))
        if float(answer_obj['earnings']) > 0.3:
            bonus_earned = True

        if assignment['WorkerId'] in worker_dict:
            worker_dict[assignment['WorkerId']].append({
                "AssignmentId": assignment['AssignmentId'],
                "Duration": duration,
                "Bonus": bonus_earned,
                "AnswerObj": answer_obj
                })
        else:
            worker_dict[assignment['WorkerId']] = []
            worker_dict[assignment['WorkerId']].append({
                "AssignmentId": assignment['AssignmentId'],
                "Duration": duration,
                "Bonus": bonus_earned,
                "AnswerObj": answer_obj
                })

    print(duration_arr)

print("Total so far: " + str(total)) # Need 30
print("Average time per HIT: " + str(avg_time/total))
all_durations = np.array(all_durations)
all_durations_sorted = np.sort(all_durations)
print(all_durations_sorted)

print()

#for key, value in worker_dict.items():
#    print(key, value)


import plotly.graph_objects as go

indices = []

for i in range(len(all_durations_sorted)):
    indices.append(i+1)

fig0 = go.Figure()
fig0.add_trace(go.Bar(
    x=indices,
    y=all_durations_sorted,
    name='Distribution of assignment durations',
    #marker_color=ED_color
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig0.update_layout(barmode='group', 
                  xaxis_tickangle=-45, 
                  #xaxis={'categoryorder':'total descending'},
                  font = {'family': "Times", 'size': 16, 'color': "Black"},
                  xaxis_title="Assignment",
                  yaxis_title="Assignment durations in minutes",)
fig0.show()



fig1 = go.Figure(data=[go.Histogram(x=all_durations_sorted)])
fig1.update_layout(
    xaxis_title="Assignment duration",
    yaxis_title="No. of assignments",
    font = {'family': "Times", 'size': 16, 'color': "Black"},
    )
fig1.show()

fig2 = go.Figure(data=[go.Histogram(x=all_durations_sorted, cumulative_enabled=True)])
fig2.update_layout(
    xaxis_title="Assignment duration",
    yaxis_title="Cumulative no. of assignments",
    font = {'family': "Times", 'size': 16, 'color': "Black"},
    )
fig2.show()


worker_ids = list(worker_dict.keys())
hit_count_per_worker = []
avg_duration = []
bonus_hits = []
for key, value in worker_dict.items():
    hit_count_per_worker.append(len(value))
    tot_duration = 0
    bonus = 0
    for i in range(len(value)):
        tot_duration += value[i]['Duration']
        if value[i]['Bonus'] == True:
            bonus += 1
    bonus_hits.append(bonus)
    avg_duration.append((tot_duration/len(value)))

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=worker_ids,
    y=hit_count_per_worker,
    name='Hit count per worker',
    #marker_color=ED_color
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig3.update_layout(barmode='group', 
                  xaxis_tickangle=-45, 
                  #xaxis={'categoryorder':'total descending'},
                  font = {'family': "Times", 'size': 16, 'color': "Black"},
                  xaxis_title="WorkerID",
                  yaxis_title="No. of HITs submitted",
                  #xaxis={'categoryorder':'total ascending'}
                  )
fig3.show()


fig4 = go.Figure()
fig4.add_trace(go.Bar(
    x=worker_ids,
    y=avg_duration,
    name='Average duration per worker',
    #marker_color=ED_color
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig4.update_layout(barmode='group', 
                  xaxis_tickangle=-45, 
                  #xaxis={'categoryorder':'total descending'},
                  font = {'family': "Times", 'size': 16, 'color': "Black"},
                  xaxis_title="WorkerID",
                  yaxis_title="Average time taken per HIT",
                  #xaxis={'categoryorder':'total ascending'}
                  )
fig4.show()


fig5 = go.Figure()
fig5.add_trace(go.Bar(
    x=worker_ids,
    y=bonus_hits,
    name='Bonus hits per worker',
    #marker_color=ED_color
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig5.update_layout(barmode='group', 
                  xaxis_tickangle=-45, 
                  #xaxis={'categoryorder':'total descending'},
                  font = {'family': "Times", 'size': 16, 'color': "Black"},
                  xaxis_title="WorkerID",
                  yaxis_title="Number of bonus HITs",
                  #xaxis={'categoryorder':'total ascending'}
                  )
fig5.show()


'''response = client.get_assignment(
    AssignmentId='3CPLWGV3MO0C2CPVUB04NYVWS7O9NW'
)

print(response)'''
