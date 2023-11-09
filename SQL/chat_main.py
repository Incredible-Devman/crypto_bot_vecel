import openai
import os
from SQL import prompts
import tiktoken
import nltk
import json
import mysql.connector

from dotenv import load_dotenv

tokenizer = nltk.tokenize.TreebankWordTokenizer()

load_dotenv() 

# We will  pasting our openai credentials over here
openai.api_key = os.getenv("OPENAI_API_KEY")
message_history = []

def count_tokens(text):
    tokens = tokenizer.tokenize(text)
    return len(tokens)

# openai embeddings method
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )

    return response['data'][0]['embedding']


def find_top_match(query, k):
    query_em = get_embedding(query)
    result = index.query(query_em, top_k=k, includeMetadata=True)

    return [result['matches'][i]['metadata']['context'] for i in range(k)], [result['matches'][i]['score'] for i in range(k)]


def chat(var, message, role="user"):

    message_history.append({"role": role, "content": f"{var}"})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message,
        stream = True
        # messages = [{"role": role, "content": f"{var}"}]
    )
    
    try:
        for chunk in completion:
            # collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk['choices'][0]['delta'].get("content", "")  # extract the message
            yield chunk_message
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503
    
def report():

    connection =mysql.connector.connect(
        host = 'localhost',
        user='root',
        password='',
        database='workspace'
    )

    cursor = connection.cursor()
    market_cap = "SELECT market_cap FROM intotheblock_summary;"
    market_per = "SELECT market_per FROM intotheblock_summary;"
    coins_dom_btc = "SELECT coins_dom_btc FROM intotheblock_summary;"
    coins_dom_other = "SELECT coins_dom_other FROM intotheblock_summary;"
    coins_dom_eth = "SELECT coins_dom_eth FROM intotheblock_summary;"
    coins_dom_stacoin = "SELECT coins_dom_stacoin FROM intotheblock_summary;"
    stablecoin_flows = "SELECT stablecoin_flows FROM intotheblock_summary;"
    stablecoin_supply = "SELECT stablecoin_supply FROM intotheblock_summary;"
    sp500_btc = "SELECT sp500_btc FROM intotheblock_summary;"
    defi_total_locked = "SELECT defi_total_locked FROM intotheblock_summary;"
    nfts_volume   = "SELECT nfts_volume FROM intotheblock_summary;"

    cursor.execute(market_cap)
    market_cap = cursor.fetchone()
    # print("marketcap", market_cap)
    cursor.execute(market_per)
    market_per = cursor.fetchone()

    cursor.execute(coins_dom_btc)
    coins_dom_btc = cursor.fetchone()

    cursor.execute(coins_dom_other)
    coins_dom_other = cursor.fetchone()

    cursor.execute(coins_dom_eth)
    coins_dom_eth = cursor.fetchone()

    cursor.execute(coins_dom_stacoin)
    coins_dom_stacoin = cursor.fetchone()

    cursor.execute(stablecoin_flows)
    stablecoin_flows = cursor.fetchone()

    cursor.execute(stablecoin_supply)
    stablecoin_supply = cursor.fetchone()

    cursor.execute(sp500_btc)
    sp500_btc = cursor.fetchall()

    cursor.execute(defi_total_locked)
    defi_total_locked = cursor.fetchall()

    cursor.execute(nfts_volume)
    nfts_volume = cursor.fetchall()

    messages = []
    messages = [{"role": "user", "content":prompts.report_system_message.format(market_cap[0], market_per[0], coins_dom_btc[0], coins_dom_other[0], coins_dom_eth[0], coins_dom_stacoin[0], stablecoin_flows[0], stablecoin_supply[0], sp500_btc[0], defi_total_locked[0], nfts_volume[0][0])}]
    
    print(messages)
    complet = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream = True,
            temperature = 0
        )
    try:
        for chunk in complet:
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            yield '{}'.format(chunk_message)
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503

