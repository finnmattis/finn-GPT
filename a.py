import tiktoken
enc = tiktoken.get_encoding("gpt2")
a = enc.encode("This book was published in 1936, by the Institute of American Ethnology, and has since been reprinted in many languages.<|endoftext|>")
enc.decode(a[-1])