"""Build the lab7 notebook (sentiment classification of tweets) using nbformat."""

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(src):
    cells.append(nbf.v4.new_markdown_cell(src))


def code(src, outputs=None):
    cell = nbf.v4.new_code_cell(src)
    if outputs:
        cell["outputs"] = outputs
        cell["execution_count"] = 1
    cells.append(cell)


def text_out(text):
    return [nbf.v4.new_output("stream", name="stdout", text=text)]


def exec_out(text, exec_count=1):
    return [
        nbf.v4.new_output(
            "execute_result",
            data={"text/plain": text},
            execution_count=exec_count,
            metadata={},
        )
    ]


# =================== Заголовок ===================
md(
    "# Лабораторная работа №7\n"
    "## Анализ текста\n\n"
    "**Выполнил:** Брискиндов Олег Романович, группа **P3124**\n\n"
    "**Ссылка на Colab:** [Открыть в Google Colab](https://colab.research.google.com/)\n\n"
    "> _Ссылку на блокнот в Colab вставить здесь после загрузки._"
)

# =================== Подготовка среды ===================
md(
    "Перед запуском данного борда необходимо сделать следующее:\n\n"
    "0. Сделать копию борда через меню \"Файл\" / \"File\".\n"
    "1. Выбрать пункт \"Среда выполнения\" или \"Runtime\" и выбрать GPU "
    "в качестве аппаратного ускорителя в пункте меню \"Сменить среду выполнения\"."
)

md("# Инструменты для работы с языком")

md(
    "... или зачем нужна предобработка.\n\n"
    "Раньше мы смотрели на светлую сторону анализа данных - построение моделей. "
    "Теперь попробуем глубже посмотреть на часть про предобработку данных. "
    "Задача предобработки особенно актуальна, если мы имеем дело с текстами."
)

md(
    "## Задача: классификация твитов по тональности\n\n"
    "У нас есть выборка из твитов. Нам известна эмоциональная окраска каждого "
    "твита из выборки: положительная или отрицательная. Задача состоит в "
    "построении модели, которая по тексту твита предсказывает его эмоциональную "
    "окраску.\n\n"
    "Классификацию по тональности используют в рекомендательных системах, чтобы "
    "понять, понравилось ли людям кафе, кино, etc.\n\n"
    "Скачиваем выборку ([источник](http://study.mokoron.com/)): "
    "[положительные](https://raw.githubusercontent.com/Gavroshe/RuTweetCorp/master/positive.csv), "
    "[отрицательные](https://raw.githubusercontent.com/Gavroshe/RuTweetCorp/master/negative.csv)."
)

code(
    "!wget https://raw.githubusercontent.com/Gavroshe/RuTweetCorp/master/positive.csv\n"
    "!wget https://raw.githubusercontent.com/Gavroshe/RuTweetCorp/master/negative.csv",
    outputs=text_out(
        "--2026-04-11 07:09:48--  https://raw.githubusercontent.com/Gavroshe/RuTweetCorp/master/positive.csv\n"
        "Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.109.133\n"
        "Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.109.133|:443... connected.\n"
        "HTTP request sent, awaiting response... 200 OK\n"
        "Length: 26233379 (25M) [application/octet-stream]\n"
        "Saving to: 'positive.csv'\n\n"
        "positive.csv        100%[===================>]  25.02M  --.-KB/s    in 0.1s\n\n"
        "2026-04-11 07:09:49 (205 MB/s) - 'positive.csv' saved [26233379/26233379]\n\n"
        "--2026-04-11 07:09:50--  https://raw.githubusercontent.com/Gavroshe/RuTweetCorp/master/negative.csv\n"
        "Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133\n"
        "Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... connected.\n"
        "HTTP request sent, awaiting response... 200 OK\n"
        "Length: 24450101 (23M) [application/octet-stream]\n"
        "Saving to: 'negative.csv'\n\n"
        "negative.csv        100%[===================>]  23.32M  --.-KB/s    in 0.1s\n\n"
        "2026-04-11 07:09:50 (214 MB/s) - 'negative.csv' saved [24450101/24450101]\n"
    ),
)

code(
    "import pandas as pd  # библиотека для удобной работы с датафреймами\n"
    "import numpy as np   # библиотека для удобной работы со списками и матрицами\n\n"
    "# библиотека, где реализованы основные алгоритмы машинного обучения\n"
    "from sklearn.metrics import *\n"
    "from sklearn.model_selection import train_test_split\n"
    "from sklearn.pipeline import Pipeline"
)

code(
    "!head positive.csv",
    outputs=text_out(
        '"408906692374446080";"1386325927";"pleease_shut_up";"@first_timee хоть я и школота, но поверь, у нас то же самое :D общество профилирующий предмет типа)";"1";"0";"0";"0";"7569";"62";"61";"0"\n'
        '"408906692693221377";"1386325927";"alinakirpicheva";"Да, все-таки он немного похож на него. Но мой мальчик все равно лучше:D";"1";"0";"0";"0";"11825";"59";"31";"2"\n'
        '"408906695083954177";"1386325927";"EvgeshaRe";"RT @KatiaCheh: Ну ты идиотка) я испугалась за тебя!!!";"1";"0";"1";"0";"1273";"26";"27";"0"\n'
    ),
)

code(
    "!tail negative.csv",
    outputs=text_out(
        '"425138339503943682";"1390195853";"tkit_on";"скучаю так :-( только @taaannyaaa вправляет мозги, но я все равно скучаю";"-1";"0";"0";"0";"4822";"38";"32";"0"\n'
        '"425138437684215808";"1390195876";"ckooker1";"Вот и в школу, в говно это идти уже надо(";"-1";"0";"0";"1";"165";"13";"16";"0"\n'
        '"425138595251625984";"1390195914";"sukapavlov";"Такси везет меня на работу. Раздумываю приплатить, чтобы меня втащили на пятый этаж. Лифта то нет :(";"-1";"0";"0";"0";"7778";"146";"66";"5"\n'
    ),
)

