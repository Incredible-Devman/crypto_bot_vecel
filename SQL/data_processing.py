import pandas as pd
import ast
import io
import chardet
import json
import mysql.connector
import numpy as np
from datetime import datetime

current_time = datetime.now()

current_hour = current_time.hour
current_minute = current_time.minute
current_second = current_time.second


cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='workspace'
)


def add_column():


    for index, row in df.iterrows():
        getitem(index, row['line_items'])
        print(index)

    df.dropna(subset=['Item_Name'], inplace=True)
    
    columns_to_drop = ['note', 'receipt_type', 'refund_for', 'order', 'created_at', 'updated_at', 'source', 'points_deducted', 'cancelled_at', 'dining_option', 'total_discounts', 'total_taxes', 'tip', 'surcharge', 'payments', 'line_items']
    df.drop(columns_to_drop, axis=1, inplace=True)
    
    df.rename(columns={'receipt_date': 'Receipt_date'}, inplace=True)

    df.replace({np.nan: None}, inplace=True)

    cursor = cnx.cursor()

    for _, row in df.iterrows():
        query = "INSERT INTO receipts_8 (receipt_number, Receipt_date, total_money, total_tax, points_earned, points_balance, customer_id, total_discount, employee_id, store_id, pos_device_id, Item_Name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (row['receipt_number'], row['Receipt_date'], row['total_money'], row['total_tax'], row['points_earned'], row['points_balance'], row['customer_id'], row['total_discount'], row['employee_id'], row['store_id'], row['pos_device_id'], row['Item_Name'])
        cursor.execute(query, values)

    cnx.commit()
    cnx.close()

    # df.to_csv('updated_receipts111.csv', index = False)    

def getitem(index, itemContent):
    global df

    item_names = []
    new_rows = []
   

    for dictionary in itemContent:

        item_names.append(dictionary['item_name'])
        item_name = dictionary['item_name']
        
        if item_name != '**Transcation Fee':
            new_row = createrow(index)
            new_row['Item_Name'] = item_name
            new_rows.append(new_row)
            print(item_name)

    # df = df.drop(index=index)
    df = pd.concat([df] + new_rows, ignore_index=True)
    # df.loc[index, 'item_names'] = item_names
       

def createrow(index):
    global df

    row_data = df.loc[index].copy()
    return pd.DataFrame([row_data])
    # df.loc[index, 'item_names'] = item_names    
