import requests
import json

from mendable import ChatApp
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import openai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import mysql.connector

# filename = 'training/data.csv'

load_dotenv()

coinmarketcap_api_key = os.getenv("COINMARKETCAP_API_KEY")
mendable_api_key = os.getenv("MENDABLE_API_KEY")
defined_api_key = os.getenv("DEFINED_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = openai_api_key

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']


def create_dataframe(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename)
    print(f'Data saved to {filename} successfully.')


def getRealTimeCoinPrice() :
    data_dict = {
        "content": [],
    }
    res = ""
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    parameters = {
        'start': '1',
        'limit': '500',
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': coinmarketcap_api_key,  # replace 'your-api-key' with your actual API key
    }
    sql_datas = []
    data_type = {
        "name": "VARCHAR(50)", "symbol": "VARCHAR(50)", "max_supply": "DECIMAL(20, 2)", "circulating_supply": "DECIMAL(20, 2)", 'total_supply': "DECIMAL(20, 2)", 'price': "DECIMAL(20, 2)", 'volume_24h': "DECIMAL(20, 2)", 'volume_change_24h': "DECIMAL(20, 2)", 'percent_change_1h': "DECIMAL(20, 2)", 'percent_change_24h': "DECIMAL(20, 2)", 'percent_change_7d': "DECIMAL(20, 2)", 'percent_change_30d': "DECIMAL(20, 2)", 'percent_change_60d': "DECIMAL(20, 2)", 'percent_change_90d': "DECIMAL(20, 2)", 'market_cap': "DECIMAL(20, 2)", 'fully_diluted_market_cap': "DECIMAL(20, 2)"
    }
    response = requests.get(url, headers=headers, params=parameters)
    info = json.loads(response.text)
    print(len(info['data']))
    for coin in info['data']:
        res = f"Current Status of {coin['name']}, {coin['symbol']} \n"
        res += f"Coin: {coin['name']}, Symbol: {coin['symbol']}, Max supply: {coin['max_supply']}, Circulating supply: {coin['circulating_supply']}, Total supply: {coin['total_supply']}, Price: {coin['quote']['USD']['price']}, Volume 24h: {coin['quote']['USD']['volume_24h']},Volume Change 24h: {coin['quote']['USD']['volume_change_24h']}, Percent Change 1h: {coin['quote']['USD']['percent_change_1h']}, Percent Change 24h: {coin['quote']['USD']['percent_change_24h']}, Percent Change 7d: {coin['quote']['USD']['percent_change_7d']}, Percent Change 30d: {coin['quote']['USD']['percent_change_30d']}, Percent Change 60d: {coin['quote']['USD']['percent_change_60d']}, Percent Change 90d: {coin['quote']['USD']['percent_change_90d']}, Market Capitalization: {coin['quote']['USD']['market_cap']}, Fully diluted market capitalization: {coin['quote']['USD']['fully_diluted_market_cap']}\n\n"
        sql_data = {
            "name": coin['name'], "symbol": coin['symbol'], "max_supply": coin['max_supply'], "circulating_supply": coin['circulating_supply'], 'total_supply': coin['total_supply'], 'price': coin['quote']['USD']['price'], 'volume_24h': coin['quote']['USD']['volume_24h'], 'volume_change_24h': coin['quote']['USD']['volume_change_24h'], 'percent_change_1h': coin['quote']['USD']['percent_change_1h'], 'percent_change_24h': coin['quote']['USD']['percent_change_24h'], 'percent_change_7d': coin['quote']['USD']['percent_change_7d'], 'percent_change_30d': coin['quote']['USD']['percent_change_30d'], 'percent_change_60d': coin['quote']['USD']['percent_change_60d'], 'percent_change_90d': coin['quote']['USD']['percent_change_90d'], 'market_cap': coin['quote']['USD']['market_cap'], 'fully_diluted_market_cap': coin['quote']['USD']['fully_diluted_market_cap']
        }
        sql_datas.append(sql_data)
        data_dict['content'].append(res)

    # create_dataframe(data_dict, 'training/coinprice.csv')
    saveToSql('current_status_of_tokens_coinmarketcap', sql_datas, data_type)

def getAirDropsOfCoins():
    data_dict = {
        "content": [],
    }
    today = datetime.today().date()
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/airdrops"
    parameters = {
        'start': '1',
        'limit': '100',
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': coinmarketcap_api_key,  # replace 'your-api-key' with your actual API key
    }
    response = requests.get(url, headers=headers, params=parameters)
    info = json.loads(response.text)
    print('total Air Drops count = ', len(info['data']))
    sql_datas = []
    data_type = {
        "project_name": "VARCHAR(50)", "description": "TEXT", "status": "TEXT", "coin_name": "VARCHAR(50)", 'coin_symbol': "VARCHAR(50)", 'start_date': "DATE", 'end_date': "DATE", 'total_prize': "DECIMAL(20, 2)", 'winner_count': "DECIMAL(20, 2)"
    }
    res = ""
    for airdrop in info['data']:
        res = "airdrops of coins\n"
        res += f"Project Name: {airdrop['project_name']}, Description: {airdrop['description']}, Status: {airdrop['status']}, Coin Name: {airdrop['coin']['name']}, Coin Symbol: {airdrop['coin']['symbol']}, Start Date: {airdrop['start_date']}, End Date: {airdrop['end_date']}, Total Prize: {airdrop['total_prize']}, Winner Count: {airdrop['winner_count']}\n"
        sql_data = {
            "project_name": airdrop['project_name'], "description": airdrop['description'], "status": airdrop['status'], "coin_name": airdrop['coin']['name'], 'coin_symbol': airdrop['coin']['symbol'], 'start_date': airdrop['start_date'], 'end_date': airdrop['end_date'], 'total_prize': airdrop['total_prize'], 'winner_count': airdrop['winner_count']
        }
        sql_datas.append(sql_data)
        data_dict['content'].append(res)
    # create_dataframe(data_dict, 'training/airdrops_of_coins.csv')
    saveToSql('airdrops_of_tokens_coinmarketcap', sql_datas, data_type)

def getContentLatest():
    return
    data_dict = {
        # "title": [],
        "content": [],
        # "embedding": []
    }
    url = "https://pro-api.coinmarketcap.com/v1/content/latest"
    parameters = {
        'start': '1',
        'limit': '100',
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': coinmarketcap_api_key,  # replace 'your-api-key' with your actual API key
    }
    response = requests.get(url, headers=headers, params=parameters)
    info = json.loads(response.text)
    print('total Content Latest count = ', len(info['data']))
    res = ""
    sql_datas = []
    data_type = {
        "assets name": "VARCHAR(50)", "assets symbol": "VARCHAR(50)", "title": "VARCHAR(50)", "subtitle": "VARCHAR(50)", 'type': "VARCHAR(50)", 'source name': "VARCHAR(50)", 'source url': "VARCHAR(50)"
    }
    for content in info['data']:
        res = "Content Latest\n"
        res += f"Assets Name: {content['assets']['name']}, Assets Symbol: {content['assets']['symbol']}, Title: {content['title']}, Subtitle: {content['subtitle']}, Type: {content['type']}, Source Name: {content['source_name']}, Source URL: {content['source_url']} \n"
        data_dict['content'].append(res)
        sql_data = {
            "assets name": content['assets']['name'], "assets symbol": content['assets']['symbol'], "title": content['title'], "subtitle": content['subtitle'], 'type': content['type'], 'source name': content['source_name'], 'source url': content['source_url']
        }
        sql_datas.append(sql_data)
    # create_dataframe(data_dict, 'training/latestcontent.csv')
    saveToSql('latest_content_of_tokens_coinmarketcap', sql_datas, data_type)

def getCommunityTrendingTokens():
    return
    data_dict = {
        # "title": [],
        "content": [],
        # "embedding": []
    }
    url = "https://pro-api.coinmarketcap.com/v1/community/trending/token"
    parameters = {
        'start': '1',
        'limit': '100',
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': coinmarketcap_api_key,  # replace 'your-api-key' with your actual API key
    }
    response = requests.get(url, headers=headers, params=parameters)
    info = json.loads(response.text)
    print('total Community Trending Tokens count = ', len(info['data']))
    res = ""
    sql_datas = []
    data_type = {
        "rank": "VARCHAR(50)", "cmc rank": "VARCHAR(50)", "token name": "VARCHAR(50)", "token symbol": "VARCHAR(50)"
    }
    for tokens in info['data']:
        res = "Comunity Trending Tokens\n"
        res += f"Rank: {tokens['rank']}, CMC Rank: {tokens['cmc_rank']}, Token Name: {tokens['name']}, Token Symbol: {tokens['symbol']} \n"
        data_dict['content'].append(res)
        sql_data = {
            "rank": tokens['rank'], "cmc rank": tokens['cmc_rank'], "token name": tokens['name'], "token symbol": tokens['symbol']
        }
        sql_datas.append(sql_data)
    # create_dataframe(data_dict, 'training/community_trending_tokens.csv')
    saveToSql('community_trending_tokens_coinmarketcap', sql_datas, data_type)

def getTrendingLatest():
    data_dict = {
        "content": [],
    }
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/trending/latest"
    parameters = {
        'start': '1',
        'limit': '100',
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': coinmarketcap_api_key,  # replace 'your-api-key' with your actual API key
    }

    response = requests.get(url, headers=headers, params=parameters)
    info = json.loads(response.text)
    print('total Trending Latest count = ', len(info['data']))
    res = ""
    sql_datas = []
    data_type = {
        "name": "VARCHAR(50)", "symbol": "VARCHAR(50)", "date_added": "DATE", "max_supply": "DECIMAL(20, 2)", "circulating_supply": "DECIMAL(20, 2)", "total_supply": "DECIMAL(20, 2)", "cmc_rank" : "DECIMAL(20, 2)", "self_reported_circulating_supply": "DECIMAL(20, 2)", "self_reported_market_cap": "DECIMAL(20, 2)", "last_updated": "DATE", "price": "DECIMAL(20, 2)", "volume_24h": "DECIMAL(20, 2)", "volume_change_24h": "DECIMAL(20, 2)", "percent_change_1h": "DECIMAL(20, 2)", "percent_change_24h": "DECIMAL(20, 2)", "percent_change_7d": "DECIMAL(20, 2)", "percent_change_30d": "DECIMAL(20, 2)", "percent_change_60d": "DECIMAL(20, 2)", "percent_change_90d": "DECIMAL(20, 2)", "market_cap": "DECIMAL(20, 2)"
    }
    for tokens in info['data']:
        res = "Trending cryptocurrency market data\n"
        # res += f"Rank: {tokens['rank']}, CMC Rank: {tokens['cmc_rank']}, Token Name: {tokens['name']}, Token Symbol: {tokens['symbol']}"
        res += json.dumps(tokens) + "\n"
        data_dict['content'].append(res)
        sql_data = {
            "name": tokens['name'], "symbol": tokens['symbol'], "date_added": tokens['date_added'], "max_supply": tokens['max_supply'], "circulating_supply": tokens['circulating_supply'], "total_supply": tokens['total_supply'], "cmc_rank" : tokens['cmc_rank'], "self_reported_circulating_supply": tokens['self_reported_circulating_supply'], "self_reported_market_cap": tokens['self_reported_market_cap'], "last_updated": tokens['last_updated'], "price": tokens['quote']['USD']['price'], "volume_24h": tokens['quote']['USD']['volume_24h'], "volume_change_24h": tokens['quote']['USD']['volume_change_24h'], "percent_change_1h": tokens['quote']['USD']['percent_change_1h'], "percent_change_24h": tokens['quote']['USD']['percent_change_24h'], "percent_change_7d": tokens['quote']['USD']['percent_change_7d'], "percent_change_30d": tokens['quote']['USD']['percent_change_30d'], "percent_change_60d": tokens['quote']['USD']['percent_change_60d'], "percent_change_90d": tokens['quote']['USD']['percent_change_90d'], "market_cap": tokens['quote']['USD']['market_cap']
        }
        sql_datas.append(sql_data)
    # create_dataframe(data_dict, 'training/trending_latest.csv')
    saveToSql('latest_trending_tokens_coinmarketcap', sql_datas, data_type)

def getListingNews():
    data_dict = {
        "content": [],
    }
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/new"
    parameters = {
        'start': '1',
        'limit': '5',
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': coinmarketcap_api_key,  # replace 'your-api-key' with your actual API key
    }
    response = requests.get(url, headers=headers, params=parameters)
    info = json.loads(response.text)
    print('total Listing News count = ', len(info['data']))
    res = ""
    print(info['data'][0])
    sql_datas = []
    data_type = {
        "name": "VARCHAR(50)", "symbol": "VARCHAR(50)", "date_added": "DATE", "max_supply": "DECIMAL(20, 2)", "circulating_supply": "DECIMAL(20, 2)", "total_supply": "DECIMAL(20, 2)", "cmc_rank" : "DECIMAL(20, 2)", "self_reported_circulating_supply": "DECIMAL(20, 2)", "self_reported_market_cap": "DECIMAL(20, 2)", "last_updated": "DATE", "price": "DECIMAL(20, 2)", "volume_24h": "DECIMAL(20, 2)", "volume_change_24h": "DECIMAL(20, 2)", "percent_change_1h": "DECIMAL(20, 2)", "percent_change_24h": "DECIMAL(20, 2)", "percent_change_7d": "DECIMAL(20, 2)", "percent_change_30d": "DECIMAL(20, 2)", "percent_change_60d": "DECIMAL(20, 2)", "percent_change_90d": "DECIMAL(20, 2)", "market_cap": "DECIMAL(20, 2)"
    }
    for tokens in info['data']:
        res = "Recently added cryptocurrency\n"
        res += json.dumps(tokens) + "\n"
        data_dict['content'].append(res)
        sql_data = {
            "name": tokens['name'], "symbol": tokens['symbol'], "date_added": tokens['date_added'], "max_supply": tokens['max_supply'], "circulating_supply": tokens['circulating_supply'], "total_supply": tokens['total_supply'], "cmc_rank" : tokens['cmc_rank'], "self_reported_circulating_supply": tokens['self_reported_circulating_supply'], "self_reported_market_cap": tokens['self_reported_market_cap'], "last_updated": tokens['last_updated'], "price": tokens['quote']['USD']['price'], "volume_24h": tokens['quote']['USD']['volume_24h'], "volume_change_24h": tokens['quote']['USD']['volume_change_24h'], "percent_change_1h": tokens['quote']['USD']['percent_change_1h'], "percent_change_24h": tokens['quote']['USD']['percent_change_24h'], "percent_change_7d": tokens['quote']['USD']['percent_change_7d'], "percent_change_30d": tokens['quote']['USD']['percent_change_30d'], "percent_change_60d": tokens['quote']['USD']['percent_change_60d'], "percent_change_90d": tokens['quote']['USD']['percent_change_90d'], "market_cap": tokens['quote']['USD']['market_cap']
        }
        sql_datas.append(sql_data)
    # create_dataframe(data_dict, 'training/listine_news.csv')
    saveToSql('new_listings_tokens_coinmarketcap', sql_datas, data_type)

def getChains():
    data_dict = {
        "content": [],
    }

    chrome_options = Options()
    # Initialize the Chrome webdriver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the URL
    driver.get('https://defillama.com/chains')
    # time.sleep(10)
    # Wait for the page to fully load. This is very important for dynamic websites and the actual wait time may vary.
    # You might need to increase this value if your internet speed is slow or the server is slow.
    driver.implicitly_wait(20)  # waits up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds.

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    scripts = soup.find_all('script')
    tbody = soup.find_all('tbody')
    sql_datas = []
    for tbb in tbody:
        trs=  tbb.find_all('tr')

        for tr in trs:
            name_element = tr.find('a', class_='sc-230b184d-1')
            name = name_element.text if name_element else None
            td_elements = tr.find_all('td') 
            if len(td_elements) >= 2:  # Ensure that there are at least two <td> elements
                protocols = td_elements[1].text  # Access the second <td> element and retrieve its text content
                users = td_elements[2].text
                if users is None:
                    users = "<no user>"
                elif 'm' in users:
                    users = users.replace('m', '')  # Remove the 'M' character
                    users = float(users) * 1000000  # Multiply by 1,000,000
                else:
                    users = users
                    users = users.replace(',', '')
                
                print("user", users)
                change_1d = td_elements[3].text 
                change_7d = td_elements[4].text  
                tvl = td_elements[6].text  
                tvl = td_elements[6].text.replace('$', '') if td_elements else None  
                if 'm' in tvl:
                    tvl = tvl.replace('m', '')  # Remove the 'M' character
                    tvl = float(tvl) * 1000000  # Multiply by 1,000,000
                elif 'b' in tvl:
                    tvl = tvl.replace('b', '')  # Remove the 'M' character
                    tvl = float(tvl) * 1000000000
                else:
                    tvl = tvl
                    tvl = tvl.replace(',', '')

                stables = td_elements[7].text
                stables = td_elements[7].text.replace('$', '') if td_elements else None  
                if 'm' in stables:
                    stables = stables.replace('m', '')  # Remove the 'M' character
                    stables = float(stables) * 1000000  # Multiply by 1,000,000
                elif 'b' in stables:
                    stables = stables.replace('b', '')  # Remove the 'M' character
                    stables = float(stables) * 1000000000
                else:
                    stables = stables
                    stables = stables.replace(',', '')

                totalVolume24h = td_elements[8].text
                totalVolume24h = td_elements[8].text.replace('$', '') if td_elements else None  
                if 'm' in totalVolume24h:
                    totalVolume24h = totalVolume24h.replace('m', '')  # Remove the 'M' character
                    totalVolume24h = float(totalVolume24h) * 1000000  # Multiply by 1,000,000
                elif 'b' in totalVolume24h:
                    totalVolume24h = totalVolume24h.replace('b', '')  # Remove the 'M' character
                    totalVolume24h = float(totalVolume24h) * 1000000000
                else:
                    totalVolume24h = totalVolume24h
                    totalVolume24h = totalVolume24h.replace(',', '')

                totalFees24h = td_elements[9].text
                totalFees24h = td_elements[9].text.replace('$', '') if td_elements else None  
                if 'm' in totalFees24h:
                    totalFees24h = totalFees24h.replace('m', '')  # Remove the 'M' character
                    totalFees24h = float(totalFees24h) * 1000000  # Multiply by 1,000,000
                elif 'b' in totalFees24h:
                    totalFees24h = totalFees24h.replace('b', '')  # Remove the 'M' character
                    totalFees24h = float(totalFees24h) * 1000000000
                else:
                    totalFees24h = totalFees24h
                    totalFees24h = totalFees24h.replace(',', '')
                    
                mcaptvl = td_elements[10].text
                change_1m = td_elements[5].text

            
            data_type = {
                "name": "VARCHAR(50)", "protocols": "DECIMAL(20, 2)", "users": "DECIMAL(20, 2)", "change_1d": "DECIMAL(20, 2)", "change_7d": "DECIMAL(20, 2)", "change_1m": "DECIMAL(20, 2)", "tvl" : "DECIMAL(20, 2)", "stables": "DECIMAL(20, 2)", "totalVolume24h": "DECIMAL(20, 2)", "totalFees24h": "DECIMAL(20, 2)", "mcaptvl": "DECIMAL(20, 2)"
            }
            sql_data = {
                "name": name, "protocols": protocols, "users": users, "change_1d": change_1d, "change_7d": change_7d, "change_1m": change_1m, "tvl" : tvl, "stables": stables, "totalVolume24h": totalVolume24h, "totalFees24h": totalFees24h, "mcaptvl": mcaptvl
            }
            sql_datas.append(sql_data)

            print("asdas", sql_datas)

    saveToSql('tvl_chains_defillama', sql_datas, data_type)

def getProtocols():
    data_dict = {
        "content": [],
    }
    # Initialize the Chrome webdriver
    driver = webdriver.Chrome()

    # Open the URL
    driver.get('https://defillama.com/protocols')
    # time.sleep(10)
    # Wait for the page to fully load. This is very important for dynamic websites and the actual wait time may vary.
    # You might need to increase this value if your internet speed is slow or the server is slow.
    driver.implicitly_wait(20)  # waits up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds.

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    scripts = soup.find_all('script')
    script = ''
    for s in scripts:
        if 'type' in s.attrs.keys():
            script = s  
            print('true')
    if script == '':
        return

    script = json.loads(script.text.strip())

    protocols = script['props']['pageProps']['protocols']

    # print(type(script))
    # Close the browser
    driver.quit()

    # Now you can use BeautifulSoup to parse and extract the data
    # print(soup.prettify())
    # print('total Listing News count = ', len(info['data']))
    res = ""
    sql_datas = []
    data_type = {
        "name": "VARCHAR(50)", "category": "VARCHAR(50)", "change_1d": "DECIMAL(20, 2)", "change_7d": "DECIMAL(20, 2)", "change_1m": "DECIMAL(20, 2)", "tvl" : "DECIMAL(20, 2)", "mcaptvl": "DECIMAL(20, 2)"
    }

    for i in range(0, 100):
        res += "Protocols of chains\n"
        res += f"Name: {protocols[i]['name']}, Category: {protocols[i]['category']}, 1d Change: {protocols[i]['change_1d']}, 7d Change: {protocols[i]['change_7d']}, 1m Change: {protocols[i]['change_1m']}, TVL: {protocols[i]['tvl']}, MCap/TVL: {protocols[i]['mcaptvl']} \n"
        data_dict['content'].append(res)
        sql_data = {
            "name": protocols[i]['name'], "category": protocols[i]['category'], "change_1d": protocols[i]['change_1d'], "change_7d": protocols[i]['change_7d'], "change_1m": protocols[i]['change_1m'], "tvl" : protocols[i]['tvl'], "mcaptvl": protocols[i]['mcaptvl']
        }
        sql_datas.append(sql_data)
    saveToSql('protocols_defillama', sql_datas, data_type)
    # create_dataframe(data_dict, 'training/protocol_of_chains.csv')

def getAirDropsOfChains():
    data_dict = {
        "content": [],
    }
    # Initialize the Chrome webdriver
    driver = webdriver.Chrome()

    driver.get('https://defillama.com/airdrops')
    # time.sleep(10)
    # Wait for the page to fully load. This is very important for dynamic websites and the actual wait time may vary.
    # You might need to increase this value if your internet speed is slow or the server is slow.
    driver.implicitly_wait(20)  # waits up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds.

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    scripts = soup.find_all('script')
    # with open('data.txt', 'w', encoding='utf-8') as file:
    #     file.write(str(script))
    script = ''
    for s in scripts:
        if 'type' in s.attrs.keys():
            script = s  
            print('true')
    if script == '':
        return
    script = json.loads(script.text.strip())

    airdrops = script['props']['pageProps']['protocols']

    driver.quit()

    # Now you can use BeautifulSoup to parse and extract the data
    res = ""
    res += "Airdrops of chains\n"
    sql_datas = []
    data_type = {
        "name": "VARCHAR(50)", "category": "VARCHAR(50)", "tvl" : "DECIMAL(20, 2)"
    }

    for i in range(len(airdrops)-1, len(airdrops)-31, -1):
        res += f"Name: {airdrops[i]['name']}, Category: {airdrops[i]['category']}, TVL: {airdrops[i]['tvl']} \n"
        data_dict['content'].append(res)
        sql_data = {
            "name": airdrops[i]['name'], "category": airdrops[i]['category'], "tvl" : airdrops[i]['tvl']
        }
        sql_datas.append(sql_data)
    saveToSql('airdrops_defillama', sql_datas, data_type)
    # create_dataframe(data_dict, 'training/airdrops_of_chains.csv')

def get_defined_data():
    # Define the API endpoint URL
    url = "https://api.defined.fi"

    headers = {
        "content_type":"application/json",
        "x-api-key": defined_api_key
    }

    getNetworks = """query GetNetworksQuery { getNetworks { name id } }"""
    response = requests.post(url, headers=headers, json={"query": getNetworks})
    networks = json.loads(response.text)
    networks = networks['data']['getNetworks']
    data = ""
    for network in networks:
        getTopTokens = f"""
            query {{
                listTopTokens(limit: 5, networkFilter: {network['id']}) {{
                    name
                    symbol
                    price
                    priceChange
                    liquidity
                    volume
                }}
            }}
        """
        response = requests.post(url, headers=headers, json={"query": getTopTokens})
        listTokens = json.loads(response.text)
        listTokens = listTokens['data']['listTopTokens']
        token_str = ''
        token_str += "5 trending tokens of " + network['name'] + "\n"
        for token in listTokens:
            token_str += json.dumps(token) + "\n"
        data += token_str + "\n"
    return data

def getTrendingTokens() :
    data_dict = {
        # "title": [],
        "content": [],
        # "embedding": []
    }
    # Initialize the Chrome webdriver
    driver = webdriver.Chrome()

    driver.get('https://www.defined.fi/trending')
    time.sleep(10)
    # Wait for the page to fully load. This is very important for dynamic websites and the actual wait time may vary.
    # You might need to increase this value if your internet speed is slow or the server is slow.
    driver.implicitly_wait(20)  # waits up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds.

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    trendings = soup.find_all(class_='css-1v9dlgu')
    sql_datas = []
    data_type = {
        "symbol": "VARCHAR(50)", "name": "VARCHAR(50)", "price" : "VARCHAR(50)", "token_symbol_1": "VARCHAR(50)", "token_name_1": "VARCHAR(50)", "token_price_1": "VARCHAR(50)", "token_percent_1": "VARCHAR(50)", "token_symbol_2": "VARCHAR(50)", "token_name_2": "VARCHAR(50)", "token_price_2": "VARCHAR(50)", "token_percent_2": "VARCHAR(50)", "token_symbol_3": "VARCHAR(50)", "token_name_3": "VARCHAR(50)", "token_price_3": "VARCHAR(50)", "token_percent_3": "VARCHAR(50)", "token_symbol_4": "VARCHAR(50)", "token_name_4": "VARCHAR(50)", "token_price_4": "VARCHAR(50)", "token_percent_4": "VARCHAR(50)", "token_symbol_5": "VARCHAR(50)", "token_name_5": "VARCHAR(50)", "token_price_5": "VARCHAR(50)", "token_percent_5": "VARCHAR(50)" 
    }
    for trending in trendings:
        symbol = trending.find_all(class_='MuiTypography-h6')[0].text
        name = trending.find_all(class_='MuiTypography-body2')[0].text
        price = trending.find_all(class_='css-vjb988')[0].text
        tokenSymbol = trending.find_all(class_='css-xejnbo')
        token_symbols = []
        token_names = []
        token_prices = []
        token_percents = []
        for s in tokenSymbol:
            token_symbols.append(s.text)

        tokenName = trending.find_all(class_='css-gh04iv')
        for s in tokenName:
            token_names.append(s.text)

        tokenPrice = trending.find_all(class_='css-z9ewvz')
        for s in tokenPrice:
            token_prices.append(s.text)
        percentDiv = trending.find_all(attrs = {"translate":'no'})
        for s in percentDiv:
            sym = ''
            path = s.find_all(lambda tag: tag.has_attr('d') and "7-8h-14z" in tag['d'])
            if len(path) > 0:
                sym = '-'
            token_percents.append(sym + s.text)
        if len(token_percents) == 5:
            sql_data = {
                "symbol": symbol, "name": name, "price" : price, "token_symbol_1": token_symbols[0], "token_name_1":token_names[0], "token_price_1": token_prices[0], "token_percent_1": token_percents[0], "token_symbol_2": token_symbols[1], "token_name_2":token_names[1], "token_price_2": token_prices[1], "token_percent_2": token_percents[1], "token_symbol_3": token_symbols[2], "token_name_3":token_names[2], "token_price_3": token_prices[2], "token_percent_3": token_percents[2], "token_symbol_4": token_symbols[3], "token_name_4":token_names[3], "token_price_4": token_prices[3], "token_percent_4": token_percents[3], "token_symbol_5": token_symbols[4], "token_name_5":token_names[4], "token_price_5": token_prices[4], "token_percent_5": token_percents[4]
            }
        else:
            sql_data = {
                "symbol": symbol, "name": name, "price" : price, "token_symbol_1": "None", "token_name_1":"None", "token_price_1": "None", "token_percent_1": "None", "token_symbol_2": "None", "token_name_2":"None", "token_price_2": "None", "token_percent_2": "None", "token_symbol_3": "None", "token_name_3":"None", "token_price_3": "None", "token_percent_3": "None", "token_symbol_4": "None", "token_name_4":"None", "token_price_4": "None", "token_percent_4": "None", "token_symbol_5": "None", "token_name_5":"None", "token_price_5": "None", "token_percent_5": "None"
            }
        sql_datas.append(sql_data)

    saveToSql('trending_tokens_defined', sql_datas, data_type)

def getNewTokens() :
    # Initialize the Chrome webdriver
    driver = webdriver.Chrome()

    driver.get('https://www.defined.fi/new')
    time.sleep(20)
    # Wait for the page to fully load. This is very important for dynamic websites and the actual wait time may vary.
    # You might need to increase this value if your internet speed is slow or the server is slow.
    driver.implicitly_wait(20)  # waits up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds.

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup)
    lists = soup.find_all(class_='css-1qw2275')
    print("sdsd", lists)
    sql_datas = []
    data_type = {
        "name": "VARCHAR(50)", "price" : "VARCHAR(50)", "variation_price": "VARCHAR(50)", "total_liquidity": "VARCHAR(50)", "variation_liquidity": "VARCHAR(50)", "created_time" : "DATE"
    }
    for token in lists:
        name = token.find_all(class_='css-1pfxfym')[0].text
        # print("nam>>>>", name)
        price = token.find_all(class_='css-1tphccq')[0].text
        total_liquidiy = token.find_all(class_='css-1tphccq')[1].text
        percentDiv = token.find_all(attrs = {"translate":'no'})
        token_percents = []
        for s in percentDiv:
            sym = ''
            path = s.find_all(lambda tag: tag.has_attr('d') and "7-8h-14z" in tag['d'])
            if len(path) > 0:
                sym = '-'
            token_percents.append(sym + s.text)
        created_time = token.find_all(class_='css-1rxp0nc')[0]['aria-label']
        # print("name   ", name)
        # print("price   ", price)
        # print("liquidity   ", total_liquidiy)
        # print("percent   ", token_percents)

        sql_data = {
            "name": name, "price" : price, "variation_price": token_percents[0], "total_liquidity": total_liquidiy, "variation_liquidity": token_percents[1], "created_time": created_time
        }
        sql_datas.append(sql_data)

    saveToSql('new_tokens_defined', sql_datas, data_type)

