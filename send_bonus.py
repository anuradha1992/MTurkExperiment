





# for worker_id, assignment_id in zip(worker_ids, assignment_ids):
#     response = mturk.send_bonus(
#         WorkerId=worker_id,
#         BonusAmount='0.1', # <-- Change accordingly!
#         AssignmentId=assignment_id,
#         Reason=reason,
#         UniqueRequestToken=worker_id+'-bonus-01'
#     )
#     print(response)
#     print()