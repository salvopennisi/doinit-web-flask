import numpy as np
import pandas as pd 

def calculate_proximity_score( distance, max_score = 40):
        return max_score * (1 - 0.15) ** (distance / 100)

def calculate_bz_interest_score( n_common_business_interest, max_score= 25):
    #bz_interest = set(table_bz_insterests) & set(user_businessInterests)
    if n_common_business_interest > 1:
        divisor = max_score * 0.25
        dividend = (1 + np.exp(-1 * (n_common_business_interest - 1)))
        return max_score * 0.75 + (divisor / dividend)
    else:
        return max_score * 0.75 * n_common_business_interest

def calculate_skills_score( skills_distinct_sum, n_common_skills, max_score=20):
    # merged_skill = set(user_skills) & set(table_skills) #comuni
    # sum_skill = set(user_skills).union(table_skills) #somma_distinct
    return -(max_score /skills_distinct_sum) * n_common_skills + max_score

def calculate_hobbies_score( distinct_hobbies_sum, n_common_hobbies, max_score=15):
    # merged_hobby = set(user_hobbies) & set(table_hobbies)
    # sum_hobbies = set(user_hobbies).union(table_hobbies)
    return (max_score / distinct_hobbies_sum) * n_common_hobbies



def execute_calculate_proximity_score(max_distance):
    data = []
    for i in range(0,max_distance,100):
        y = calculate_proximity_score(i)
        row  = {'distance':i, 'proximityScore':y}
        data.append(row)
    return data

def execute_calculate_bz_interest_score(max_n_bz_int):
    data = []
    for i in range(0,max_n_bz_int):
        y = calculate_bz_interest_score(i)
        row  = {'n_common_business_interest':i, 'businessInterestsScore':y}
        data.append(row)
    return data


def execute_calculate_skills_score(max_n_skills):
    data = []
    for i in range(2,max_n_skills):
        for z in range(0,(i+1)):
            y = calculate_skills_score(i,z)
            row  = {'skills_distinct_sum':i, 'common_skills':z,'skillsScore':y}
            data.append(row)
    return data


def execute_calculate_hobbies_score(max_n_hobbies):
    data = []
    for i in range(2,max_n_hobbies):
        for z in range(0,(i+1)):
            y = calculate_hobbies_score(i,z)
            row  = {'hobbies_distinct_sum':i, 'common_hobbies':z,'hobbiesScore':y}
            data.append(row)
    return data



def simulate_total_scores(max_distance,max_n_hobbies, max_n_skills, max_n_bz_int):
    proximity = pd.DataFrame(execute_calculate_proximity_score(max_distance))
    bzScore =   pd.DataFrame(execute_calculate_bz_interest_score(max_n_bz_int))
    skill =     pd.DataFrame(execute_calculate_skills_score(max_n_skills))
    hobbies =   pd.DataFrame(execute_calculate_hobbies_score(max_n_hobbies))
    result = proximity.merge(bzScore, how='cross').merge(skill, how='cross').merge(hobbies, how='cross')
    scores = ['proximityScore','businessInterestsScore','skillsScore', 'hobbiesScore']
    moved_columns = result[scores]
    remaining_columns = result.drop(columns=scores)
    df_reordered = pd.concat([remaining_columns, moved_columns], axis=1)
    df_reordered['total_score'] = df_reordered[scores].sum(axis=1)
    data = df_reordered.sort_values(by='total_score')
    data = data.round(2)
    data.to_csv('analisi_simulazione_scores.csv', header=True, sep=';', index=False, decimal=',')

simulate_total_scores(500,5,6,6)
# print(len(set(['a','b'])&set(['e','c']))) 
# print(len(set(['a','b']).union(['a','c']))) 