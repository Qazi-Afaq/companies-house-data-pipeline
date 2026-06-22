#!/usr/bin/env python
# coding: utf-8

# # import libraries

# In[ ]:





# In[1]:


import json
import os
import pandas as pd

os.chdir("/home/afaq/learning/learning-de/projects/finance-de-projects/financial-statements-pipeline")

with open('ingestion/config.json', 'r') as f:
    config = json.load(f)


# # LOAD files via s3 or local

# In[2]:


data = None
with open('ingestion/saved-json-responses/good-quality/aranci-advisors.json', 'r') as file:
    data = json.load(file)


# In[3]:


data


# In[4]:


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

# In[5]:


financials = data['financials']
profile = data['profile']
sic_codes = profile['sic_codes']
for sic_code_obj in sic_codes:
    sic_code_obj['company_number'] = profile['company_number']
financials = (flatten_dict(financials))['company_financial_list']
for finance_obj in financials:
    finance_obj['company_number'] = profile['company_number']


# # Break profile 

# In[6]:


profile_df = pd.DataFrame([profile])


# In[7]:


profile_df


# In[8]:


profile_df.head()


# # Break financials

# In[9]:


financials_df = pd.DataFrame(financials)


# In[10]:


financials_df


# In[11]:


financials_df.columns


# # Break officers

# In[12]:


# officers_df = pd.DataFrame(officers)


# In[13]:


# officers_df


# # Break PSC

# In[14]:


# psc_df = pd.DataFrame(psc)


# In[15]:


# psc_df


# ## CLEAN

# #### Convert to required data-types

# In[16]:


config_tables = config['tables']
def clean_dataframe(df_table_name , df , table_obj):
    config_columns = table_obj[df_table_name]['columns']
    df_columns = df.columns
    for col in df_columns:
        config_col_obj = config_columns[col]
        conf_col_source_prefix = config_col_obj.get('source_prefix')
        conf_col_source_name = config_col_obj.get('source_name')
        conf_col_type = config_col_obj.get('type')


        if conf_col_type == 'float64':
            # before applying conversion
            col_null_count_before = len(df[df[col].isna()])
            df[col] = pd.to_numeric(df[col] , errors='coerce')
            df[col] = df[col].astype('float64')
            # after applying conversion
            col_null_count_after = len(df[df[col].isna()])


        elif conf_col_type == 'string':
            df[col] = df[col].astype('string')

        elif conf_col_type == 'datetime64[ns]':
            df[col] = pd.to_datetime(df[col] , errors='coerce' , dayfirst=True).dt.date

        # output each column's before-after nulls for stats

clean_dataframe('finance_statements', financials_df, config_tables)
clean_dataframe('profiles' , profile_df , config_tables)


# #### RENAME COLUMNS TO AVOID TRUNCATION IN DATABASE (50 characters or less)

# In[17]:


config_tables = config['tables']
def rename_cols_for_db(df_table_name , df , conf_table_obj):
    config_columns = conf_table_obj[df_table_name]['columns']
    for col in df.columns:
        conf_curr_col_obj = config_columns[col]
        db_column_name = conf_curr_col_obj.get('db_column')
        if db_column_name:
            df.rename(columns={col:db_column_name} , inplace=True)

rename_cols_for_db('finance_statements' , financials_df , config_tables)
rename_cols_for_db('profiles' , profile_df , config_tables)


# In[18]:


financials_df.columns


# In[19]:


# the columns of dataframes must have same length of the config number of columns: if not then: fail execution
config_tables = config['tables']
conf_financials_df_len = len(config_tables['finance_statements']['columns'].keys())
conf_financials_df_len = (conf_financials_df_len -1) if 'index' in financials_df.columns else conf_financials_df_len
conf_profiles_df_len = len(config_tables['profiles']['columns'].keys())
conf_profiles_df_len = (conf_profiles_df_len -1) if 'index' in profile_df.columns else conf_profiles_df_len

print(conf_financials_df_len , len(financials_df.columns))
print(conf_profiles_df_len , len(profile_df.columns))
if (conf_financials_df_len != len(financials_df.columns)) or (conf_profiles_df_len != len(profile_df.columns)):
    raise KeyError('UNEXPECTED COLUMNS FOUND IN DATAFRAMES')


# # PUSH CLEANED tables data into database

# In[20]:


from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")


# In[22]:


config_tables = config['tables']
financials_df['loaded_at'] = pd.Timestamp('now', tz='utc')
financials_df.to_sql(config_tables['finance_statements']['db_table_name'] , engine , index=False , schema='finance_companies', if_exists='replace')


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





# In[ ]:




