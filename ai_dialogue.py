from typing import Optional
from numpy import histogram
import paddle
from paddlenlp.transformers import (UnifiedTransformerLMHeadModel,
                                    UnifiedTransformerTokenizer)

from utils import print_args, set_seed, select_response


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


@singleton
class DialogueBot:
    def __init__(self, model_name_or_path="plato-mini") -> None:
        self.seed = None
        self.min_dec_len = 1
        self.max_dec_len = 64
        self.num_return_sequences = 20
        self.decode_strategy = 'sampling'
        self.top_k = 5
        self.temperature = 1.0
        self.top_p = 1.0
        self.num_beams = 0
        self.length_penalty = 1.0
        self.early_stopping = False
        self.device = 'cpu'
        self.model = UnifiedTransformerLMHeadModel.from_pretrained(
            model_name_or_path)
        self.tokenizer = UnifiedTransformerTokenizer.from_pretrained(
            model_name_or_path)
        self.history = []

    def history_clean(self):
        del self.history[:]

    def response(self, input: Optional[str]) -> Optional[str]:
        print(self.history)
        self.history.append(input)
        inputs = self.tokenizer.dialogue_encode(
            self.history,
            add_start_token_as_response=True,
            return_tensors=True,
            is_split_into_words=False)
        inputs['input_ids'] = inputs['input_ids'].astype('int64')
        ids, scores = self.model.generate(
            input_ids=inputs['input_ids'],
            token_type_ids=inputs['token_type_ids'],
            position_ids=inputs['position_ids'],
            attention_mask=inputs['attention_mask'],
            max_length=self.max_dec_len,
            min_length=self.min_dec_len,
            decode_strategy=self.decode_strategy,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            num_beams=self.num_beams,
            length_penalty=self.length_penalty,
            early_stopping=self.early_stopping,
            num_return_sequences=self.num_return_sequences)
        bot_response = select_response(
            ids,
            scores,
            self.tokenizer,
            self.max_dec_len,
            self.num_return_sequences,
            keep_space=False)[0]
        self.history.append(bot_response)
        return bot_response

if __name__ == '__main__':
    bot = DialogueBot()
    print('----------------------')
    print(bot.response("你好"))
    print(bot.response("你多大了？"))