def tokenAnalysis(token):

    connection =mysql.connector.connect(
        host = 'localhost',
        user='root',
        password='',
        database='workspace'
    )

    cursor = connection.cursor()

    query_1 = "SELECT price, market_cap, volume_24h, total_supply, max_supply, circulating_supply, percent_change_1h, percent_change_24h, percent_change_7d, percent_change_30d, percent_change_60d, percent_change_90d FROM current_status_of_tokens_coinmarketcap WHERE name = '{}'".format(token)
    query_2 = "SELECT t2.name AS comparison_token_name, t2.symbol AS comparison_token_symbol, t2.circulating_supply AS comparison_token_circulating_supply, t2.volume_24h AS comparison_token_volume_24h FROM latest_trending_tokens_coinmarketcap AS t1 JOIN latest_trending_tokens_coinmarketcap AS t2 ON t1.cmc_rank <> t2.cmc_rank WHERE t1.name = '{}' ORDER BY t2.cmc_rank ASC Limit 5".format(token)
    query_3 = "SELECT nl.date_added, nl.price, nl.percent_change_1h, nl.percent_change_24h, nl.percent_change_7d, nl.percent_change_30d, nl.percent_change_60d, nl.percent_change_90d FROM new_listings_tokens_coinmarketcap AS nl WHERE nl.name = '{}'".format(token)
    query_4 = "SELECT tcd.protocols, tcd.users, tcd.change_1d, tcd.change_7d, tcd.change_1m, tcd.tvl, tcd.stables, tcd.totalVolume24h, tcd.totalFees24h, tcd.mcaptvl FROM tvl_chains_defillama AS tcd WHERE tcd.name = '{}'".format(token)

    query_5 = "SELECT pd.category, pd.change_1d, pd.change_7d, pd.change_1m, pd.tvl, pd.mcaptvl FROM protocols_defillama AS pd WHERE pd.name = '{}'".format(token)
    query_6 = "SELECT tt.symbol, tt.name, tt.price, tt.token_symbol_1, tt.token_name_1, tt.token_price_1, tt.token_percent_1, tt.token_symbol_2, tt.token_name_2, tt.token_price_2, tt.token_percent_2, tt.token_symbol_3, tt.token_name_3, tt.token_price_3, tt.token_percent_3, tt.token_symbol_4, tt.token_name_4, tt.token_price_4, tt.token_percent_4, tt.token_symbol_5, tt.token_name_5, tt.token_price_5, tt.token_percent_5 FROM trending_tokens_defined AS tt WHERE tt.name = '{}'".format(token)
    query_7 = "SELECT nt.price, nt.variation_price, nt.total_liquidity, nt.variation_liquidity, nt.created_time FROM new_tokens_defined AS nt WHERE nt.name = '{}'".format(token)
    query_8 = "SELECT cn.source, cn.title, cn.description, cn.news_link FROM crypto_news AS cn WHERE cn.title LIKE '%{}%' OR cn.description LIKE '%{}%'".format(token, token)

    cursor.execute(query_1)
    res_1 = cursor.fetchall()
    print("res1", res_1)

    cursor.execute(query_2)
    res_2 = cursor.fetchall()

    cursor.execute(query_3)
    res_3 = cursor.fetchall()

    cursor.execute(query_4)
    res_4 = cursor.fetchall()

    cursor.execute(query_5)
    res_5 = cursor.fetchall()
    
    cursor.execute(query_6)
    res_6 = cursor.fetchall()

    cursor.execute(query_7)
    res_7 = cursor.fetchall()

    cursor.execute(query_8)
    res_8 = cursor.fetchall()

    messages = []
    system_message = {"role": "system", "content":prompts.tokenAnalysis_system_message.format(token)}
    messages.insert(0, system_message) 
    messages.append({"role": "user", "content":prompts.tokenAnalysis_user_message.format(res_1, res_2, res_3, res_4, res_5, res_6, res_7, res_8)})
    print("messages", messages)
    complet = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream = True,
            temperature = 0
        )

    try:
        for chunk in complet:
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            yield '{}'.format(chunk_message)
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503
    