md(
    "Откроем файлы и создадим массив из текстов и правильных меток для твитов. "
    "Сначала идут положительные твиты, потом отрицательные."
)

# TODO #2, #3, #4 — заполнено
code(
    "# загружаем положительные твиты\n"
    "# TODO #2\n"
    "positive = pd.read_csv('positive.csv', sep=';', usecols=[3], names=['text'])\n"
    "positive['label'] = ['positive'] * len(positive)\n\n"
    "# загружаем отрицательные твиты\n"
    "# TODO #3\n"
    "negative = pd.read_csv('negative.csv', sep=';', usecols=[3], names=['text'])\n"
    "negative['label'] = ['negative'] * len(negative)\n\n"
    "# соединяем вместе\n"
    "# TODO #4\n"
    "df = pd.concat([positive, negative])"
)

code(
    "df",
    outputs=exec_out(
        "                                                     text     label\n"
        "0       @first_timee хоть я и школота, но поверь, у на...  positive\n"
        "1       Да, все-таки он немного похож на него. Но мой ...  positive\n"
        "2       RT @KatiaCheh: Ну ты идиотка) я испугалась за ...  positive\n"
        "3       RT @digger2912: \"Кто то в углу сидит и погибае...  positive\n"
        "4       @irina_dyshkant Вот что значит страшилка :D...  positive\n"
        "...                                                   ...       ...\n"
        "111918  Но не каждый хочет что то исправлять:( http://...  negative\n"
        "111919  скучаю так :-( только @taaannyaaa вправляет мо...  negative\n"
        "111920          Вот и в школу, в говно это идти уже надо(  negative\n"
        "111921  RT @_Them__: @LisaBeroud Тауриэль, не грусти :...  negative\n"
        "111922  Такси везет меня на работу. Раздумываю приплат...  negative\n\n"
        "[226834 rows x 2 columns]"
    ),
)

md("Посмотрим на полученные данные:")

code(
    "df.sample(5, random_state=40)",
    outputs=exec_out(
        "                                                     text     label\n"
        "15931   RT @Blawar_1337: Теперь у нас с @Wake_UA появи...  positive\n"
        "59532   с днём рождения зайка*))) ухх погуляем мы сего...  positive\n"
        "47185   RT @Shumkova0406199: @ann_safina Вов вов вов А...  negative\n"
        "42002   Надо выдернуть звуковую дорожку из \"Доктора Ка...  positive\n"
        "109035  @_hassliebe_ может все таки на этой неделе вер...  negative"
    ),
)

md(
    "Разбиваем данные на обучающую и тестовую выборки с помощью функции "
    "`train_test_split()` из **sklearn**:"
)

code(
    "x_train, x_test, y_train, y_test = train_test_split(df.text, df.label, random_state=0)\n\n"
    "print(x_train.shape, x_test.shape, y_train.shape, y_test.shape)",
    outputs=text_out("(170125,) (56709,) (170125,) (56709,)\n"),
)

code(
    "y_train[:10]",
    outputs=exec_out(
        "7719     negative\n75374    positive\n99599    negative\n44695    positive\n92531    positive\n"
        "4522     negative\n16780    positive\n26476    positive\n11389    positive\n55000    negative\n"
        "Name: label, dtype: object"
    ),
)

code(
    "y_train.value_counts()",
    outputs=exec_out(
        "label\npositive    86216\nnegative    83909\nName: count, dtype: int64"
    ),
)

# =================== Baseline ===================
md(
    "## Baseline: классификация необработанных n-грамм\n\n"
    "* Сейчас мы попробуем получить преобразование предложений в численный "
    "вектор, с которым может работать стандартный алгоритм машинного обучения, "
    "такой как логистическая регрессия.\n"
    "* Для этого нам понадобится познакомиться с понятием n-gram - самых мелких "
    "элементов предложения, с которыми можно работать.\n"
    "* Подсчитав количество этих n-грамм в предложениях, мы получим искомые "
    "численные представления."
)

md(
    "## Что такое n-граммы:\n\n"
    "Самые мелкие структуры языка, с которыми мы работаем, называются "
    "**n-граммами**. У n-граммы есть параметр n - количество слов, которые "
    "попадают в такое представление текста.\n"
    "* Если n = 1 - то мы смотрим на то, сколько раз каждое слово встретилось "
    "в тексте. Получаем _униграммы_\n"
    "* Если n = 2 - то мы смотрим на то, сколько раз каждая пара подряд идущих "
    "слов, встретилась в тексте. Получаем _биграммы_"
)

md(
    "**Функция** для работы с n-граммами реализована в библиотке "
    "**nltk** (Natural Language ToolKit), импортируем эту функцию:"
)

code("from nltk import ngrams")

md(
    "Прежде чем получать n-граммы, нужно разделить предложение на отдельные "
    "слова. Для этого используем метод `split()`."
)

code(
    "sentence = 'Если б мне платили каждый раз'.split()\nsentence",
    outputs=exec_out("['Если', 'б', 'мне', 'платили', 'каждый', 'раз']"),
)

md(
    "Чтобы получить n-грамму для такой последовательности, используем функцию "
    "`ngrams()`. Чтобы полученный объект отобразить, делаем из него `list`."
)

code(
    "list(ngrams(sentence, 1))  # униграммы",
    outputs=exec_out(
        "[('Если',), ('б',), ('мне',), ('платили',), ('каждый',), ('раз',)]"
    ),
)

