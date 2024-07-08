import numpy as np
import os
from openai import OpenAI
import random
from tqdm import tqdm

import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # give acess to parent dir
from tokenizer import get_tokenizer

client = OpenAI(api_key="API_KEY")
enc = get_tokenizer()

convs = []

NUM_PROBLEMS = 100

i = 0
# Nonword problems
for i in tqdm(range(NUM_PROBLEMS//2), desc="Generating Nonword Problems"):
    if i >= NUM_PROBLEMS//4:
        difficulty = "simple"
    else:
        difficulty = "complex"

    options = ["", "Can you solve: ", "Compute: ", "Do this problem: ", "What is this: "]
    primer = random.choice(options)

    prompt = f"Give me {difficulty} math expressions (not word problems) - don't say anything other than the word problem - then put a <|sep|> between the question and the answer which should be written as a calculation. For example 2+2. The calculation should just be a single long expression - it should work in python's eval() so use math.sqrt()"
    
    try:
        response = client.chat.completions.create(model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        response = response.choices[0].message.content.split("<|sep|>")
        response[1] = response[1].replace("\n", "")
        user, assistant = enc.encode(f"<|user|>{primer}{response[0]}", allowed_special={"<|user|>"}), enc.encode(f"<|assistant|><|calc|>{response[1]}<|/calc|>", allowed_special={"<|assistant|>", "<|calc|>", "<|/calc|>"})
        conv = [[user], [assistant]]
        convs.append(conv)
    except Exception as e:
        print(e)

# Word problems
for i in tqdm(range(NUM_PROBLEMS//2), desc="Generating Word Problems"):
    if i >= NUM_PROBLEMS//4:
        difficulty = "simple"
    else:
        difficulty = "complex"

    prompt = f"Generate a {difficulty} math word problem involving the basic math operations (+, -, *, /, ^, sqrt()) - don't say anything other than the word problem - then put a <|sep|> between the question and the answer which should be written as a calculation. For example 2+2. The calculation should just be a single long expression - it should work in python's eval() so use math.sqrt()"

    try:
        response = client.chat.completions.create(model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        response = response.choices[0].message.content.split("<|sep|>")
        response[1] = response[1].replace("\n", "")
        user, assistant = enc.encode(f"<|user|>{response[0]}", allowed_special={"<|user|>"}), enc.encode(f"<|assistant|><|calc|>{response[1]}<|/calc|>", allowed_special={"<|assistant|>", "<|calc|>", "<|/calc|>"})
        print(assistant)
        conv = [[user], [assistant]]
        convs.append(conv)
    except Exception as e:
        print(e)

convs = np.array(convs, dtype=object)
np.save("math_finetune.npy", convs)