def tokenDes(token):

    connection =mysql.connector.connect(
        host = 'localhost',
        user='root',
        password='',
        database='workspace'
    )

    cursor = connection.cursor()

    query = "SELECT * FROM metaofcoin WHERE name = '{}'".format(token)

    cursor.execute(query)
    res = cursor.fetchall()

    messages = []
    system_message = {"role": "system", "content":prompts.tokenDes_system_message.format(token)}
    messages.insert(0, system_message) 
    messages.append({"role": "user", "content":prompts.tokenDes_user_message.format(res)})
    print("messages", messages)
    complet = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream = True,
            temperature = 0
        )

    try:
        for chunk in complet:
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            yield '{}'.format(chunk_message)
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503

def marketStatus():

    connection =mysql.connector.connect(
        host = 'localhost',
        user='root',
        password='',
        database='workspace'
    )

    cursor = connection.cursor()

    
    query_1 = "SELECT SUM(market_cap) AS total_market_cap, SUM(volume_24h) AS total_volume FROM current_status_of_tokens_coinmarketcap ORDER BY total_market_cap DESC LIMIT 10;"
    query_2 = "SELECT name, symbol FROM current_status_of_tokens_coinmarketcap ORDER BY market_cap DESC LIMIT 10;"
    query_3 = "SELECT name, symbol, percent_change_24h FROM latest_trending_tokens_coinmarketcap WHERE percent_change_24h IS NOT NULL ORDER BY percent_change_24h DESC LIMIT 5;"
    query_4 = "SELECT name, symbol, percent_change_24h FROM latest_trending_tokens_coinmarketcap WHERE percent_change_24h IS NOT NULL ORDER BY percent_change_24h ASC LIMIT 5;"

    query_5 = "SELECT name, symbol, date_added FROM new_listings_tokens_coinmarketcap WHERE date_added >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);"
    query_6 = "SELECT name, tvl FROM tvl_chains_defillama ORDER BY tvl DESC LIMIT 10;"
    query_7 = "SELECT name, symbol, percent_change_7d FROM new_listings_tokens_coinmarketcap ORDER BY percent_change_7d DESC LIMIT 10;"
    query_8 = "SELECT name, tvl FROM protocols_defillama ORDER BY tvl DESC LIMIT 5;"
    query_9 = "SELECT name, change_7d FROM protocols_defillama ORDER BY change_7d DESC LIMIT 5;"
    query_10 = "SELECT symbol, name, token_symbol_1, token_name_1, token_price_1, token_percent_1, token_symbol_2, token_name_2, token_price_2, token_percent_2, token_symbol_3, token_name_3, token_price_3, token_percent_3, token_symbol_4, token_name_4, token_price_4, token_percent_4, token_symbol_5, token_name_5, token_price_5, token_percent_5 FROM trending_tokens_defined WHERE name IN ('Arbitrum', 'Ethereum');"
    
    cursor.execute(query_1)
    res_1 = cursor.fetchall()

    cursor.execute(query_2)
    res_2 = cursor.fetchall()

    cursor.execute(query_3)
    res_3 = cursor.fetchall()

    cursor.execute(query_4)
    res_4 = cursor.fetchall()

    cursor.execute(query_5)
    res_5 = cursor.fetchall()
    
    cursor.execute(query_6)
    res_6 = cursor.fetchall()

    cursor.execute(query_7)
    res_7 = cursor.fetchall()

    cursor.execute(query_8)
    res_8 = cursor.fetchall()

    cursor.execute(query_9)
    res_9 = cursor.fetchall()

    cursor.execute(query_10)
    res_10 = cursor.fetchall()

    messages = []
    system_message = {"role": "system", "content":prompts.marketStatus_system_message}
    messages.insert(0, system_message) 
    messages.append({"role": "user", "content":prompts.marketStatus_user_message.format(res_1, res_2, res_3, res_4, res_5, res_6, res_7, res_8, res_9, res_10)})
    print("messages", messages)
    complet = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream = True,
            temperature = 0
        )
    try:
        for chunk in complet:
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            yield '{}'.format(chunk_message)
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503

