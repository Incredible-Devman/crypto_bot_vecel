import requests
import mysql.connector
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import schedule
import time

# API_KEY = 'Elydwnko9jqbjpjw6kuct4o6jlnry9aclh9os2rr'
API_KEY = '2yb6sdlnw8o2bv33tgtv9gnmjxlnsok40c077rxve'

url_coinOfTheDay = "https://lunarcrush.com/api3/coinoftheday"

url_coinOfTheDay_info = "https://lunarcrush.com/api3/coinoftheday/info"

url_coins = "https://lunarcrush.com/api3/coins"

url_influences_coins = 'https://lunarcrush.com/api3/coins/influencers'

url_feeds = 'https://lunarcrush.com/api3/feeds'

headers = {
  'Authorization': f'Bearer {API_KEY}'
}

def fetchData(url, headers):
    response = requests.request("GET", url, headers=headers)
    # print("123213", response.text)
    if response.text.find("<!DOC") != -1:
        return None
    result = json.loads(response.text)
    return result

def getCoinOftheDay():
    result = fetchData(url_coinOfTheDay, headers)
    dataType = {
        "name": 'VARCHAR(50)', "symbol": "VARCHAR(50)"
    }
    if result != None:
        saveToSql('coin_of_the_day', [result], dataType)

def getCoinOftheDayInfo():
    result = fetchData(url_coinOfTheDay_info, headers)
    dataType = {
        'id': 'INT NOT NULL',
        'symbol': 'VARCHAR(50)',
        'name': 'VARCHAR(50)',
        'last_cotd': 'DECIMAL(20, 0)'
    }
    if result != None:
        saveToSql('coin_of_the_day_info', result['history'], dataType)

def getCoins(sort = None, limit = None):
    new_url = f'{url_coins}'
    if sort is not None and limit is not None:
        new_url = f'{new_url}?sort={sort}&limit={limit}'
    elif sort is not None:
        new_url = f'{new_url}?sort={sort}'
    elif limit is not None:
        new_url = f'{new_url}?limit={limit}'
    result = fetchData(new_url, headers)
    print("resss", result)
    data = result['data']
    rlt = []
    for item in data:
        for key in list(item):
            if key not in ['id', 's', 'n', 'p', 'p_btc', 'v', 'vr', 'vt', 'cs', 'ms', 'pch', 'pc',
                            'pc7d', 'mc', 'mcr', 'gs', 'ss', 'bl', 'br', 'sp', 'na', 'md',
                            't', 'r', 'yt', 'sv', 'u', 'c', 'sd', 'd', 'acr', 'tc', 'categories', 'chains']:
                item.pop(key)
    dataType = {
        'id': 'INT NOT NULL',
        's': 'VARCHAR(30)',
        'n': 'VARCHAR(30)',
        'p': 'DECIMAL(10, 6)',
        'p_btc': 'DECIMAL(20, 15)',
        'v': 'DECIMAL(15, 2)',
        'vr': 'INT',
        'vt': 'DECIMAL(15, 10)',
        'cs': 'DECIMAL(15, 2)',
        'ms': 'DECIMAL(15, 2)',
        'pch': 'DECIMAL(10, 6)',
        'pc': 'DECIMAL(10, 5)',
        'pc7d': 'DECIMAL(10, 5)',
        'mc': 'DECIMAL(15, 2)',
        'mcr': 'DECIMAL(15, 2)',
        'gs': 'DECIMAL(5, 1)',
        'ss': 'DECIMAL(25, 2)',
        'bl': 'DECIMAL(10, 2)',
        'br': 'DECIMAL(25, 2)',
        'sp': 'DECIMAL(25, 2)',
        'na': 'DECIMAL(25, 2)',
        'md': 'DECIMAL(25, 2)',
        't': 'DECIMAL(25, 2)',
        'r': 'DECIMAL(20, 2)',
        'yt': 'DECIMAL(25, 2)',
        'sv': 'DECIMAL(25, 2)',
        'u': 'DECIMAL(25, 2)',
        'c': 'DECIMAL(25, 2)',
        'sd': 'DECIMAL(5, 2)',
        'd': 'DECIMAL(5, 2)',
        'acr': 'DECIMAL(15, 2)',
        'tc': 'TIMESTAMP',
        'categories': 'VARCHAR(150)',
        'chains': 'VARCHAR(200)',
    }
    saveToSql('coins', data, dataType)