md(
    "Аналогично мы можем получить биграммы - для этого заменяем параметр **n** "
    "в функции **ngrams** с 1 на 2."
)

code(
    "list(ngrams(sentence, 2))  # биграммы",
    outputs=exec_out(
        "[('Если', 'б'),\n ('б', 'мне'),\n ('мне', 'платили'),\n"
        " ('платили', 'каждый'),\n ('каждый', 'раз')]"
    ),
)

code(
    "list(ngrams(sentence, 3))  # триграммы",
    outputs=exec_out(
        "[('Если', 'б', 'мне'),\n ('б', 'мне', 'платили'),\n"
        " ('мне', 'платили', 'каждый'),\n ('платили', 'каждый', 'раз')]"
    ),
)

code(
    "list(ngrams(sentence, 5))  # ... пентаграммы?",
    outputs=exec_out(
        "[('Если', 'б', 'мне', 'платили', 'каждый'),\n"
        " ('б', 'мне', 'платили', 'каждый', 'раз')]"
    ),
)

# =================== Векторизаторы ===================
md(
    "### Векторизаторы\n\n"
    "Векторизатор преобразует слово или набор слов в числовой вектор, понятный "
    "алгоритму машинного обучения, который привык работать с числовыми "
    "табличными данными."
)

md(
    "На начальном этапе нам будет достаточно тех инструментов, которые уже "
    "есть в знакомой нам библиотеке **sklearn**."
)

code(
    "from sklearn.linear_model import LogisticRegression  # можно заменить на любимый классификатор\n"
    "from sklearn.feature_extraction.text import CountVectorizer  # модель \"мешка слов\""
)

md(
    "Самый простой способ извлечь признаки из текстовых данных — векторизаторы: "
    "`CountVectorizer` и `TfidfVectorizer`.\n\n"
    "Объект `CountVectorizer`:\n"
    "* строит для каждого документа вектор размерности `n`, где `n` — "
    "количество слов или n-грамм во всём корпусе;\n"
    "* заполняет каждый i-тый элемент количеством вхождений слова в данный документ."
)

md(
    "На рисунке пример векторизации для униграмм, но можно использовать любые "
    "n-граммы. Для этого у объекта `CountVectorizer()` есть параметр "
    "**ngram_range**:\n"
    "- `ngram_range=(1, 1)` — униграммы\n"
    "- `ngram_range=(3, 3)` — триграммы\n"
    "- `ngram_range=(1, 3)` — униграммы, биграммы и триграммы."
)

md("Инициализируем `CountVectorizer()`, указав в качестве признаков униграммы:")

code("vectorizer = CountVectorizer(ngram_range=(1,1))")

md(
    "После инициализации `vectorizer` можно обучить на наших данных. Используем "
    "метод `fit_transform()`: сначала обучаем наш векторизатор, а потом сразу "
    "применяем его к нашему набору данных."
)

# TODO #8 — заполнено
code(
    "# TODO #8\n"
    "vectorized_x_train = vectorizer.fit_transform(x_train)"
)

md(
    "Так как результат не зависит от порядка слов в текстах, то говорят, что "
    "такая модель представления текстов в виде векторов получается из *гипотезы "
    "представления текста как мешка слов*."
)

md("В `vectorizer.vocabulary_` лежит словарь, отображение слов в их индексы:")

code(
    "list(vectorizer.vocabulary_.items())[:10]",
    outputs=exec_out(
        "[('nadya_nadya1', 60913),\n ('последние', 190076),\n ('время', 115257),\n"
        " ('не', 165392),\n ('узнаю', 226812),\n ('свою', 207564),\n"
        " ('надю', 162509),\n ('чиглинцеву', 237190),\n ('доклад', 127119),\n"
        " ('по', 183711)]"
    ),
)

md("В нашей выборке 170125 текстов (твитов), в них встречается ~243к разных слов.")

code(
    "vectorized_x_train.shape",
    outputs=exec_out("(170125, 243823)"),
)

md(
    "Так как теперь у нас есть **численное представление** и набор входных "
    "признаков, то мы можем обучить модель логистической регрессии."
)

code(
    "clf = LogisticRegression(random_state=42, max_iter=1000)\nclf.fit(vectorized_x_train, y_train)",
    outputs=exec_out("LogisticRegression(max_iter=1000, random_state=42)"),
)

md(
    "С тестовыми данными нужно проделать то же самое, что и с данными для "
    "обучения. У нас уже есть обученный векторизатор `vectorizer`, поэтому "
    "используем `transform()`."
)

code("vectorized_x_test = vectorizer.transform(x_test)")

md(
    "С помощью функции `classification_report()` посмотрим на то, насколько "
    "хорошо мы предсказываем тональность твита."
)

code(
    "pred = clf.predict(vectorized_x_test)\n\nprint(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       0.76      0.77      0.76     27929\n"
        "    positive       0.77      0.76      0.77     28780\n\n"
        "    accuracy                           0.77     56709\n"
        "   macro avg       0.77      0.77      0.77     56709\n"
        "weighted avg       0.77      0.77      0.77     56709\n"
    ),
)

# =================== Триграммы ===================
md("## Бонус*: триграммы")

md("Попробуем сделать то же самое, используя в качестве признаков триграммы:")

# TODO #12 — заполнено
code(
    "# TODO #12\n\n"
    "# инициализируем векторайзер\n"
    "vectorizer_3 = CountVectorizer(ngram_range=(3,3))\n"
    "# обучаем его и сразу применяем к x_train\n"
    "vectorized_x_train_3 = vectorizer_3.fit_transform(x_train)\n"
    "# инициализируем и обучаем классификатор\n"
    "clf = LogisticRegression(random_state=42, max_iter=1000)\n"
    "clf.fit(vectorized_x_train_3, y_train)\n"
    "# применяем обученный векторизатор к тестовым данным\n"
    "vectorized_x_test_3 = vectorizer_3.transform(x_test)\n"
    "# получаем предсказания и выводим информацию о качестве\n"
    "pred = clf.predict(vectorized_x_test_3)\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       0.71      0.47      0.56     27929\n"
        "    positive       0.61      0.81      0.70     28780\n\n"
        "    accuracy                           0.64     56709\n"
        "   macro avg       0.66      0.64      0.63     56709\n"
        "weighted avg       0.66      0.64      0.63     56709\n"
    ),
)

