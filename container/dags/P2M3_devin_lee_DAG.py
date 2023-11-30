'''
=================================================
Milestone 3

Nama  : Devin Lee
Batch : HCK-09

Script Python pada proses ini berisikan seluruh proses dari loading data, cleaning data, dan memasukan data ke dalam airflow menjadi satu file. Hal ini bertujuan untuk memunculkan data yang sudah di handling kedalama Elasticsearch. Proses ini dilakukan untuk melanjutkan analisa visualisasi di elasticsearch kibana
=================================================
'''

import pandas as pd
import re
from sqlalchemy import create_engine, Table, MetaData
from elasticsearch import Elasticsearch, helpers
import numpy as np
import datetime as dt
from datetime import timedelta
from airflow import DAG
# from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

def loading_data():
    ''' 
    Fungsi ini bertujuan untuk melakukan mendefine data raw yang akan diproses, dimana pemanggilan data raw ini menggunakan SQL Alchemy yang setelahnya data tersebut akan diubah menjadi bentuk CSV.
    '''
    engine = create_engine('postgresql+psycopg2://postgres:postgres@postgres:5432/milestone')
    df = pd.read_sql_table('table_m3', engine)
    df.to_csv('/opt/airflow/dags/P2M3_devin_lee_raw.csv',index=0)

def clean():
    ''' 
    Fungsi ini berisikan seluruh proses cleaning data raw yang sudah diuji pada simulasi cleaning. Dengan menggunakan fungsi ini, data raw yang sudah dilakukan defining akan melewati proses cleaning ini yang akan membuat data menjadi lebih proper. Dengan langkah terakhir yaitu dengan mengexport data yang sudah di cleaning tersebut menjadi data CSV baru.
    '''
    df = pd.read_csv('/opt/airflow/dags/P2M3_devin_lee_raw.csv')
    # Remove numbers and special characters except for spaces and underscores from column names
    df.columns = [re.sub(r'[^a-zA-Z _ ()]', '', col) for col in df.columns]

    # missing value
    df.replace(' ', np.nan, inplace=True)
    df = df.dropna()
    
    # Remove '@!#$%^&*' from the end of each column name
    df.columns = [re.sub(r'@!#$%\^&\*$', '', col) for col in df.columns]
    
    # Convert column names to lowercase
    df.columns = [x.lower() for x in df.columns]

    # Format numbers to two decimal places
    exclude = ['id','long', 'lat']
    formatted_columns = df.drop(columns=exclude).applymap(lambda x: '{:.2f}'.format(x) if isinstance(x, (int, float)) else x)
    df = pd.concat([df[['id']], df[exclude[1:]], formatted_columns], axis=1)
    
    # Raplace name columns
    df.rename(columns={
        "riverdist_(m)": "riverdist_m",
        "faultdist_(m)": "faultdist_m"
    }, inplace=True)

    # Convert Data Types for All Columns
    data_types = {
        'id': 'float64',
        'long': 'float64',
        'lat': 'float64',
        'sub_basin': 'string',
        'elevation': 'float64',
        'landuse_type': 'string',
        'slop(percent)': 'float64',
        'slop(degrees)': 'float64',
        'geo_unit': 'string',
        'des_geouni': 'string',
        'climate_type': 'string',
        'des_climatetype': 'string'
    }

    # Apply the data types to the DataFrame
    df = df.astype(data_types)

    df.to_csv('/opt/airflow/dags/P2M3_devin_lee_data_clean.csv', index=False)

def clean2():
    '''
    Proses cleaning ini dilakukan secara terpisah karena butuh melakukan proses yang khusus. Dimana proses ini memanggil 3 columns tertentu dengan mengunakan fungsi .iloc, dan mendefined masing-masing columns tersebut untuk dilakukan perubahan type data menggunakan fungsi .astype. 
    '''
    df = pd.read_csv('/opt/airflow/dags/P2M3_devin_lee_data_clean.csv')
        # New types
    col_1 = df.iloc[:,5:8].columns[0]
    col_2 = df.iloc[:,5:8].columns[1]
    col_3 = df.iloc[:,5:8].columns[2]

    df[col_1] = df[col_1].astype(float)
    df[col_2] = df[col_2].astype(float)
    df[col_3] = df[col_3].astype(float)

    df.to_csv('/opt/airflow/dags/P2M3_devin_lee_data_clean.csv', index=False)

def insert_data_to_elasticsearch():
    ''' 
    Fungsi ini adalah untuk membuat suatu index baru yang berisikan file atau data yang sudah di lakukan atau sudah melalui proses cleaning. Pada bagian ini, file yang sudah dicleaning akan dimasukan kedalam index elasticsearch yang nantinya akan dilanjutkan dengan melakukan analisa visualisasi pada kibana.
    '''
    es = Elasticsearch('http://elasticsearch:9200')
    print("Elasticsearch connection:", es.ping())
    
    # Read data from CSV file
    data = pd.read_csv('/opt/airflow/dags/P2M3_devin_lee_data_clean.csv')

    # Prepare bulk data for indexing
    actions = [
        {
            "_op_type": "index",
            "_index": "milestone",
            "_source": row.to_dict()
        }
        for _, row in data.iterrows()
    ]

    # Perform bulk indexing
    response = helpers.bulk(es, actions)
    print("Bulk indexing response:", response)


default_args = {
    'owner': 'devin lee',
    'start_date': dt.datetime(2023, 11, 23),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=1),
}

connect_args = {
    'username': 'postgres',
    'password': 'postgres',
    'database': 'milestone',
    'table_name': 'table_m3'
}

clean_data_args = {
    'data_path': '/opt/airflow/dags/Landslide_Factors_IRAN.csv'
}


with DAG('import_clean_elastic',
         default_args=default_args,
         schedule_interval='30 23 * * *', # Daily at 1130PM UTC // 630AM UTC+7
         catchup=False) as dag:
    
    connect_task = PythonOperator(
        task_id='connect',
        python_callable=loading_data,
        op_kwargs=connect_args
    )

    clean_data_task = PythonOperator(
        task_id='clean_data',
        python_callable=clean,
        op_kwargs=clean_data_args
    )

    clean_data_task2 = PythonOperator(
        task_id='clean_data2',
        python_callable=clean2,
        op_kwargs=clean_data_args
    )

    insertToElastic = PythonOperator(task_id='insert_elastic',
        python_callable=insert_data_to_elasticsearch
    )

    connect_task >> clean_data_task >> clean_data_task2 >> insertToElastic