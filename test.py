import tiktoken

gpt2_enc = tiktoken.get_encoding("gpt2")

# In production, load the arguments directly instead of accessing private attributes
# See openai_public.py for examples of arguments for specific encodings
enc = tiktoken.Encoding(
    # If you're changing the set of special tokens, make sure to use a different name
    # It should be clear from the name what behaviour to expect.
    name="gpt2-chat",
    pat_str=gpt2_enc._pat_str,
    mergeable_ranks=gpt2_enc._mergeable_ranks,
    special_tokens={
        **gpt2_enc._special_tokens,
        "<|pad|>": 50257,
        "<|user|>": 50258,
        "<|assistant|>": 50259,
        "<|calc|>": 50260,
        "<|/calc|>": 50261,
        "<|day|>": 50262,
        "<|time|>": 50263,
    }
)

print(enc.decode([50263]))