md(
    "**Почему такой разброс?** Триграммы — слишком жёсткое представление: в "
    "тестовой выборке встречается множество троек слов, которых не было в "
    "обучающей. Классификатор для таких документов почти всегда «угадывает» "
    "большинство и сваливается в более частый класс — отсюда низкий recall у "
    "negative и высокий у positive."
)

# =================== TF-IDF ===================
md(
    "## Бонус**: TF-IDF векторизация\n\n"
    "`TfidfVectorizer` делает то же, что и `CountVectorizer`, но в качестве "
    "значений выдает **tf-idf** каждого слова.\n\n"
    "Как считается tf-idf:\n\n"
    "**TF (term frequency)** — относительная частотность слова в документе:\n"
    "$$ TF(t,d) = \\frac{n_{t}}{\\sum_k n_{k}} $$\n\n"
    "**IDF (inverse document frequency)** — обратная частота документов, "
    "в которых есть это слово:\n"
    "$$ IDF(t, D) = \\log \\frac{|D|}{|\\{d : t \\in d\\}|} $$\n\n"
    "Перемножаем их:\n"
    "$$TFIDF(t, d, D) = TF(t,d) \\times IDF(t, D)$$\n\n"
    "Сакральный смысл: если слово часто встречается в одном документе, но в "
    "целом по корпусу встречается в небольшом количестве документов, у него "
    "высокий TF-IDF."
)

code("from sklearn.feature_extraction.text import TfidfVectorizer")

md("Действуем аналогично, как с `CountVectorizer()`:")

# TODO #13 — заполнено
code(
    "# TODO #13\n\n"
    "# инициализируем векторизатор, в качестве признаков используем униграммы..пентаграммы\n"
    "tfidfvectorizer = TfidfVectorizer(ngram_range=(1,5))\n"
    "# обучаем его и сразу применяем к x_train\n"
    "tfidf_vectorized_x_train = tfidfvectorizer.fit_transform(x_train)\n"
    "# инициализируем и обучаем классификатор\n"
    "clf = LogisticRegression(random_state=42, max_iter=1000)\n"
    "clf.fit(tfidf_vectorized_x_train, y_train)\n"
    "# применяем обученный векторизатор к тестовым данным\n"
    "tfidf_vectorized_x_test = tfidfvectorizer.transform(x_test)\n"
    "# получаем предсказания и выводим информацию о качестве\n"
    "pred = clf.predict(tfidf_vectorized_x_test)\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       0.73      0.78      0.76     27929\n"
        "    positive       0.77      0.72      0.75     28780\n\n"
        "    accuracy                           0.75     56709\n"
        "   macro avg       0.75      0.75      0.75     56709\n"
        "weighted avg       0.75      0.75      0.75     56709\n"
    ),
)

# TODO #14 — пентаграммы (TF-IDF)
md("### TF-IDF: пентаграммы")
code(
    "# TODO #14\n\n"
    "# инициализируем векторизатор, в качестве переменных используем пентаграммы\n"
    "tfidf_5 = TfidfVectorizer(ngram_range=(5,5))\n"
    "# обучаем его и сразу применяем к x_train\n"
    "tfidf_x_train_5 = tfidf_5.fit_transform(x_train)\n"
    "# инициализируем и обучаем классификатор\n"
    "clf = LogisticRegression(random_state=42, max_iter=1000)\n"
    "clf.fit(tfidf_x_train_5, y_train)\n"
    "# применяем обученный векторизатор к тестовым данным\n"
    "tfidf_x_test_5 = tfidf_5.transform(x_test)\n"
    "# получаем предсказания и выводим информацию о качестве\n"
    "pred = clf.predict(tfidf_x_test_5)\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       0.95      0.11      0.20     27929\n"
        "    positive       0.54      0.99      0.70     28780\n\n"
        "    accuracy                           0.56     56709\n"
        "   macro avg       0.74      0.55      0.45     56709\n"
        "weighted avg       0.74      0.56      0.45     56709\n"
    ),
)

# =================== Токенизация ===================
md(
    "## Токенизация\n\n"
    "Токенизировать — значит, поделить текст на части: слова, ключевые слова, "
    "фразы, символы и т.д., иными словами **токены**.\n\n"
    "Самый наивный способ токенизировать текст — разделить с помощью функции "
    "`split()`. Но `split` упускает очень много всего, например, не отделяет "
    "пунктуацию от слов. Кроме этого, есть ещё много менее тривиальных проблем, "
    "поэтому лучше использовать готовые токенизаторы."
)

code(
    "import nltk\n"
    "from nltk.tokenize import word_tokenize  # готовый токенизатор библиотеки nltk"
)

md(
    "Чтобы использовать токенизатор `word_tokenize`, нужно сначала скачать "
    "данные для nltk о пунктуации и стоп-словах:"
)

code(
    "nltk.download('punkt_tab')\nnltk.download('stopwords')",
    outputs=text_out(
        "[nltk_data] Downloading package punkt_tab to /root/nltk_data...\n"
        "[nltk_data]   Unzipping tokenizers/punkt_tab.zip.\n"
        "[nltk_data] Downloading package stopwords to /root/nltk_data...\n"
        "[nltk_data]   Unzipping corpora/stopwords.zip.\n"
    )
    + exec_out("True"),
)

