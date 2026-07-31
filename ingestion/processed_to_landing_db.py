#!/usr/bin/env python
# coding: utf-8

# # import libraries

# In[ ]:


import json
import os
import pandas as pd

os.chdir("/home/afaq/learning/learning-de/projects/finance-de-projects/financial-statements-pipeline")

with open('ingestion/config.json', 'r') as f:
    config = json.load(f)


# # LOAD files via s3 or local

# In[ ]:





# In[ ]:


data = None
with open('ingestion/saved-json-responses/good-quality/perthshire.json', 'r') as file:
    data = json.load(file)


# In[ ]:


data


# In[ ]:


def flatten_dict(d, prefix=''):
    result = {}
    for key, value in d.items():
        new_key = f"{prefix}_{key}" if prefix else key

        if isinstance(value, dict):
            # Recurse and merge the flattened sub-dict into result
            result.update(flatten_dict(value, new_key))

        elif isinstance(value, list):
            # Keep the list, but flatten any dicts inside it
            result[new_key] = flatten_list(value)

        else:
            # Primitive: just assign
            result[new_key] = value

    return result


def flatten_list(lst):
    result = []
    for item in lst:
        if isinstance(item, dict):
            # Flatten the dict, but don't hoist it into the parent — keep it in the list
            result.append(flatten_dict(item))
        elif isinstance(item, list):
            result.append(flatten_list(item))
        else:
            # Primitive: leave as-is
            result.append(item)
    return result


# answer = flatten_dict(my_dict)
# answer


# # BREAK into tables(profile , financials , officers , psc)

# In[ ]:


financials = data['financials']
profile = data['profile']
sic_codes = profile['sic_codes']
for sic_code_obj in sic_codes:
    sic_code_obj['company_number'] = profile['company_number']
financials = (flatten_dict(financials))['company_financial_list']
for finance_obj in financials:
    finance_obj['company_number'] = profile['company_number']


# PSC
psc = data['psc']
psc = [flatten_dict(p) for p in data['psc']]
for p in psc:
    p['company_number'] = profile['company_number']


# # Break profile 

# In[ ]:


profile_df = pd.DataFrame([profile])


# In[ ]:


profile_df


# In[ ]:


profile_df.head()


# # Break financials

# In[ ]:


financials_df = pd.DataFrame(financials)


# In[ ]:


financials_df


# In[ ]:


financials_df.columns


# # Break officers

# In[ ]:


# officers_df = pd.DataFrame(officers)


# In[ ]:


# officers_df


# # Break PSC

# In[ ]:


psc_df = pd.DataFrame(psc)


# In[ ]:


psc_df


# ## CLEAN

# In[ ]:


# cast all columns to string
financials_df = financials_df.astype('str')


# #### VERIFY NUMBER OF COLUMNS IN THE DATAFRAME ARE EXPECTED USING CONFIG.JSON

# In[ ]:


# the columns of dataframes must have same length of the config number of columns: if not then: fail execution
config_tables = config['tables']
# LATER


# #### REPLACE COLUMN NAMES TO AVOID NAME TRUNCATION IN DATABASE

# In[ ]:


def rename_columns(config_columns, dataframe):
    """
    Flatten nested config column structure and rename dataframe columns accordingly.

    Args:
        config_columns: Nested dictionary from config['tables'][table_name]['columns']
        dataframe: pandas DataFrame to rename columns in

    Returns:
        Renamed DataFrame (modified in-place)
    """
    for key in config_columns.keys():
        sub_keys = config_columns[key].keys()
        for s_key in sub_keys:
            # Construct flattened column name
            if key == '_root':
                flattened_df_col_name = s_key
            else:
                flattened_df_col_name = f"{key}_{s_key}"

            # Get the target column name from config
            target_col_name = config_columns[key][s_key]

            # Rename if column exists
            if flattened_df_col_name in dataframe.columns:
                dataframe.rename(columns={flattened_df_col_name: target_col_name}, inplace=True)
            else:
                print(f"Warning: Column '{flattened_df_col_name}' not found in DataFrame")

    return dataframe

# Usage for finance_statements
print("FINANCIALS RENAMING START: =====================================")
conf_finance_df_cols = config['tables']['finance_statements']['columns']
financials_df = rename_columns(conf_finance_df_cols, financials_df)

# Usage for profiles
print("PROFILES RENAMING START: =====================================")
conf_profiles_df_cols = config['tables']['profiles']['columns']
profile_df = rename_columns(conf_profiles_df_cols, profile_df)

print("PSC RENAMING START: =====================================")
# Usage for psc
conf_psc_df_cols = config['tables']['psc']['columns']
psc_df = rename_columns(conf_psc_df_cols , psc_df)


# # PUSH CLEANED tables data into database

# In[ ]:


from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")


# In[ ]:


config_tables = config['tables']
financials_df['loaded_at'] = pd.Timestamp('now', tz='utc')
financials_df.to_sql(config_tables['finance_statements']['db_table_name'] , engine , index=False , schema='finance_companies', if_exists='append')


# In[ ]:


# with open('data2.json' , 'w') as f:
#     json.dump(profile , f)


# In[ ]:


from sqlalchemy.types import JSON
config_tables = config['tables']
profile_df['loaded_at'] = pd.Timestamp('now', tz='utc')
profile_df.to_sql(config_tables['profiles']['db_table_name'] , engine , index=False, schema='finance_companies' , if_exists='append' ,  dtype={
        "sic_codes": JSON,
        "registered_office_address": JSON
    }) 


# In[ ]:


from sqlalchemy.types import JSON

config_tables = config['tables']
psc_df['loaded_at'] = pd.Timestamp('now', tz='utc')

psc_df.to_sql(
    config_tables['psc']['db_table_name'],
    engine,
    index=False,
    schema='finance_companies',
    if_exists='append',
    dtype={"natures_of_control": JSON}
)


# In[ ]:




