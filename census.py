'''
A script to generate, then perturb synthetic census and CCS data
'''
import pandas as pd
import numpy as np
import random
from faker import Faker

random.seed(41)
np.random.seed(41)
Faker.seed(41)  # toggle based on faker version
fake = Faker('en_UK')

import datetime

#############

def create_row_resident():
  
    sex = ['Female', 'Male', 'M', 'F', '1', '2', '-9', '-7', ' ', 'NAN']
    
    ethnic_groups = ['White',
    'Mixed or multiple ethnic groups',
    'Asian or Asian British',
    'Black, Black British, Carribean or African',
    'Other ethnic group',
     '-9',
     'NAN',
     ' '
    ]
    
    marital_status = ['Married',
                      'Divorced',
                      'Civil partnership',
                      'Single',
                      'NAN',
                      ' '
    ]
    
    output = {"ID": 'c'+str(random.randint(10**18, 2**63-1)),
              'ENUM_FNAME': fake.first_name(),
              'ENUM_SNAME': fake.last_name(),
              'date_time_obj': fake.date_between_dates(date_start=datetime.date(1934, 1, 1),
                                                       date_end=datetime.date(2022, 12, 1)),
              'Address':fake.street_address()+', '+fake.city(),
              'Postcode': fake.postcode(),
              'Sex': "".join(random.choices(sex, [0.2, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05])),
              'Marital_Status': random.choice(marital_status)}
    
    return output

def calculate_age_on_31_12_2022(born):
  today = datetime.date(2022, 12, 31)
  return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def split_DOB(person_index_df):
    person_index_df['Resident_Day_Of_Birth'] = person_index_df.date_time_obj.apply(lambda x: x.day)
    person_index_df['Resident_Month_Of_Birth'] = person_index_df.date_time_obj.apply(lambda x: x.month)
    person_index_df['Resident_Year_Of_Birth'] = person_index_df.date_time_obj.apply(lambda x: x.year)
    person_index_df['Resident_Age'] = person_index_df.date_time_obj.apply(calculate_age_on_31_12_2022)
    person_index_df['DOB'] = person_index_df.date_time_obj.apply(lambda x: x.strftime("%d/%m/%Y"))
    person_index_df = person_index_df.drop('date_time_obj', axis = 1)
    return person_index_df



# create 1 row dictionary list
census = [create_row_resident()]

# append new rows to list of dictionaries
for i in range(100000):
  new_row = create_row_resident()
  census.append(new_row)
  
  if i % 10000 == 0:
    print("iteration", i)
  
# convert list of dicts to df
census_df = pd.DataFrame(census)

# apply DOB derivation function to df
census_df = split_DOB(census_df)

# make sure kids aren't married D:
census_df['Marital_Status'] = np.where(census_df['Resident_Age'] < 18, 'Single' , census_df['Marital_Status'])

# save
census_df.to_csv('dummy_data/census_residents.csv', index = False)

# 1% sample for ccs
ccs = census_df[:1001]

# save
ccs.to_csv('dummy_data/ccs_residents.csv', index = False)
