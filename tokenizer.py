import tiktoken
from tiktoken.load import data_gym_to_mergeable_bpe_ranks

def get_tokenizer():
    return tiktoken.Encoding(
            name="finngpt",
            pat_str=r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""",
            mergeable_ranks = data_gym_to_mergeable_bpe_ranks(
                vocab_bpe_file="https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/vocab.bpe",
                encoder_json_file="https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/encoder.json",
                vocab_bpe_hash="1ce1664773c50f3e0cc8842619a93edc4624525b728b188a9e0be33b7726adc5",
                encoder_json_hash="196139668be63f3b5d6574427317ae82f612a97c5d1cdaf36ed2256dbf636783",
            ),
            special_tokens={
                "<|endoftext|>": 50256,
                "<|pad|>": 50257,
                "<|user|>": 50258,
                "<|assistant|>": 50259,
                "<|calc|>": 50260,
                "<|/calc|>": 50261,
            }
        )