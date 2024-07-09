import json
import re
import os
import numpy as np
from openai import OpenAI
from tqdm import tqdm
import random
import math # for eval

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # give acess to parent dir
from tokenizer import get_tokenizer

NUM_NONWORD = 50

enc = get_tokenizer()

def format_word_problems(problems, split):
    formatted = []
    for problem in tqdm(problems, desc=f"Formatting {split} word problems"):
        # Format question
        question = problem["Problem"]

        # Handle spacing
        question = re.sub(r'\s+([.,?!])', r'\1', question) # Remove spaces before punctuation
        question = re.sub(r'(\d+)\s*%', r'\1%', question) # Remove space before percentage
        question = re.sub(r'(\w+)\s*\'\s*(\w+)', r"\1'\2", question) # Fix apostrophes
        question = re.sub(r'(?<=\w)([.,?!])(?=\w)', r'\1 ', question) # Add space after punctuation if followed by a word

        question = question.replace("rs. ", "") # Remove rs
        # Handle capitalization
        sentences = question.split('.')
        capitalized_sentences = [sentence.strip().capitalize() for sentence in sentences if sentence.strip()]
        question = '. '.join(capitalized_sentences) + ('.' if question.endswith('.') else '')

        # Format answer
        formula = problem["annotated_formula"]
        formula = re.sub(r'const_(\d+)_?(\d*)', lambda m: f'.{m.group(2)}' if m.group(2) else m.group(1), formula)
        for _ in range(formula.count("add")):
            formula = re.sub(r"add\((.*?),\s*(.*?)\)", r"(\1 + \2)", formula)

        for _ in range(formula.count("subtract")):
            formula = re.sub(r"subtract\((.*?),\s*(.*?)\)", r"(\1 - \2)", formula)

        for _ in range(formula.count("multiply")):
            formula = re.sub(r"multiply\((.*?),\s*(.*?)\)", r"(\1 * \2)", formula)

        for _ in range(formula.count("divide")):
            formula = re.sub(r"divide\((.*?),\s*(.*?)\)", r"(\1 / \2)", formula)

        try:
            eval(formula)
        except:
            continue
        # Make conversation
        user = enc.encode(f"<|user|>{question}", allowed_special={'<|user|>'})
        assistant = enc.encode(f"<|assistant|>The answer is <calc>{formula}</calc>", allowed_special={'<|assistant|>'})
        formatted.append([[user], [assistant]])
    return formatted

def get_nonword_problems(num, split):
    problems = []
    # Nonword problems
    for i in tqdm(range(num), desc=f"Generating {split} nonword problems"):
        if i >= num//2:
            difficulty = "simple"
        else:
            difficulty = "complex"

        options = ["", "Can you solve: ", "Compute: ", "Do this problem: ", "What is this: "]
        primer = random.choice(options)

        prompt = f"Generate a {difficulty} math problem involving the basic math operations (+, -, *, /, **, math.sqrt()) - just provide the raw expression, don't say anything else"
        
        try:
            response = client.chat.completions.create(model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ])

            response = response.choices[0].message.content
            # make sure valid
            eval(response)

            user, assistant = enc.encode(f"<|user|>{primer}{response}", allowed_special={"<|user|>"}), enc.encode(f"<|assistant|><|calc|>{response}<|/calc|>", allowed_special={"<|assistant|>", "<|calc|>", "<|/calc|>"})
            conv = [[user], [assistant]]
            problems.append(conv)
        except Exception as e:
            print(e)
    return problems


# Train
with open("train/data/raw_mathqa_train.json", "r") as file:
    train_word = json.load(file)
print(f"Num train word problems: {len(train_word)}")
train_word = format_word_problems(train_word, "train")
print(f"Num train processed: {len(train_word)}")

train_nonword = get_nonword_problems(NUM_NONWORD, "train")
print(f"Num numword: {len(train_nonword)}")

train_problems = train_word + train_nonword
train_problems = np.array(train_problems, dtype=object)
np.random.shuffle(train_problems)

# Val
with open("train/data/raw_mathqa_val.json", "r") as file:
    val_word = json.load(file)
print(f"Num val word problems: {len(val_word)}")
val_word = format_word_problems(val_word, "val")
print(f"Num val processed: {len(val_word)}")

val_nonward = get_nonword_problems(NUM_NONWORD//10, "val")
print(f"Num nonwordd: {len(val_nonward)}")

val_problems = val_word + val_nonward
val_problems = np.array(val_problems, dtype=object)
np.random.shuffle(val_problems)

np.save("train/data/mathqa_train.npy", train_problems)
np.save("train/data/mathqa_val.npy", val_problems)