def extract_coinstats_news():
    data_dict = {
        'content': [],
    }   
    url = 'https://api.coinstats.app/public/v1/news?skip=0&limit=20'
    # Check if the request was successful
    response = requests.get(url)
    time.sleep(2)
    sql_datas = []
    data_type = {
        "news_id": "VARCHAR(50)", "feedDate": "DECIMAL(20, 2)", "source": "VARCHAR(50)", "title": "TEXT", "description": "TEXT", "imageURL": "TEXT", "news_link": "TEXT", "shareURL": "TEXT"
    }
    # Extract the JSON data from the response
    info = json.loads(response.text)
    # Process and extract the desired data from the JSON
    res = ''
    for tokens in info['news']:
        res += json.dumps(tokens) + "\n"
        data_dict['content'].append(res)

        sql_data = { 'news_id': tokens['id'], 'feedDate': tokens['feedDate'], 'source': tokens['source'], 'title': tokens['title'], 'description': tokens['description'], 'imageURL': tokens['imgURL'], 'news_link': tokens['link'], 'shareURL': tokens['shareURL'] }
        sql_datas.append(sql_data)
    saveToSql('crypto_news', sql_datas, data_type)

# getRealTimeCoinPrice()
# getAirDrops()
# getTrendingLatest()
# create_dataframe(data_dict)

