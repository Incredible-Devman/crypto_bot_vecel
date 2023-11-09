# import streamlit as st
import openai
# from streamlit_chat import message
# import pinecone
import os
from Backend import prompts
import json

from dotenv import load_dotenv
load_dotenv()

# We will  pasting our openai credentials over here
openai.api_key = os.getenv("OPENAI_API_KEY")
# pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
# pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
# index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))
message_history = [{"role": "system", "content": prompts.auto_system_message}]


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


def get_message_history(contexts):
    message_hist = message_history
    message_hist.append([{"role": "user", "content": contexts}])

    return message_hist


def chat(var, message, role="user"):
    message_history.append({"role": role, "content": f"{var}"})
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        # model="gpt-3.5-turbo",
        messages=message,
        stream = True
        # messages = [{"role": role, "content": f"{var}"}]
    )
    # collected_chunks = []
    # reply = []
    try:
        for chunk in completion:
            # collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk['choices'][0]['delta'].get("content", "")  # extract the message
            # reply.append(chunk_message)  # save the message
            # print(f"{chunk_message}")  # print the delay and text
            yield chunk_message
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        return 503
    # print("chat: ", completion)
    # reply = completion.choices[0].message.content
    # message_history.append({"role": "assistant", "content": f"{reply}"})
    # return reply


def get_response(user_input):
    context, score = find_top_match(user_input, 1)
    print("pinecone", context[0])

    # Generate human prompt template and convert to API message format
    query_with_context = prompts.human_template.format(query=user_input, context=context[0])

    # Convert chat history to a list of messages
    messages = [{"role": "system", "content": prompts.auto_system_message}]
    messages.append({"role": "user", "content": query_with_context})

    # response = chat(user_input, messages)
    # return response

    message_history.append({"role": "user", "content": f"{user_input}"})
    completion = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model="gpt-4",
        messages=messages,
        stream = True
        # messages = [{"role": role, "content": f"{var}"}]
    )
    # collected_chunks = []
    # reply = []
    return completion['choices'][0]['message']['content']
        # for chunk in completion:
        #     # collected_chunks.append(chunk)  # save the event response
        #     chunk_message = chunk['choices'][0]['delta'].get("content", "")  # extract the message
        #     words = []

            
        #     for message in chunk_message:
        #         words.extend(message.split())
        #     # reply.append(chunk_message)  # save the message
        #     # print(f"{chunk_message}")  # print the delay and text
        #     yield 'data: {} \n\n'.format(chunk_message)

    

def get_auto_response(user_input, email) :
    # global level, level_id, engage_id
    messages = message_history.copy()
    messages.append({"role": "user", "content": user_input})
    # messages.append({"role": "user", "content": user_input + "\n\n" + "Please review the sentences above and respond similar to the examples provided below and additionally, kindly conclude your response with a short agreement or acknowledgement of understanding with at most 5 tokens. \n\n" + "'" + reply + "'" + "\n\n"})
    print("message, ", messages)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        # stream = True
        # messages = [{"role": role, "content": f"{var}"}]
    )
    # print('res', completion['choices'][0]['message']['content'])
    res = completion['choices'][0]['message']['content']
    message_history.append({"role": "user", "content": f"{user_input}"})
    message_history.append({"role" : "assistant", "content" : res})
    return res
