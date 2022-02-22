import json
import re
from collections import Counter
from pathlib import Path
from typing import Union

import arabic_reshaper
import demoji
#from bidi.algorithm import get_display
import matplotlib.pyplot as plt
from hazm import Lemmatizer, Normalizer, Stemmer, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud


class chatstatistics:
    """ Generates Word Cloud from Telegram chat
    """
    def __init__(self,chat_json: Union[str, Path]):
        """: param: chat_json: Telegram json file 
        """
 #Load Chat Data and Stop Words
        logger.info(f'Load Chat Data from {chat_json} and Stop Words')
        with open(str(Path(chat_json))) as f:
            self.chat_data=json.load(f)
            stop_word = open(str(Path(DATA_DIR)/'stopword.txt')).readlines()
            stop_word = list(map(str.strip,stop_word))
            self.normalizer = Normalizer()
            self.stop_word = list(map(self.normalizer.normalize,stop_word))

    def generate_word_cloud(
        self,
        output_dir: Union[str, Path],
        width : int = 1200, height : int = 800,
        ):
        """ Generate word Cloud from json file
        : param: output_dir: directory of output png file
        """
    # Generate Text Content
        logger.info('Loading Text Content ...')
        text_content=''
        for msg in self.chat_data['messages']:
            if type(msg['text']) is str:
                tokens=word_tokenize(msg['text'])
                tokens=list(filter(lambda item: item not in self.stop_word,tokens))
                text_content += f"{' '.join(tokens)}"
    # Delete annoying character
        re_pattern = re.compile(pattern="["
                        "\u2069"
                        "\u2066"
                        "]+",
                        flags=re.UNICODE)
        text_content=re_pattern.sub(r' ',text_content)
        text_content=demoji.replace(text_content," ")

    # Normalize Text Content
        text_content = self.normalizer.normalize(text_content)
        stemmer = Stemmer()
        stemmer.stem(text_content)
        lemmatizer = Lemmatizer()
        lemmatizer.lemmatize(text_content)

    # reshape Farsi Characters
        text_content=arabic_reshaper.reshape(text_content)
    #text_content=get_display(text_content)

    # Final Word Cloud
        logger.info('Generating Word Cloud ...')
        tokens=word_tokenize(text_content)
        wordcloud=WordCloud(
            width = 1200, height = 800,
            font_path=str(Path(DATA_DIR)/'Vazir.ttf'),
        background_color='white').generate(text_content)
        plt.imshow(wordcloud,interpolation='bilinear')
        plt.axis("off")
        logger.info(f'Saving Word Cloud to {output_dir}')
        wordcloud.to_file(str(Path(output_dir)/'WordCloud.png'))

if __name__=="__main__":
    chat_stats=chatstatistics(chat_json=str(Path(DATA_DIR)/'My_One_and_Only.json'))
    chat_stats.generate_word_cloud(output_dir=str(Path(DATA_DIR)))
    print('Done!')