# from llama_index import LLMPredictor, PromptHelper, SimpleDirectoryReader, ServiceContext, GPTVectorStoreIndex, download_loader, StorageContext, load_index_from_storage
# from langchain.chat_models import ChatOpenAI

# # we will use this UnstructuredReader to read PDF file
# UnstructuredReader = download_loader('UnstructuredReader', refresh_cache=True)
# loader = UnstructuredReader()
# # load the data
# data = loader.load_data(f'data.csv', split_documents=False)

# # define LLM
# # llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.2,model_name='gpt-3.5-turbo'))
# # define prompt helper
# # set maximum input size
# max_input_size = 4096
# # set number of output tokens
# num_output = 256
# # set maximum chunk overlap
# max_chunk_overlap = 20
# # prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)
# # service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
# index = GPTVectorStoreIndex.from_documents(
#     data
#     # service_context=service_context
# )
# query_engine = index.as_query_engine()
# while True:
#     user_query = input()
#     response = query_engine.query(user_query)
#     print(response)

# def index_documents(folder):
#     max_input_size    = 4096
#     num_outputs       = 512
#     max_chunk_overlap = 0.5
#     chunk_size_limit  = 1000

#     prompt_helper = PromptHelper(max_input_size, 
#                                  num_outputs, 
#                                  max_chunk_overlap, 
#                                  chunk_size_limit = chunk_size_limit)