def getInfluenceOfACoin(coin_id):
    new_url = f'https://lunarcrush.com/api3/coins/{coin_id}/influencers'
    result = fetchData(new_url, headers)
    # print("12121212", result['data'])
    dataType = {
        'medium': 'VARCHAR(30)',
        'identifier': 'DECIMAL(30, 0)',
        'volume': 'INT',
        'volume_rank': 'INT',
        'followers': 'DECIMAL(15, 0)',
        'followers_rank': 'INT' ,
        'engagement': 'DECIMAL(15, 0)',
        'engagement_rank': 'INT',
        'influencer_rank': 'INT',
        'weighted_average_rank': 'INT',
        'twitter_screen_name': 'VARCHAR(30)',
        'display_name': 'VARCHAR(30)',
        'profile_image': 'VARCHAR(200)'
    }
    saveToSql('influenceOfcoin', result['data'], dataType)

def getMetaOfACoin(coin_id):

    connection = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        database = 'workspace'
    )
    ids =[]
    cursor = connection.cursor()
    query = "SELECT id FROM coins"
    cursor.execute(query)
    ids = cursor.fetchall()
    # print(ids)
    data = []
    sql_datas = []
    res = ''
    for coin_id in ids:
        new_url = f'https://lunarcrush.com/api3/coins/{coin_id[0]}/meta'
        result = fetchData(new_url, headers)
        if result == None:
            continue
        res += json.dumps(result['data']) + '\n'
        data.append(res)
        print("data",data)
        sql_data = { 'id': result['data']['id'], 'name': result['data']['name'], 'symbol': result['data']['symbol'], 'short_summary': result['data']['short_summary'], 'twitter_link': result['data']['twitter_link'], 'blog_link':result['data']['blog_link'], 'whitepaper_text':result['data']['whitepaper_text'], 'blog_link':result['data']['blog_link']}
        sql_datas.append(sql_data)

    dataType = {
        'id': 'INT',
        'name': 'VARCHAR(50)',
        'symbol': 'VARCHAR(50)',
        'short_summary': 'TEXT',
        'twitter_link': 'VARCHAR(200)',
        'blog_link': 'VARCHAR(200)',
        'whitepaper_text': 'VARCHAR(200)',
    }
    saveToSql('metaOfcoin', sql_datas, dataType)

def getInfluenceOfCoins(order = None):
    new_url = f'{url_influences_coins}'
    if order is not None:
        new_url = f'{new_url}?order={order}'
    result = fetchData(new_url, headers)
    dataType = {
        'medium': 'VARCHAR(50)',
        'identifier': 'INT',
        'volume': 'INT',
        'volume_rank': 'INT' ,
        'followers': 'DECIMAL(15, 0)',
        'followers_rank': 'INT',
        'engagement': 'DECIMAL(10, 0)',
        'engagement_rank': 'INT',
        'influencer_rank': 'INT',
        'weighted_average_rank': 'INT',
        'twitter_screen_name': 'VARCHAR(20)',
        'display_name': 'VARCHAR(100)',
        'profile_image': 'VARCHAR(300)'
    }
    if result != None:
        saveToSql('influenceOfcoins', result['data'], dataType)

def getFeeds():
    result = fetchData(url_feeds, headers)
    dataType = {
        'lunar_id': 'DECIMAL(15, 0)',
        'market': 'VARCHAR(20)',
        'asset_id': 'INT',
        'time_int': 'INT',
        'time': 'TIMESTAMP',
        'symbol': 'VARCHAR(50)',
        'name': 'VARCHAR(100)',
        'type': 'VARCHAR(50)',
        'identifier': 'DECIMAL(30, 0)',
        'url': 'VARCHAR(200)',
        'title': 'VARCHAR(200)',
        'body': 'TEXT',
        'image': 'VARCHAR(200)',
        'display_name': 'VARCHAR(300)',
        'publisher': 'VARCHAR(300)',
        'twitter_screen_name': 'VARCHAR(100)',
        'profile_image': 'VARCHAR(300)',
        'sentiment': 'INT',
        'score': 'DECIMAL(15, 0)'
    }
    if result != None:
        saveToSql('feeds', result['data'], dataType)