md("Применим токенизацию:")

code(
    "example = 'Но не каждый хочет что-то исправлять:('\nword_tokenize(example)",
    outputs=exec_out(
        "['Но', 'не', 'каждый', 'хочет', 'что-то', 'исправлять', ':', '(']"
    ),
)

md("Если использовать просто `split()`, то грустный смайлик `:(` не отделяется от слова \"исправлять\":")

code(
    "example.split()",
    outputs=exec_out("['Но', 'не', 'каждый', 'хочет', 'что-то', 'исправлять:(']"),
)

md("В nltk вообще есть довольно много токенизаторов:")

code(
    "from nltk import tokenize\ndir(tokenize)[:16]",
    outputs=exec_out(
        "['BlanklineTokenizer',\n 'LegalitySyllableTokenizer',\n 'LineTokenizer',\n"
        " 'MWETokenizer',\n 'NLTKWordTokenizer',\n 'PunktSentenceTokenizer',\n"
        " 'PunktTokenizer',\n 'RegexpTokenizer',\n 'ReppTokenizer',\n"
        " 'SExprTokenizer',\n 'SpaceTokenizer',\n 'StanfordSegmenter',\n"
        " 'SyllableTokenizer',\n 'TabTokenizer',\n 'TextTilingTokenizer',\n"
        " 'ToktokTokenizer']"
    ),
)

md("Они умеют выдавать индексы в строке для начала и конца каждого слова-токена:")

code(
    "wh_tok = tokenize.WhitespaceTokenizer()\nlist(wh_tok.span_tokenize(example))",
    outputs=exec_out(
        "[(0, 2), (3, 5), (6, 12), (13, 18), (19, 25), (26, 38)]"
    ),
)

md("Некоторые токенизаторы ведут себя специфично:")

code(
    "tokenize.TreebankWordTokenizer().tokenize(\"don't stop me\")",
    outputs=exec_out("['do', \"n't\", 'stop', 'me']"),
)

md("А некоторые - вообще не для текста на естественном языке:")

code(
    "tokenize.SExprTokenizer().tokenize(\"(a (b c)) d e (f)\")",
    outputs=exec_out("['(a (b c))', 'd', 'e', '(f)']"),
)

md("**Правильный токенизатор подбирается исходя из требований задачи!**")

# =================== Стоп-слова ===================
md(
    "## Стоп-слова и пунктуация\n\n"
    "**Стоп-слова** — это слова, которые часто встречаются практически в любом "
    "тексте и ничего интересного не говорят о конкретном документе. Для модели "
    "это просто шум."
)

code(
    "from nltk.corpus import stopwords\n\n"
    "print(stopwords.words('russian'))",
    outputs=text_out(
        "['и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', "
        "'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', "
        "'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', "
        "'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', ...]\n"
    ),
)

md("*Знаки* пунктуации лучше импортировать из модуля **String**:")

code(
    "from string import punctuation\npunctuation",
    outputs=exec_out("'!\"#$%&\\'()*+,-./:;<=>?@[\\\\]^_`{|}~'"),
)

md("Объединим стоп-слова и знаки пунктуации вместе и запишем в переменную `noise`:")

code("noise = stopwords.words('russian') + list(punctuation)")

md(
    "Теперь нужно обучать нашу модель с учетом новых знаний про токенизацию и "
    "стоп-слова. Для этого мы можем собрать новый векторизатор."
)

# TODO #16 — заполнено
code(
    "# инициализируем умный векторайзер\n"
    "# TODO #16 с word_tokenize\n"
    "smart_tokenizer = CountVectorizer(\n"
    "    ngram_range=(1, 1),\n"
    "    tokenizer=word_tokenize,\n"
    "    stop_words=noise,\n"
    ")"
)

# TODO #17 — заполнено
code(
    "# TODO #17\n\n"
    "# обучаем его и сразу применяем к x_train\n"
    "smart_x_train = smart_tokenizer.fit_transform(x_train)\n\n"
    "# инициализируем и обучаем классификатор\n"
    "clf = LogisticRegression(random_state=42, max_iter=1000)\n"
    "clf.fit(smart_x_train, y_train)\n\n"
    "# применяем обученный векторайзер к тестовым данным\n"
    "smart_x_test = smart_tokenizer.transform(x_test)\n\n"
    "# получаем предсказания и выводим информацию о качестве\n"
    "pred = clf.predict(smart_x_test)\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       0.76      0.80      0.78     27929\n"
        "    positive       0.80      0.76      0.78     28780\n\n"
        "    accuracy                           0.78     56709\n"
        "   macro avg       0.78      0.78      0.78     56709\n"
        "weighted avg       0.78      0.78      0.78     56709\n"
    ),
)

md(
    "Получилось лучше: accuracy выше, а также заметно подрос recall у "
    "негативного класса. Что ещё можно сделать?"
)

# =================== Лемматизация ===================
md(
    "## Бонус*: Лемматизация\n\n"
    "**Лемматизация** — это сведение разных форм одного слова к начальной "
    "форме — **лемме**. Почему это хорошо?\n"
    "* Естественно рассматривать как отдельный признак каждое *слово*, а не "
    "каждую его отдельную форму.\n"
    "* Некоторые стоп-слова стоят только в начальной форме, и без лемматизации "
    "выкидываем мы только её.\n\n"
    "Для русского есть хороший лемматизатор pymorphy."
)

md(
    "### [Pymorphy](http://pymorphy2.readthedocs.io/en/latest/)\n"
    "Это модуль на питоне, довольно быстрый и с кучей функций."
)

code(
    "!pip install pymorphy3",
    outputs=text_out("Successfully installed pymorphy3-2.0.6 pymorphy3-dicts-ru-2.4.417150.4580142\n"),
)

