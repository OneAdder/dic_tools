import pandas as pd
import re

def rev(word):
    new_word = list(word)
    new_word.reverse()
    return ''.join(new_word)

def cut_plural_form(article):
    try:
        form = re.findall(', -(.*?) ', article)[0]
    except IndexError:
        form = ''
    return form

vowels = 'уеыаоэяию'

def decide_stem_type(word, plural_form):
    """
    0 -- не дана форма множественного числа
    1 -- основа на согласный
    2 -- основа на беглый гласный
    3 -- основа на гласный
    """
    '''
    if plural_form.empty or plural_form == ' ':
        return 0
    '''
    try:
        if word[-1] in vowels:
            if plural_form[0] in vowels:
                return 3
            else:
                if '|' in word:
                    return 2
                else:
                    return 3
        else:
            #Это чтобы стриггерить исключение, если там ничего нет
            plural_form[0]
            return 1
    except (KeyError, IndexError):
        return 0

def test():
    print(decide_stem_type('ящик', 'т'))
    print(decide_stem_type('осё|л', 'лхт'))
    print(decide_stem_type('сянго|рь', 'рьхт'))
    print()

    print(decide_stem_type('суз|а', 'т'))
    print(decide_stem_type('толвал|да', 'тт'))
    print(decide_stem_type('толвал|да', 'тт'))
    print()

    print(decide_stem_type('биржа', 'т'))
    print(decide_stem_type('пукш|а', 'ет'))
    print()

      
if __name__ == '__main__':
    #Читаем таблицу
    m = pd.read_csv('+msh-ru_30000.csv', delimiter='\t', header=0)
    m.fillna('', inplace=True)

    #Обрежем до существительных
    nouns_only = m[m['Части речи, etc.'] == 'S']

    #Обрежем номилализации
    nouns_only = nouns_only[nouns_only['Словообразование, etc.'] != 'NZR']

    #Добавляем перевёрнутые слова для сортировки
    nouns_only = nouns_only.assign(reversed_words=list(map(rev, list(nouns_only['Слово']))))

    #Сортируем по перевёрнутым словам
    sorted_df = nouns_only.sort_values('reversed_words')

    #Сохраняем в CSV
    sorted_df.to_csv('results/Мокша (обратный словрь существительных).csv', sep='\t')

    useful_df = pd.DataFrame()

    #Создаём датафрейм, где будет только интересующая нас информация
    useful_df = useful_df.assign(moksha_lemma=sorted_df['Слово'])
    useful_df = useful_df.assign(plural_form=list(map(cut_plural_form, list(sorted_df['Словарная статья']))))
    useful_df = useful_df.assign(marks=sorted_df['Диалектные и стилистические пометы'])
    useful_df = useful_df.assign(full_article=sorted_df['Словарная статья'])

    #Сохраняем в CSV
    useful_df.to_csv('results/Существительные и формы множественного числа.csv', sep='\t')

    #Возьмём типы основ
    stem_types = [decide_stem_type(*word) for word in zip(useful_df['moksha_lemma'], useful_df['plural_form'])]

    #Добавим типы основ
    useful_df = useful_df.assign(stem_type=stem_types)

    consonants = pd.DataFrame()
    consonants = consonants.assign(consonant_lemma=useful_df['moksha_lemma'][useful_df['stem_type']==1])
    consonants = consonants.assign(consonant_plural=useful_df['plural_form'][useful_df['stem_type']==1])
    consonants = consonants.assign(empty1='')

    hidden = pd.DataFrame()
    hidden = hidden.assign(hidden_vowel_lemma=useful_df['moksha_lemma'][useful_df['stem_type']==2])
    hidden = hidden.assign(hidden_vowel_plural=useful_df['plural_form'][useful_df['stem_type']==2])
    hidden = hidden.assign(empty2='')

    vowel_s = pd.DataFrame()
    vowel_s = vowel_s.assign(vowel_lemma=useful_df['moksha_lemma'][useful_df['stem_type']==3])
    vowel_s = vowel_s.assign(vowel_plural=useful_df['plural_form'][useful_df['stem_type']==3])
    vowel_s = vowel_s.assign(empty3='')

    unknown = pd.DataFrame()
    unknown = unknown.assign(unknown_lemma=useful_df['moksha_lemma'][useful_df['stem_type']==0])

    consonants.to_csv('results/consonant_stems.csv', sep='\t')
    hidden.to_csv('results/hidden_vowel_stems.csv', sep='\t')
    vowel_s.to_csv('results/vowel_stems.csv', sep='\t')
    unknown.to_csv('results/unknown.csv', sep='\t')
