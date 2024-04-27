import numpy as np

class ScoreCalculator:
    def __init__(self
                 , max_score_proximity=40
                 , max_score_bz_interest=20
                 , max_score_bz_exp=20
                 , max_score_skills=15
                 , max_score_hobbies=5
                 , coefficient_score_proximity=0.15
                 , increment_distance_proximity=50,
                  ):
        self.max_score_proximity = max_score_proximity
        self.coefficient_score_proximity = coefficient_score_proximity
        self.increment_distance_proximity = increment_distance_proximity
        self.max_score_bz_interest = max_score_bz_interest
        self.max_score_bz_exp = max_score_bz_exp
        self.max_score_skills = max_score_skills
        self.max_score_hobbies = max_score_hobbies

    def calculate_proximity_score(self, distance):
        return self.max_score_proximity * (1 - self.coefficient_score_proximity) ** (distance / self.increment_distance_proximity)

    def calculate_bz_interest_score(self, user_businessInterests, table_bz_insterests):
        bz_interest = set(table_bz_insterests) & set(user_businessInterests)
        if len(bz_interest) > 1:
            divisor = self.max_score_bz_interest * 0.25
            dividend = (1 + np.exp(-1 * (len(bz_interest) - 1)))
            return self.max_score_bz_interest * 0.75 + (divisor / dividend)
        else:
            return self.max_score_bz_interest * 0.75 * len(bz_interest)
    
    def calculate_bz_exp_score(self, user_businessInterests, table_business_exp, table_bz_insterests):
        experiencesRelatedToUserInterests = set(user_businessInterests) & set (table_business_exp)
        experiencesRelatedToCommonInterests = experiencesRelatedToUserInterests & set(table_bz_insterests)
        if len(experiencesRelatedToCommonInterests) > 0:
            score = self.max_score_bz_exp
        elif len(experiencesRelatedToUserInterests) > 0:
            score = self.max_score_bz_exp * 0.70
        elif len(set(table_business_exp)) > 0:
            score = self.max_score_bz_exp * 0.5
        else:
            score = 0
        return score

    def calculate_skills_score(self, user_skills, table_skills):
        merged_skill = set(user_skills) & set(table_skills)
        sum_skill = set(user_skills).union(table_skills)
        return -(self.max_score_skills / len(sum_skill)) * len(merged_skill) + self.max_score_skills

    def calculate_hobbies_score(self, user_hobbies, table_hobbies):
        merged_hobby = set(user_hobbies) & set(table_hobbies)
        sum_hobbies = set(user_hobbies).union(table_hobbies)
        return (self.max_score_hobbies / len(sum_hobbies)) * len(merged_hobby)

    def calculate_total_score(self, df, score_columns:list):
        df['total_score'] = df[score_columns].sum(axis=1)
        return df