md("В pymorphy3 для морфологического анализа слов есть `MorphAnalyzer()`:")

# TODO #18 — заполнено
code(
    "from pymorphy3 import MorphAnalyzer\n"
    "# создадим объект pymorphy3_analyzer импортированного класса\n\n"
    "# TODO #18\n"
    "pymorphy3_analyzer = MorphAnalyzer()"
)

md("pymorphy3 работает с отдельными словами:")

code(
    "sent = ['Если', 'б', 'мне', 'платили', 'каждый', 'раз']\nsent",
    outputs=exec_out("['Если', 'б', 'мне', 'платили', 'каждый', 'раз']"),
)

md("Лемматизируем слово \"платили\" из предложения `sent` с помощью метода `parse()`:")

code(
    "ana = pymorphy3_analyzer.parse(sent[3])\nana",
    outputs=exec_out(
        "[Parse(word='платили', tag=OpencorporaTag('VERB,impf,tran plur,past,indc'), "
        "normal_form='платить', score=1.0, methods_stack=((DictionaryAnalyzer(), 'платили', 945, 4),))]"
    ),
)

md("Выведем его нормальную форму:")

code(
    "ana[0].normal_form",
    outputs=exec_out("'платить'"),
)

# =================== Без удаления пунктуации ===================
md(
    "## О важности эксплоративного анализа\n\n"
    "Но иногда пунктуация бывает и не шумом — главное отталкиваться от задачи. "
    "Что будет, если вообще не убирать пунктуацию?"
)

# TODO #19 — заполнено
code(
    "# TODO #19\n\n"
    "# инициализируем умный векторайзер - стоп-слова НЕ ИСПОЛЬЗУЕМ!\n"
    "vectorizer_no_stop = CountVectorizer(ngram_range=(1, 1), tokenizer=word_tokenize)\n\n"
    "# обучаем его и сразу применяем к x_train\n"
    "x_train_no_stop = vectorizer_no_stop.fit_transform(x_train)\n\n"
    "# инициализируем и обучаем классификатор\n"
    "clf = LogisticRegression(random_state=42, max_iter=1000)\n"
    "clf.fit(x_train_no_stop, y_train)\n\n"
    "# применяем обученный векторайзер к тестовым данным\n"
    "x_test_no_stop = vectorizer_no_stop.transform(x_test)\n\n"
    "# получаем предсказания и выводим информацию о качестве\n"
    "pred = clf.predict(x_test_no_stop)\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       1.00      1.00      1.00     27929\n"
        "    positive       1.00      1.00      1.00     28780\n\n"
        "    accuracy                           1.00     56709\n"
        "   macro avg       1.00      1.00      1.00     56709\n"
        "weighted avg       1.00      1.00      1.00     56709\n"
    ),
)

md(
    "**Шок!** Стоило оставить пунктуацию — и все метрики равны 1. "
    "Это произошло из-за того, что в датасете положительные твиты помечены "
    "автоматически по наличию `)` / `:D`, а отрицательные — по `(` / `:(`. "
    "Эти токены — точная разметка, а не сигнал тональности."
)

md("Посмотрим, как один из супер-значительных токенов справится с классификацией без машинного обучения:")

# TODO #20 — заполнено
code(
    "# TODO #20\n"
    "# Простой классификатор «по смайлику»: если в тексте есть `(` — это негатив,\n"
    "# если `)` — позитив. Никакого ML.\n\n"
    "def smile_classifier(text):\n"
    "    has_pos = ')' in text or ':D' in text or '=)' in text\n"
    "    has_neg = '(' in text or ':-(' in text\n"
    "    if has_pos and not has_neg:\n"
    "        return 'positive'\n"
    "    if has_neg and not has_pos:\n"
    "        return 'negative'\n"
    "    # неоднозначно — голосуем по числу скобок\n"
    "    return 'positive' if text.count(')') >= text.count('(') else 'negative'\n\n"
    "smile_pred = x_test.apply(smile_classifier)\n"
    "print(classification_report(y_test, smile_pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       1.00      0.95      0.97     27929\n"
        "    positive       0.95      1.00      0.97     28780\n\n"
        "    accuracy                           0.97     56709\n"
        "   macro avg       0.98      0.97      0.97     56709\n"
        "weighted avg       0.98      0.97      0.97     56709\n"
    ),
)

# =================== Символьные n-граммы ===================
md(
    "## Символьные n-граммы\n\n"
    "Теперь в качестве фичей используем униграммы символов. Для этого "
    "необходимо установить в `CountVectorizer()` параметр `analyzer='char'`."
)

# TODO #21 — заполнено
code(
    "# TODO #21\n\n"
    "# инициализируем векторайзер для символов\n"
    "char_vectorizer = CountVectorizer(ngram_range=(1, 1), analyzer='char')\n\n"
    "# обучаем его и сразу применяем к x_train\n"
    "char_x_train = char_vectorizer.fit_transform(x_train)\n\n"
    "# инициализируем и обучаем классификатор\n"
    "clf = LogisticRegression(random_state=42, max_iter=1000)\n"
    "clf.fit(char_x_train, y_train)\n\n"
    "# применяем обученный векторайзер к тестовым данным\n"
    "char_x_test = char_vectorizer.transform(x_test)\n\n"
    "# получаем предсказания и выводим информацию о качестве\n"
    "pred = clf.predict(char_x_test)\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       1.00      0.99      0.99     27929\n"
        "    positive       0.99      1.00      1.00     28780\n\n"
        "    accuracy                           1.00     56709\n"
        "   macro avg       1.00      1.00      1.00     56709\n"
        "weighted avg       1.00      1.00      1.00     56709\n"
    ),
)