def extractAllInformations():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://app.intotheblock.com/category/all?end_offset=500') #https://app.intotheblock.com/category/all?end_offset=20
    driver.implicitly_wait(20)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print("ssss", soup)
    tbody = soup.find_all('div', class_='rt-tbody')
    ext_data = []
    for tbb in tbody:
        trs = tbb.find_all('div', class_='rt-tr-group')
        for tr in trs:
            tds = tr.find_all('div', class_='rt-td')
            td_name = tr.find_all(class_ = 'asset-name')
            td_symbol = tr.find_all(class_ = 'asset-symbol')
            ext_data.append({
                'name': td_name[0].text,
                'symbol': td_symbol[0].text,
                'market_cap': convertNumber(tds[1].text),
                'price': convertNumber(tds[2].text),
                'price_change': convertNumber(tds[3].text),
                'daily_active_addresses_price': convertNumber(tds[6].text[: tds[6].text.find('(') - 1] if tds[6].text.find('(') != -1 else tds[6].text),
                'daily_active_addresses_per': convertNumber(tds[6].text[tds[6].text.find('(') + 1: -1] if tds[6].text.find('(') != -1 else tds[6].text),
                'hodlers_balance_price': convertNumber(tds[8].text[: tds[8].text.find('(') - 1] if tds[8].text.find('(') != -1 else tds[8].text),
                'hodlers_balance_per': convertNumber(tds[8].text[tds[8].text.find('(') + 1: -1] if tds[8].text.find('(') != -1 else tds[8].text),
                'signals': tds[11].text
            })
    dataType = {
        'name': 'VARCHAR(100)',
        'symbol': 'VARCHAR(100)',                
        'market_cap': 'DECIMAL(15, 2)',
        'price': 'DECIMAL(15, 2)',
        'price_change': 'DECIMAL(8, 6)',
        'daily_active_addresses_price': 'DECIMAL(15, 2)',
        'daily_active_addresses_per': 'DECIMAL(8, 6)',
        'hodlers_balance_price': 'DECIMAL(15, 2)',
        'hodlers_balance_per': 'DECIMAL(8, 6)',
        'signals': 'VARCHAR(50)'
    }
    saveToSql('intotheblock', ext_data, dataType)

def extractAllCryptocurrencies():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://app.intotheblock.com/category/all') #https://app.intotheblock.com/category/all?end_offset=20
    driver.implicitly_wait(20)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    contents = soup.find_all('div', class_='Highlights-container')
    market_cap = contents[0].find('span', class_='value').text
    market_per = contents[0].find('span', class_='change').text
    ext_data = []
    records = soup.find_all('div', 'icon-container')
    for record in records:
        ext_data.append(record.find('span', class_='label').text + record.find('span', class_='value').text)
    i = 1
    while i < len(contents):
        ext_data.append(contents[i].find('span', class_='value').text)
        i = i + 1
    # print("asdasdasd", ext_data)
    dataType = {
        'market_cap': 'VARCHAR(30)',
        'market_per': 'VARCHAR(30)',
        'coins_dom_btc': 'VARCHAR(30)',
        'coins_dom_eth': 'VARCHAR(30)',
        'coins_dom_other': 'VARCHAR(30)',
        'coins_dom_stacoin': 'VARCHAR(30)',
        'stablecoin_flows': 'VARCHAR(30)',
        'stablecoin_supply': 'VARCHAR(30)',
        'sp500_btc': 'VARCHAR(30)',
        'defi_total_locked': 'VARCHAR(30)',
        'nfts_volume': 'VARCHAR(30)',
    }
    data = [
        {
            'market_cap': convertNumber(market_cap),
            'market_per': market_per,
            'coins_dom_btc': ext_data[0],
            'coins_dom_other': ext_data[1],
            'coins_dom_eth': ext_data[2],
            'coins_dom_stacoin': ext_data[3],
            'stablecoin_flows': convertNumber(ext_data[4]),
            'stablecoin_supply': convertNumber(ext_data[5]),
            'sp500_btc': ext_data[6],
            'defi_total_locked': convertNumber(ext_data[7]),
            'nfts_volume': convertNumber(ext_data[8])
        }
    ]
    print(data)
    saveToSql('intotheblock_summary', data, dataType)

def saveToSql(table_name, data, data_type):
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='workspace'
    )

    cursor = connection.cursor()
    print("start save to sql..")
    # Define the SQL statement to delete all data from the table
    delete_query = f"DROP TABLE IF EXISTS {table_name}"
    # Execute the SQL statement to delete all data
    print("delete query: ", delete_query)
    cursor.execute(delete_query)
    print('delete table')
    create_table_query = """
        CREATE TABLE IF NOT EXISTS {table_name} (
            _id INT AUTO_INCREMENT PRIMARY KEY,
    """.format(table_name = table_name)
    print(create_table_query)

    # data = json.loads(json_data)
    # Define SQL statement
    # sql = "INSERT INTO your_table (column1, column2, column3) VALUES (%s, %s, %s)"
    sql = "INSERT INTO " + table_name + " ("
    keys = data[0].keys()
    id = 0
    sstr = "("
    print(keys)
    for key in keys:
        if id < len(keys) - 1:
            sql += key + ", "
            sstr += "%s, "
            create_table_query += key + " " + data_type[key] + ",\n"
        else:
            sql += key + ") VALUES "
            sstr += "%s)"
            create_table_query += key + " " + data_type[key] + "\n)"
        id += 1

    sql += sstr
    print("sql query: ", sql)
    print("table query: ", create_table_query)
    cursor.execute(create_table_query)

    # Insert data into the database
    for record in data:
        values = ()
        for key in keys:
            if key in record:
                values += (record[key],)
            else:
                values += (None,)
        cursor.execute(sql, values)

    # Commit the changes
    connection.commit()
    cursor.close()
    connection.close()

def convertNumber(str_number):
    str_number = str_number.replace(',', '')
    str_number = str_number.replace(' ', '')
    ext_num = 0
    if str_number == '' or str_number is None:
        return '0'
    if str_number[0] == '$':
        if str_number[len(str_number) - 1] == 'b':
            ext_num = str_number[1 : len(str_number) - 1]
            ext_num = float(ext_num) * 1000000000
        elif str_number[len(str_number) - 1] == 'm':
            ext_num = str_number[1 : len(str_number) - 1]
            ext_num = float(ext_num) * 1000000
        elif str_number[len(str_number) - 1] == 'k':
            ext_num = str_number[1 : len(str_number) - 1]
            ext_num = float(ext_num) * 1000
        elif str_number[len(str_number) - 1] == 't':
            ext_num = str_number[1 : len(str_number) - 1]
            ext_num = float(ext_num) * 1000000000000
        else:
            ext_num = float(str_number[1:])
    elif str_number[len(str_number) - 1] == '%':
        ext_num = float(str_number[ : len(str_number) - 1])
    else:
        if str_number[len(str_number) - 1] == 'b':
            ext_num = str_number[: len(str_number) - 1]
            ext_num = float(ext_num) * 1000000000
        elif str_number[len(str_number) - 1] == 'm':
            ext_num = str_number[: len(str_number) - 1]
            ext_num = float(ext_num) * 1000000
        elif str_number[len(str_number) - 1] == 'k':
            ext_num = str_number[: len(str_number) - 1]
            ext_num = float(ext_num) * 1000
        else:
            ext_num = float(str_number[:])
    return ext_num

# def run():
getCoinOftheDay()
getCoinOftheDayInfo()
getCoins()
# getInfluenceOfACoin(2)
getMetaOfACoin(2)
getInfluenceOfCoins()
getFeeds()
extractAllInformations()
extractAllCryptocurrencies()

# schedule.every().hour.do(run)

# while True:
#     print('Fetching data from external apis...')
#     schedule.run_pending()
#     time.sleep(60)