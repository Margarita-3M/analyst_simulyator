import pandahouse

def get_df(query):
    '''
    The function returns dataframe based on the defined query from
    our database.
    
    Params:
    - query: SQL query (Clickhouse)
    
    '''
    
    connection = {
        'host': 'https://clickhouse.lab.karpov.courses',
        'password': 'dpo_python_2020',
        'user': 'student',
        'database': 'simulator_20211220'
    }
    
    df = pandahouse.read_clickhouse(query, connection=connection)
    
    return df