#     llm_predictor = LLMPredictor(
#         llm = ChatOpenAI(temperature = 0.7, 
#                          model_name = "gpt-3.5-turbo", 
#                          max_tokens = num_outputs)
#         )
#     documents = SimpleDirectoryReader(folder).load_data()
#     index = GPTVectorStoreIndex.from_documents(
#                 documents, 
#                 llm_predictor = llm_predictor, 
#                 prompt_helper = prompt_helper)
#     index.storage_context.persist(persist_dir=".")
# getChains()
# index_documents("training")

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
            id INT AUTO_INCREMENT PRIMARY KEY,
    """.format(table_name = table_name)
    print(create_table_query)

    # Define SQL statement
    # sql = "INSERT INTO your_table (column1, column2, column3) VALUES (%s, %s, %s)"
    sql = "INSERT INTO " + table_name + " ("
    keys = data[0].keys()
    id = 0
    sstr = "("
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
            values += (record[key],)
        cursor.execute(sql, values)

    # Commit the changes
    connection.commit()
    cursor.close()
    connection.close()

while True:
    print("update")
    getRealTimeCoinPrice()
    print("finished airdrops of coins")
    getTrendingLatest()
    print("finished trending latest")
    getListingNews()
    print("finished listing news")
    getChains()
    print("finished chains")
    getProtocols()
    print("finished protocols")
    getAirDropsOfChains()
    print("finished airdrops of chains")
    getTrendingTokens()
    print("finished trending tokens")
    getNewTokens()
    print("finished new tokens")
    extract_coinstats_news()
    print("finished extract_coinstats_news")

    # index_documents('training')
    # print("finished indexing documents")
    # id = 1 - id
    # my_docs_bot.delete_source("yoursource.com")
    # upload_document()
    # Wait for the specified interval
    time.sleep(30)

# from openai.embeddings_utils import get_embedding, cosine_similarity

# def search_reviews(df, user_input, n=3, pprint=True):
#    embedding = get_embedding(user_input, model='text-embedding-ada-002')
#    df['similarities'] = df.ada_embedding.apply(lambda x: cosine_similarity(x, embedding))
#    res = df.sort_values('similarities', ascending=False).head(n)
#    return res

# res = search_reviews(df, 'delicious beans', n=3)