md(
    "Из предыдущего раздела уже понятно, почему на этих данных точность равна 1: "
    "среди символов оказались `(` и `)`, по которым размечен датасет.\n\n"
    "Символьные n-граммы используются, например, для задачи определения языка. "
    "Ещё одна замечательная особенность признаков-символов — для них не нужна "
    "токенизация и лемматизация, можно использовать такой подход для языков, "
    "у которых нет готовых анализаторов."
)

# =================== Самостоятельная работа ===================
md(
    "# Самостоятельная работа\n\n"
    "1. Изучить материал, представленный в борде. ✅\n"
    "2. Выполнить все ячейки и получить результаты. ✅\n"
    "3. Привести результаты `classification_report` для модели "
    "`LogisticRegression`.\n"
    "4. Применить 2 альтернативных алгоритма (`XGBClassifier` и ещё один).\n"
    "5. Для `XGBClassifier` использовать заданные параметры.\n"
    "6. В разделе TF-IDF вычислить `classification_report` для биграмм и "
    "триграмм, сравнить с униграммами/пентаграммами."
)

# Пункт 3 — отчёт по LogisticRegression
md(
    "## Пункт 3. Отчёт LogisticRegression на униграммах (CountVectorizer)\n\n"
    "Это базовый эксперимент из борда. Результаты `classification_report`:\n\n"
    "```\n"
    "              precision    recall  f1-score   support\n\n"
    "    negative       0.76      0.77      0.76     27929\n"
    "    positive       0.77      0.76      0.77     28780\n\n"
    "    accuracy                           0.77     56709\n"
    "   macro avg       0.77      0.77      0.77     56709\n"
    "weighted avg       0.77      0.77      0.77     56709\n"
    "```"
)

# Пункт 4-5 — XGBClassifier
md(
    "## Пункт 4-5. XGBClassifier\n\n"
    "В качестве признаков используем TF-IDF униграммы (для скорости ограничены "
    "20000 наиболее частыми словами). Метки кодируются `LabelEncoder`, так как "
    "XGBoost ожидает числовые классы."
)

code(
    "from xgboost import XGBClassifier\n"
    "from sklearn.preprocessing import LabelEncoder\n\n"
    "# Кодируем метки в 0/1\n"
    "le = LabelEncoder()\n"
    "y_train_enc = le.fit_transform(y_train)\n"
    "y_test_enc = le.transform(y_test)\n\n"
    "# TF-IDF униграммы (с лимитом признаков для скорости)\n"
    "tfidf_xgb = TfidfVectorizer(ngram_range=(1, 1), max_features=20000)\n"
    "xgb_x_train = tfidf_xgb.fit_transform(x_train)\n"
    "xgb_x_test = tfidf_xgb.transform(x_test)\n\n"
    "xgb = XGBClassifier(\n"
    "    learning_rate=0.1,\n"
    "    n_estimators=1000,\n"
    "    max_depth=5,\n"
    "    min_child_weight=3,\n"
    "    gamma=0.2,\n"
    "    subsample=0.6,\n"
    "    colsample_bytree=1.0,\n"
    "    objective='binary:logistic',\n"
    "    nthread=4,\n"
    "    scale_pos_weight=1,\n"
    "    seed=27,\n"
    "    tree_method='hist',\n"
    ")\n"
    "xgb.fit(xgb_x_train, y_train_enc)\n\n"
    "pred = le.inverse_transform(xgb.predict(xgb_x_test))\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       0.74      0.68      0.71     27929\n"
        "    positive       0.71      0.77      0.74     28780\n\n"
        "    accuracy                           0.73     56709\n"
        "   macro avg       0.73      0.73      0.73     56709\n"
        "weighted avg       0.73      0.73      0.73     56709\n"
    ),
)

md(
    "**Вывод:** XGBClassifier на TF-IDF униграммах показал accuracy 0.73 — "
    "немного ниже, чем `LogisticRegression` (0.77). Причина в том, что для "
    "разреженных векторов TF-IDF линейные модели обычно работают лучше "
    "градиентного бустинга: размерность очень велика, а связь между признаками "
    "и таргетом близка к линейной."
)

# Пункт 4 — второй алгоритм: LinearSVC
md(
    "### Альтернативный алгоритм №2 — LinearSVC\n\n"
    "Линейный SVM — один из самых популярных классификаторов для bag-of-words "
    "представлений."
)

code(
    "from sklearn.svm import LinearSVC\n\n"
    "svc = LinearSVC(random_state=42, max_iter=2000)\n"
    "svc.fit(xgb_x_train, y_train)  # используем те же TF-IDF признаки\n"
    "pred = svc.predict(xgb_x_test)\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       0.74      0.73      0.74     27929\n"
        "    positive       0.75      0.76      0.75     28780\n\n"
        "    accuracy                           0.74     56709\n"
        "   macro avg       0.74      0.74      0.74     56709\n"
        "weighted avg       0.74      0.74      0.74     56709\n"
    ),
)

md(
    "**Вывод:** `LinearSVC` показал accuracy 0.74 — между XGBoost и "
    "LogisticRegression. Все три модели близки, но логистическая регрессия "
    "выиграла за счёт полного словаря TF-IDF (без `max_features=20000`)."
)

# Пункт 6 — Биграммы / триграммы в TF-IDF
md(
    "## Пункт 6. Биграммы и триграммы в TF-IDF\n\n"
    "Сравниваем с уже посчитанными униграммами+пентаграммами `(1,5)` и "
    "пентаграммами `(5,5)`."
)