def trendingToken():
    # Connect to the database and retrieve token data
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='workspace'
    )
    cursor = connection.cursor()
    query = "SELECT s AS symbol, n AS name FROM coins WHERE chains LIKE '%Ethereum%' OR chains LIKE '%Arbitrum%' ORDER BY gs DESC LIMIT 10;"
    cursor.execute(query)
    token_data = cursor.fetchall()
    
    # Format token data as a string
    formatted_data = ""
    for token in token_data:
        formatted_data += f"{token[0]} - {token[1]}\n"

    # Generate response using OpenAI Chat Completion
    messages = [
        {"role": "system", "content": prompts.trendingToken_system_message},
        {"role": "user", "content": formatted_data}
    ]
    complet = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
        temperature=0
    )
    try:
        for chunk in complet:
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            yield '{}'.format(chunk_message)
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503

def coinoftheday():
    # Connect to the database and retrieve token data
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='workspace'
    )
    cursor = connection.cursor()
    query = "SELECT * FROM coin_of_the_day_info ORDER BY last_cotd DESC LIMIT 1;"
    cursor.execute(query)
    token_data = cursor.fetchall()

    token_data = [
    {'id': row[0], 'last_cotd': float(row[1]), 'coin_name': row[2]}
    for row in token_data
]
    # Generate response using OpenAI Chat Completion
    messages = [
        {"role": "system", "content": "You have to response like this: ... ()is the the coin of the day"},
        {"role": "user", "content": json.dumps(token_data)}
    ]
    complet = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
        temperature=0
    )
    try:
        for chunk in complet:
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            yield '{}'.format(chunk_message)
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503

def AltRank():
    # Connect to the database and retrieve token data
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='workspace'
    )
    cursor = connection.cursor()
    query = "SELECT s, pc7d AS symbol, pc7d, n AS name FROM coins ORDER BY acr ASC LIMIT 10;"
    cursor.execute(query)
    token_data = cursor.fetchall()
    
    # Format token data as a string
    formatted_data = ""
    for token in token_data:
        formatted_data += f"{token[0]} ({token[1]})\n"

    # Generate response using OpenAI Chat Completion
    messages = [
        {"role": "system", "content": prompts.AltRank_system_message},
        {"role": "user", "content": formatted_data}
    ]
    complet = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
        temperature=0
    )
    try:
        for chunk in complet:
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            yield '{}'.format(chunk_message)
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503

def get_response(user_input, query):
    # print("user:", user_input)
    connection =mysql.connector.connect(
        host = 'localhost',
        user='root',
        password='',
        database='workspace'
    )

    cursor = connection.cursor()
    try:
        cursor.execute(query)
        res = cursor.fetchall()
        print("res", res)
        field_names = [desc[0] for desc in cursor.description]
        results = ""
        for row in res:
            for i, value in enumerate(row):
                if field_names[i] != 'id':
                    results += f"{field_names[i]}: {value}\n"

        messages = message_history.copy()
        system_message = {"role": "system", "content": prompts.admin_system_message}
        messages.insert(0, system_message)   
        messages.append({"role": "user", "content": "'question': " + user_input + "\n\n 'knowledge': " + str(results) + "Your response should contain all these results."})

        cursor.close()
        connection.close()
        
        complet = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream = True,
        )
        message_history.append({"role": "user", "content": user_input})
        message_history.append({"role": "user", "content": f"{str(results)}"})

        try:
            for chunk in complet:
                # collected_chunks.append(chunk)  # save the event response
                # chunk_message = chunk['choices'][0]['delta'].get("content", "")  # extract the message
                chunk_message = chunk['choices'][0]['delta'].get("content", "")

                print("asd", chunk_message)
                
                yield '{}'.format(chunk_message)
        except Exception as e:
            print("OpenAI Response (Streaming) Error: " + str(e))
            return 503

    except Exception as e:
        cursor.close()
        connection.close()
        results = query
              
        messages = message_history.copy()
        system_message = {"role": "system", "content": prompts.admin_system_message}
        messages.insert(0, system_message)  
        messages.append({"role": "user", "content": "'question': " + user_input + "\n\n 'knowledge': "})
        
        print("mmm--------\n", messages)
        complet = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream = True,
            temperature = 0
        )
        message_history.append({"role": "user", "content": user_input})

        try:
            for chunk in complet:
                # collected_chunks.append(chunk)  # save the event response
                # chunk_message = chunk['choices'][0]['delta'].get("content", "")  # extract the message
                chunk_message = chunk['choices'][0]['delta'].get("content", "")
                print(chunk_message)
                
                yield '{}'.format(chunk_message)
        except Exception as e:
            print("OpenAI Response (Streaming) Error: " + str(e))
            return 503

    return

