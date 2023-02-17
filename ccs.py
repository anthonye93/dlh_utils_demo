import pandas as pd
import numpy as np
import random
from faker import Faker

random.seed(42)
np.random.seed(42)
Faker.seed(42)  # toggle based on faker version
fake = Faker('en_UK')
#fake.seed(42)

import string

# overall missingness in string variables and typo prevalence
GEN_MISS = .04
GEN_TYPO = .03

df_people = pd.read_csv('dlh_utils_demo/ccs_residents.csv')

#############
### creating ccs records with new id's
#############

def CCS_scramble(df_people):
    df_people2 = df_people.copy()
    df_people2['Resident_ID'] = ['c'+str(x) for x in random.sample(range(10 ** 18, 2**63-1), df_people2.shape[0])]
    return df_people2
  
#Scramble IDs
df_people = CCS_scramble(df_people)

#Drop random records
drop_df = df_people.sample(n = 5)
df_people = pd.concat([df_people,drop_df]).drop_duplicates(keep = False)


#############
### Extra functionality
#############

def create_duplicates(df, num=50, change_house=False, twin=True):
    subset = df.iloc[random.sample(range(df.shape[0]), num)].copy().reindex()
    subset['Resident_ID'] = ['c'+ str(x) for x in random.sample(range(10 ** 18, ((10 ** 19) - 1)), num)]
    if twin:
        subset['ENUM_FNAME'] = random.sample(df.ENUM_FNAME.tolist(), num)
    return df.append(subset)

# apply create duplicates function to create 50 twins
df_people = create_duplicates(df_people)

# just duplicates
df_people = create_duplicates(df_people, twin = False)

# group by last_name column and transform (filter) for where the number of occurences of last name > 1
grouped_last_name_counts = df_people[df_people['ENUM_SNAME'].groupby(df_people['ENUM_SNAME']).transform('size') > 1]['ENUM_SNAME']

# convert from series to df for merge
twin_check = grouped_last_name_counts.to_frame()

#  merge to get first name and sex variables for where last_name > 1
twin_check.merge(df_people, on = 'ENUM_SNAME', how = 'inner')[['ENUM_FNAME', 'ENUM_SNAME', 'Sex']]
  
###############
# pertubations as listed in delivery 2.1
###############

def simple_typos(word):
    ix = random.choice(range(len(word)))
    new_word = ''.join([word[w] if w != ix else word[w] + random.choice(string.digits + string.ascii_uppercase + '/\,.-?'*3) for w in range(len(word))])
    return new_word

def randomcase(string):
  
  result = '' # empty to start with
  
  for char in string:
    
    case = random.choices(['0','1'], [0.1, 0.9]) # upper/lowercase flag

    if case == ['0']:
      result += char.upper()
      
    else:
      result += char.lower()
      
  return result

def pertubation21(ccs_people):
    # for each variable, first we replace some completely

    subset = np.random.choice([True, False], size=ccs_people.shape[0], p=[.20, 1-.20])
    ccs_people.loc[subset,'ENUM_FNAME'] = random.sample(ccs_people.ENUM_FNAME.tolist(), sum(subset))

    subset = np.random.choice([True, False], size=ccs_people.shape[0], p=[.20, 1-.20])
    ccs_people.loc[subset,'ENUM_SNAME'] = random.sample(ccs_people.ENUM_SNAME.tolist(), sum(subset))

    subset = np.random.choice([True, False], size=ccs_people.shape[0], p=[.02, 1-.02])
    ccs_people.loc[subset,'Sex'] = random.sample(ccs_people.Sex.tolist(), sum(subset))

    subset = np.random.choice([True, False], size=ccs_people.shape[0], p=[.20, 1-.20])
    ccs_people.loc[subset,'Address'] = random.sample(ccs_people.Address.tolist(), sum(subset))
    
    subset = np.random.choice([True, False], size=ccs_people.shape[0], p=[.20, 1-.20])
    ccs_people.loc[subset,'Postcode'] = random.sample(ccs_people.Postcode.tolist(), sum(subset))
    
    subset = np.random.choice([True, False], size=ccs_people.shape[0], p=[.15, 1-.15])
    ccs_people.loc[subset,'DOB'] = random.sample(ccs_people.DOB.tolist(), sum(subset))
    
    return ccs_people
  

def addwhitespace(ccs_people):
  for column in ccs_people.columns:
    if column in ['ENUM_FNAME', 'ENUM_SNAME', 'Address', 'Postcode']:
     
      subset = ccs_people.sample(frac=0.02, random_state=1).index
      ccs_people.loc[subset, column] = ccs_people.loc[subset, column] + " "

      subset = ccs_people.sample(frac=0.02, random_state=2).index
      ccs_people.loc[subset, column] = ccs_people.loc[subset, column] + "  "

      subset = ccs_people.sample(frac=0.02, random_state=3).index
      ccs_people.loc[subset, column] = " " + ccs_people.loc[subset, column]

      subset = ccs_people.sample(frac=0.02, random_state=4).index
      ccs_people.loc[subset, column] = "  " + ccs_people.loc[subset, column]
      
  return ccs_people

df_people = addwhitespace(df_people)

def add_missing_codes_to_some(ccs_people):
    # introduce missingness and typos on both sides

    for column in ccs_people.columns:
      if column not in ['Resident_ID', 'Resident_Day_Of_Birth', 'Resident_Month_Of_Birth',
                        'Resident_Year_Of_Birth','Resident_Age', 'DOB', 'Sex']:
        print(column)
        subset = np.random.choice([True, False], size=ccs_people.shape[0], p=[3*GEN_TYPO, 1-3*GEN_TYPO])
        ccs_people.loc[subset,column] = ccs_people.loc[subset,column].transform(simple_typos)

        subset = np.random.choice([True, False], size=ccs_people.shape[0], p=[3*GEN_TYPO, 1-3*GEN_TYPO])
        ccs_people.loc[subset,column] = ccs_people.loc[subset,column].transform(randomcase)
      
      if column not in ['Resident_ID']:

        subset = np.random.choice([True, False], size=ccs_people.shape[0], p=[GEN_MISS, 1 - GEN_MISS])
        ccs_people.loc[subset, column] = np.random.choice(['-9', '-7'])

    return ccs_people

df_people = add_missing_codes_to_some(df_people)
df_people = pertubation21(df_people)

# change date type for ccs
df_people['DOB'] = df_people['DOB'].str.replace('/', '-')

## replace newline characters with spaces - may leave in as standardisation procedure
# list of all string type columns
#string_columns = [x for x in df_people.columns if df_people[x].dtype == object]
#for column in string_columns:
#  df_people[column] = df_people[column].str.replace('\n',' ')


df_people = df_people.drop(['Resident_Month_Of_Birth','Resident_Day_Of_Birth'], axis = 1) # perturbations done on day/mon/year birth, so will have to recreate full_dob in course

df_people.to_csv('dlh_utils_demo/ccs_perturbed.csv', index = False)
