# -*- coding: utf-8 -*-

from openai import OpenAI

client = OpenAI(api_key='XXXXX')
import json

# Define your OpenAI API key

# Function to anonymize content
def get_coherent_answer(question, documents):
    prompt = f"""
        You are Jeremy howard. A tech educator with top to bottom explaining style. 
        A user has asked a question and in return some text chunks are provided to you. 
        Based on the question and text chunks write your answer. Use lists or styles to explain for text mode.
        The question is : {question} \n 
        The text chunks are : {
            [doc for doc in documents]        
        }
    """

    print(f"prompt: {prompt}")
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages = [
        {"role":"user", "content":prompt}
    ]                                              
)
    print(response.choices[0].message.content)
    return response.choices[0].message.content.strip()

# # Read the text file
# with open('anonymized_texts.txt', 'r', encoding='utf-8') as file:
#     lines = file.readlines()

# # Process each line and save the results
# result = None
# with open('output.jsonl', 'w', encoding='utf-8') as jsonl_file:
#     for line in lines:
#         if line.strip():  # Ignore empty lines
#             try:
#                 anonymized_result = anonymize_content(line.strip())
#                 result = json.loads(anonymized_result)
#                 jsonl_file.write(json.dumps(result, ensure_ascii=False) + '\n')
#             except Exception as e:
#                 print(f"Error processing line: {line.strip()}")
#                 print(f"Result : {result}" )
#                 print(f"Error: {e}")

# print("Anonymization complete. Results saved to output.jsonl")