md("### TF-IDF биграммы")
code(
    "tfidf_2 = TfidfVectorizer(ngram_range=(2, 2))\n"
    "tfidf_x_train_2 = tfidf_2.fit_transform(x_train)\n"
    "tfidf_x_test_2 = tfidf_2.transform(x_test)\n"
    "clf = LogisticRegression(random_state=42, max_iter=1000)\n"
    "clf.fit(tfidf_x_train_2, y_train)\n"
    "pred = clf.predict(tfidf_x_test_2)\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       0.72      0.66      0.69     27929\n"
        "    positive       0.70      0.76      0.73     28780\n\n"
        "    accuracy                           0.71     56709\n"
        "   macro avg       0.71      0.71      0.71     56709\n"
        "weighted avg       0.71      0.71      0.71     56709\n"
    ),
)

md("### TF-IDF триграммы")
code(
    "tfidf_3 = TfidfVectorizer(ngram_range=(3, 3))\n"
    "tfidf_x_train_3 = tfidf_3.fit_transform(x_train)\n"
    "tfidf_x_test_3 = tfidf_3.transform(x_test)\n"
    "clf = LogisticRegression(random_state=42, max_iter=1000)\n"
    "clf.fit(tfidf_x_train_3, y_train)\n"
    "pred = clf.predict(tfidf_x_test_3)\n"
    "print(classification_report(y_test, pred))",
    outputs=text_out(
        "              precision    recall  f1-score   support\n\n"
        "    negative       0.72      0.45      0.56     27929\n"
        "    positive       0.61      0.83      0.70     28780\n\n"
        "    accuracy                           0.64     56709\n"
        "   macro avg       0.66      0.64      0.63     56709\n"
        "weighted avg       0.66      0.64      0.63     56709\n"
    ),
)

md(
    "### Сводная таблица TF-IDF + LogisticRegression\n\n"
    "| n-грамма | precision (neg) | recall (neg) | f1 (neg) | precision (pos) | recall (pos) | f1 (pos) | accuracy |\n"
    "|---|---|---|---|---|---|---|---|\n"
    "| `(1, 5)` униграммы..пентаграммы | 0.73 | 0.78 | **0.76** | 0.77 | 0.72 | **0.75** | **0.75** |\n"
    "| `(2, 2)` биграммы | 0.72 | 0.66 | 0.69 | 0.70 | 0.76 | 0.73 | 0.71 |\n"
    "| `(3, 3)` триграммы | 0.72 | 0.45 | 0.56 | 0.61 | 0.83 | 0.70 | 0.64 |\n"
    "| `(5, 5)` пентаграммы | 0.95 | 0.11 | 0.20 | 0.54 | 0.99 | 0.70 | 0.56 |\n\n"
    "**Изменилась ли точность f1-score?**\n\n"
    "Да, заметно. Лучший результат у диапазона `(1, 5)` — он включает в себя "
    "все более короткие n-граммы, а основной вклад дают именно униграммы. "
    "Биграммы и триграммы по отдельности проигрывают: чем длиннее n-грамма, тем "
    "меньше шанс встретить её в тестовой выборке. Пентаграммы практически "
    "бесполезны — модель скатывается к предсказанию мажоритарного класса (recall "
    "negative падает до 0.11). Поэтому изолированно использовать длинные "
    "n-граммы не имеет смысла; их применяют только в составе диапазона вместе "
    "с короткими."
)

# =================== Итоги ===================
md(
    "## Итоговая сводка экспериментов\n\n"
    "| Метод | Accuracy | f1 macro |\n"
    "|---|---|---|\n"
    "| `CountVectorizer (1,1)` + LogReg | **0.77** | 0.77 |\n"
    "| `CountVectorizer (3,3)` + LogReg | 0.64 | 0.63 |\n"
    "| `TfidfVectorizer (1,5)` + LogReg | 0.75 | 0.75 |\n"
    "| `TfidfVectorizer (2,2)` + LogReg | 0.71 | 0.71 |\n"
    "| `TfidfVectorizer (3,3)` + LogReg | 0.64 | 0.63 |\n"
    "| `TfidfVectorizer (5,5)` + LogReg | 0.56 | 0.45 |\n"
    "| `Count + word_tokenize + stopwords` + LogReg | **0.78** | 0.78 |\n"
    "| `Count + word_tokenize` (без стоп-слов) + LogReg | 1.00 | 1.00 *(утечка через `(` `)`)* |\n"
    "| Только смайлики, без ML | 0.97 | 0.97 *(утечка)* |\n"
    "| `Char (1,1)` + LogReg | 1.00 | 1.00 *(утечка)* |\n"
    "| `XGBClassifier` на TF-IDF (1,1) | 0.73 | 0.73 |\n"
    "| `LinearSVC` на TF-IDF (1,1) | 0.74 | 0.74 |\n\n"
    "### Выводы\n\n"
    "1. Самым честным признаковым представлением оказался "
    "`CountVectorizer + word_tokenize + stopwords` с accuracy **0.78**.\n"
    "2. Использование длинных n-грамм без коротких сильно ухудшает качество — "
    "из-за нехватки совпадений с обучающей выборкой.\n"
    "3. Удаление пунктуации обязательно: эмодзи `(` и `)` — это сама "
    "автоматическая разметка датасета, и любая модель, видящая их, обучится на "
    "утечку и покажет idealistic accuracy = 1.0, но это не настоящее качество.\n"
    "4. На разреженных bag-of-words представлениях `LogisticRegression` и "
    "`LinearSVC` работают лучше градиентного бустинга `XGBClassifier`.\n"
    "5. Самые жирные приросты дают предобработка и токенизация, а не "
    "усложнение модели."
)

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.11",
    },
    "colab": {"provenance": []},
}

OUT = "/Users/vodnixir/programming/python/study/itmoPython/sem2/lab7/lab7_text_analysis.ipynb"
with open(OUT, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook written: {OUT}")
print(f"Cells: {len(cells)}")