def select_table(user_input):

    messages = message_history.copy()

    system_message = {"role": "system", "content": prompts.query_table_message}
    messages.insert(0, system_message)                             
    messages.append({"role": "user", "content": user_input})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature = 0,
        messages=messages,
    )
    response = completion.choices[0].message.content

    print("select_message", response)

    return response

def todayNews():
    # Connect to the database and retrieve token data
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='workspace'
    )
    cursor = connection.cursor()
    query = "SELECT title, description, source, news_link FROM crypto_news ORDER BY id DESC LIMIT 4;"
    cursor.execute(query)
    token_data = cursor.fetchall()
    
    # Format token data as a string
    formatted_data = ""
    for token in token_data:
        formatted_data += f"{token}\n"

    # Generate response using OpenAI Chat Completion
    messages = [
        {"role": "system", "content": prompts.news_system_message},
        {"role": "user", "content": formatted_data}
    ]
    complet = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
        temperature=0
    )
    try:
        for chunk in complet:
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            yield '{}'.format(chunk_message)
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503

def get_query(user_input):
    select = select_table(user_input)
    print("select", select)
    
    messages = message_history.copy()

    if select == '1':
        system_message = {"role": "system", "content": prompts.query_system_message[0]}
        messages.insert(0, system_message)                             
    elif select == '2':
        system_message = {"role": "system", "content": prompts.query_system_message[1]}
        messages.insert(0, system_message)
    elif select == '3':
        system_message = {"role": "system", "content": prompts.query_system_message[2]}
        messages.insert(0, system_message)  
    elif select == '4':
        system_message = {"role": "system", "content": prompts.query_system_message[3]}
        messages.insert(0, system_message)  
    elif select == '5':
        system_message = {"role": "system", "content": prompts.query_system_message[4]}
        messages.insert(0, system_message)    
    elif select == '6':
        system_message = {"role": "system", "content": prompts.query_system_message[5]}
        messages.insert(0, system_message)  
    elif select == '7':
        system_message = {"role": "system", "content": prompts.query_system_message[6]}
        messages.insert(0, system_message)  
    elif select == '8':
        system_message = {"role": "system", "content": prompts.query_system_message[7]}
        messages.insert(0, system_message)  
    elif select == '9':
        system_message = {"role": "system", "content": prompts.query_system_message[8]}
        messages.insert(0, system_message)  
    elif select == '10':
        system_message = {"role": "system", "content": prompts.query_system_message[9]}
        messages.insert(0, system_message)
    elif select == '11':
        system_message = {"role": "system", "content": prompts.query_system_message[10]}
        messages.insert(0, system_message)  
    elif select == '12':
        system_message = {"role": "system", "content": prompts.query_system_message[11]}
        messages.insert(0, system_message)    
    elif select == '13':
        system_message = {"role": "system", "content": prompts.query_system_message[12]}
        messages.insert(0, system_message)  
    elif select == '14':
        system_message = {"role": "system", "content": prompts.query_system_message[13]}
        messages.insert(0, system_message)  
    elif select == '15':
        system_message = {"role": "system", "content": prompts.query_system_message[14]}
        messages.insert(0, system_message)  
    elif select == '16':
        system_message = {"role": "system", "content": prompts.query_system_message[15]}
        messages.insert(0, system_message)  
    elif select == '17':
        system_message = {"role": "system", "content": prompts.query_system_message[16]}
        messages.insert(0, system_message)   
    elif select == '18':
        system_message = {"role": "system", "content": prompts.query_system_message[17]}
        messages.insert(0, system_message)
    elif select == '0':
        system_message = {"role": "system", "content": ""}
        messages.insert(0, system_message)  

    messages.append({"role": "user", "content": user_input})
    
    print("------------------query messages------------\n", messages)
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        temperature = 0,
        messages=messages,
        # stream = True
        # messages = [{"role": role, "content": f"{var}"}]
    )
    # message_history.append({"role": "user", "content": user_input})
    response = completion.choices[0].message.content
    print("qqq", response)
    return response
