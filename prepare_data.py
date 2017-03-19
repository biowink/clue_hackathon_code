from os.path import join as pj
import os
import pandas as pd
import numpy as np

base_dir = os.path.dirname(__file__)
data_dir = pj(base_dir, 'data')

# ====================== Import data ======================
active_days = pd.read_csv(pj(data_dir, 'active_days.csv'), parse_dates=['date'])
users = pd.read_csv(pj(data_dir, 'users.csv'))

cycles = pd.read_csv(pj(data_dir, 'cycles.csv'), parse_dates=['cycle_start'])
cycles0 = pd.read_csv(pj(data_dir, 'cycles0.csv'), parse_dates=['cycle_start'])

# Train on this
tracking = pd.read_csv(pj(data_dir, 'tracking.csv'), parse_dates=['date'])
# Test on this
tracking_test = pd.read_csv(pj(data_dir, 'labels.csv'))


# ================  Feature engineer a user ================
symptoms_of_interest = [
    'happy', 'pms', 'sad', 'sensitive_emotion',
    'energized', 'exhausted', 'high_energy', 'low_energy',
    'cramps', 'headache', 'ovulation_pain', 'tender_breasts',
    'acne_skin', 'good_skin', 'oily_skin', 'dry_skin'
]

other_symptoms = set(tracking.symptom.unique()) - set(symptoms_of_interest)
ordered_symptoms = {s:i for i, s in enumerate(symptoms_of_interest + list(other_symptoms))}
N_symptoms = len(ordered_symptoms)

tracking['symptom_code'] = tracking.symptom.map(lambda s: ordered_symptoms[s])


def transform_user(user_id):
    out = tracking[tracking.user_id == user_id]
    out.loc[:, 'absolute_day'] = (out.date.dt.date - out.date.dt.date.min()).dt.days + 1
    out = pd.merge(out, cycles[cycles.user_id == user_id], on=["cycle_id", "user_id"])

    out_sequence = np.zeros(
        (
            out.absolute_day.max(),
            N_symptoms
        )
    )

    for _, row in out.iterrows():
        out_sequence[row['absolute_day'] - 1, row['symptom_code']] = 1
    return out, out_sequence
