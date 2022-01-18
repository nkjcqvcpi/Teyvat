import pandas as pd
import os


class Generator:
    filename = 'loading_tips'
    langs = {'zh-CN': 'l_chinese'}

    def __init__(self, file, lang):
        self.lang = self.langs[lang]
        self.quotes = pd.read_excel(file, sheet_name=self.lang, header=None)

    def generate(self, path, fn=None):
        if not fn:
            fn = 'l_english'
        filename = self.filename + '_' + fn + '.yml'
        with open(os.path.join(path, filename), 'w', encoding='utf_8_sig') as f:
            f.write(fn + ':\n')
            for index, quote in self.quotes.iterrows():
                f.write(r' LOADING_TIP_{}:0 "{}\n- {}"'.format(index, quote[2], quote[0]) + '\n')


if __name__ == "__main__":
    g = Generator('ref/loading_tips.xlsx', 'zh-CN')
    g.generate('src/Teyvat/localisation/english')
