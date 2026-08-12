#!/usr/bin/env python
import json
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import JSON
import boto3

os.chdir("/home/afaq/learning/learning-de/projects/finance-de-projects/financial-statements-pipeline")

with open('ingestion/config.json', 'r') as f:
    config = json.load(f)

# old code
# data = None
# with open('ingestion/saved-json-responses/good-quality/perthshire.json', 'r') as file:
#     data = json.load(file)

def process_and_upload_file_data(data):

    def flatten_dict(d, prefix=''):
        result = {}
        for key, value in d.items():
            new_key = f"{prefix}_{key}" if prefix else key

            if isinstance(value, dict):
                result.update(flatten_dict(value, new_key))
            elif isinstance(value, list):
                result[new_key] = flatten_list(value)
            else:
                result[new_key] = value
        return result

    def flatten_list(lst):
        result = []
        for item in lst:
            if isinstance(item, dict):
                result.append(flatten_dict(item))
            elif isinstance(item, list):
                result.append(flatten_list(item))
            else:
                result.append(item)
        return result

    # BREAK INTO TABLES (profile, financials, officers, psc)
    financials = data['financials']
    profile = data['profile']

    sic_codes = profile['sic_codes']
    for sic_code_obj in sic_codes:
        sic_code_obj['company_number'] = profile['company_number']

    financials = (flatten_dict(financials))['company_financial_list']
    for finance_obj in financials:
        finance_obj['company_number'] = profile['company_number']

    psc = data['psc']
    psc = [flatten_dict(p) for p in data['psc']]
    for p in psc:
        p['company_number'] = profile['company_number']

    # Break profile
    profile_df = pd.DataFrame([profile])

    # Break financials
    financials_df = pd.DataFrame(financials)

    # Break PSC
    psc_df = pd.DataFrame(psc)

    # CLEAN
    financials_df = financials_df.astype('str')

    def rename_columns(config_columns, dataframe):
        for key in config_columns.keys():
            sub_keys = config_columns[key].keys()
            for s_key in sub_keys:
                if key == '_root':
                    flattened_df_col_name = s_key
                else:
                    flattened_df_col_name = f"{key}_{s_key}"

                target_col_name = config_columns[key][s_key]

                if flattened_df_col_name in dataframe.columns:
                    dataframe.rename(columns={flattened_df_col_name: target_col_name}, inplace=True)
                else:
                    print(f"Warning: Column '{flattened_df_col_name}' not found in DataFrame")
        return dataframe

    conf_finance_df_cols = config['tables']['finance_statements']['columns']
    financials_df = rename_columns(conf_finance_df_cols, financials_df)

    conf_profiles_df_cols = config['tables']['profiles']['columns']
    profile_df = rename_columns(conf_profiles_df_cols, profile_df)

    conf_psc_df_cols = config['tables']['psc']['columns']
    psc_df = rename_columns(conf_psc_df_cols, psc_df)

    # PUSH CLEANED tables data into database
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")

    config_tables = config['tables']
    financials_df['loaded_at'] = pd.Timestamp('now', tz='utc')
    financials_df.to_sql(config_tables['finance_statements']['db_table_name'], engine, index=False, schema='finance_companies', if_exists='append')

    config_tables = config['tables']
    profile_df['loaded_at'] = pd.Timestamp('now', tz='utc')
    profile_df.to_sql(config_tables['profiles']['db_table_name'], engine, index=False, schema='finance_companies', if_exists='append', dtype={
        "sic_codes": JSON,
        "registered_office_address": JSON
    })

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

s3_resource = boto3.resource('s3')
bucket_name = 'company-register-json-filings'
bucket = s3_resource.Bucket(bucket_name)

for obj in bucket.objects.all():
    s3_key = obj.key
    print(f"Processing: {s3_key}")
    obj = s3_resource.Object(bucket_name, s3_key)
    content = obj.get()['Body'].read().decode('utf-8')
    data = json.loads(content)
    process_and_upload_file_data(data)
    obj.delete()
    print(f"Deleted: {s3_key}")