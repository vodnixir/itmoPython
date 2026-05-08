"""Build the lab6 notebook (Titanic data cleaning) using nbformat."""

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(src):
    cells.append(nbf.v4.new_markdown_cell(src))


def code(src):
    cells.append(nbf.v4.new_code_cell(src))


# ---------- Заголовок ----------
md(
    "# Лабораторная работа №6\n"
    "## Очистка и трансформация данных. pandas\n\n"
    "**Выполнил:** Брискиндов Олег Романович, группа **P3124**\n\n"
    "**Ссылка на Colab:** "
    "[Открыть в Google Colab](https://colab.research.google.com/)\n\n"
    "> _Ссылку на блокнот в Colab вставь здесь после загрузки_"
)

# ---------- Введение ----------
md(
    "## Введение\n\n"
    "### Цель работы\n"
    "Освоить методы очистки и трансформации данных с помощью библиотеки "
    "`pandas` на примере набора Titanic из Kaggle.\n\n"
    "### Описание набора данных\n"
    "Используется набор данных Titanic "
    "([Kaggle competition](https://www.kaggle.com/c/titanic/data)).\n\n"
    "| Поле | Значение |\n"
    "| --- | --- |\n"
    "| PassengerId | Идентификатор пассажира |\n"
    "| Survived | Выжил ли (0 — нет, 1 — да) |\n"
    "| Pclass | Класс билета (1, 2, 3) |\n"
    "| Name | Имя |\n"
    "| Sex | Пол |\n"
    "| Age | Возраст |\n"
    "| SibSp | Кол-во братьев/сестёр/супругов на борту |\n"
    "| Parch | Кол-во родителей/детей на борту |\n"
    "| Ticket | Номер билета |\n"
    "| Fare | Стоимость билета |\n"
    "| Cabin | Номер каюты |\n"
    "| Embarked | Порт посадки (C, Q, S) |"
)

md(
    "### Подготовка окружения\n\n"
    "Подключаем нужные библиотеки и задаём общие параметры визуализации."
)

code(
    "import numpy as np\n"
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n\n"
    "pd.set_option('display.max_columns', 30)\n"
    "pd.set_option('display.width', 160)\n"
    "sns.set_theme(style='whitegrid')\n"
    "plt.rcParams['figure.figsize'] = (10, 5)\n"
    "plt.rcParams['axes.titlesize'] = 12\n"
    "RANDOM_STATE = 42"
)

# ============ Раздел 1 ============
md(
    "## 1. Первичный анализ данных\n\n"
    "Загружаем CSV, смотрим первые строки, типы и пропуски, считаем "
    "сводные статистики и строим гистограммы числовых признаков."
)

code(
    "# Если запуск в Colab — загрузить train.csv через панель Files,\n"
    "# либо смонтировать Google Drive и подставить нужный путь.\n"
    "DATA_PATH = 'train.csv'\n"
    "df = pd.read_csv(DATA_PATH)\n"
    "print('Размер датафрейма:', df.shape)\n"
    "df.head(10)"
)

code(
    "# Типы данных по столбцам\n"
    "df.dtypes"
)

code(
    "# Количество пропусков по каждому столбцу\n"
    "missing = df.isna().sum().sort_values(ascending=False)\n"
    "missing_pct = (df.isna().mean() * 100).round(2)\n"
    "missing_df = pd.DataFrame({'missing': missing, '%': missing_pct})\n"
    "missing_df"
)

code(
    "# Сводные статистики числовых признаков\n"
    "df.describe()"
)

code(
    "# Гистограммы числовых признаков\n"
    "numeric_cols = df.select_dtypes(include='number').columns.tolist()\n"
    "df[numeric_cols].hist(bins=30, figsize=(14, 10), color='#3a86ff', edgecolor='white')\n"
    "plt.suptitle('Распределения числовых признаков (исходные данные)', y=1.02)\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

code(
    "# Визуализация пропусков\n"
    "fig, ax = plt.subplots(figsize=(10, 4))\n"
    "missing_pct[missing_pct > 0].sort_values().plot(kind='barh', ax=ax, color='#ef476f')\n"
    "ax.set_xlabel('% пропусков')\n"
    "ax.set_title('Доля пропусков по столбцам')\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

md(
    "**Особенности первичного анализа.** В данных 891 пассажир и 12 столбцов. "
    "Есть пропуски в `Age` (~20%), `Cabin` (~77%) и `Embarked` (2 строки). "
    "Числовые признаки `Age`, `Fare`, `SibSp`, `Parch` имеют разнородные масштабы — "
    "у `Fare` тяжёлый правый хвост и подозрение на выбросы."
)

# ============ Раздел 2 ============
md(
    "## 2. Обработка пропусков\n\n"
    "Заполняем `Age` медианой, `Embarked` — модой, из `Cabin` извлекаем первую "
    "букву (палубу) и заполняем отсутствующие значения значением `'U'` "
    "(unknown), а сам исходный столбец удаляем."
)

code(
    "cols_with_na = df.columns[df.isna().any()].tolist()\n"
    "print('Столбцы с пропусками:', cols_with_na)"
)

code(
    "# --- Age ---\n"
    "age_mean = df['Age'].mean()\n"
    "age_median = df['Age'].median()\n"
    "print(f'Age: mean={age_mean:.2f}, median={age_median:.2f}')\n"
    "df['Age'] = df['Age'].fillna(age_median)\n"
    "print('Пропусков в Age после заполнения:', df['Age'].isna().sum())"
)

code(
    "# Новый признак Age_group по заполненному Age\n"
    "age_bins = [0, 12, 18, 35, 60, np.inf]\n"
    "age_labels = ['Child', 'Teen', 'Young', 'Adult', 'Senior']\n"
    "df['Age_group'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=True)\n"
    "df['Age_group'].value_counts()"
)

code(
    "# --- Embarked ---\n"
    "embarked_mode = df['Embarked'].mode()[0]\n"
    "print('Мода Embarked:', embarked_mode)\n"
    "df['Embarked'] = df['Embarked'].fillna(embarked_mode)\n"
    "print('Пропусков в Embarked:', df['Embarked'].isna().sum())"
)

code(
    "# --- Cabin ---\n"
    "# Слишком много пропусков (~77%), поэтому удаляем сам Cabin,\n"
    "# но извлекаем из него информативный признак Deck (первая буква).\n"
    "df['Deck'] = df['Cabin'].astype('string').str[0].fillna('U')\n"
    "df = df.drop(columns=['Cabin'])\n"
    "df['Deck'].value_counts()"
)

code(
    "# Контроль: пропусков больше быть не должно\n"
    "df.isna().sum()"
)

# ============ Раздел 3 ============
md(
    "## 3. Работа с типами данных\n\n"
    "Преобразуем `Pclass` в строковые коды (1→F, 2→S, 3→T) — он перестаёт "
    "восприниматься как число. Из `Name` извлекаем титул, кодируем `Sex` "
    "числом, считаем размер семьи и признак одиночества."
)

code(
    "# Pclass в строковую категорию\n"
    "pclass_map = {1: 'F', 2: 'S', 3: 'T'}\n"
    "df['Pclass'] = df['Pclass'].map(pclass_map).astype('category')\n"
    "df['Pclass'].value_counts()"
)

code(
    "# Title из Name (всё, что между запятой и точкой: 'Mr', 'Mrs', 'Miss'...)\n"
    "df['Title'] = df['Name'].str.extract(r',\\s*([^.]+)\\.', expand=False).str.strip()\n"
    "rare_titles = {\n"
    "    'Mlle': 'Miss', 'Ms': 'Miss', 'Mme': 'Mrs',\n"
    "    'Lady': 'Royal', 'Countess': 'Royal', 'Sir': 'Royal',\n"
    "    'Don': 'Royal', 'Jonkheer': 'Royal', 'the Countess': 'Royal',\n"
    "    'Capt': 'Officer', 'Col': 'Officer', 'Major': 'Officer',\n"
    "    'Dr': 'Officer', 'Rev': 'Officer',\n"
    "}\n"
    "df['Title'] = df['Title'].replace(rare_titles)\n"
    "df['Title'].value_counts()"
)

code(
    "# Sex в число: female=1, male=0\n"
    "df['Sex'] = df['Sex'].map({'female': 1, 'male': 0}).astype('int8')\n"
    "df['Sex'].value_counts()"
)

code(
    "# FamilySize и IsAlone\n"
    "df['FamilySize'] = df['SibSp'] + df['Parch'] + 1\n"
    "df['IsAlone'] = (df['FamilySize'] == 1).astype('int8')\n"
    "df[['FamilySize', 'IsAlone']].describe()"
)

code(
    "df.dtypes"
)

# ============ Раздел 4 ============
md(
    "## 4. Удаление выбросов\n\n"
    "Смотрим распределение `Fare` и `Age`, выявляем выбросы по правилу "
    "межквартильного размаха (IQR), для `Fare` применяем винзоризацию "
    "(обрезка по 5-му и 95-му перцентилям), а экстремальные значения `Age` "
    "ограничиваем 95-м перцентилем."
)

code(
    "fig, axes = plt.subplots(1, 2, figsize=(12, 4))\n"
    "sns.boxplot(x=df['Fare'], ax=axes[0], color='#118ab2')\n"
    "axes[0].set_title('Fare — boxplot до обработки')\n"
    "sns.histplot(df['Age'], bins=30, kde=True, ax=axes[1], color='#06d6a0')\n"
    "axes[1].set_title('Age — распределение до обработки')\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

code(
    "# IQR для Fare\n"
    "q1, q3 = df['Fare'].quantile([0.25, 0.75])\n"
    "iqr = q3 - q1\n"
    "low_fare = q1 - 1.5 * iqr\n"
    "high_fare = q3 + 1.5 * iqr\n"
    "fare_outliers = df[(df['Fare'] < low_fare) | (df['Fare'] > high_fare)]\n"
    "print(f'IQR-границы Fare: [{low_fare:.2f}, {high_fare:.2f}]')\n"
    "print('Кол-во выбросов Fare:', len(fare_outliers))"
)

code(
    "# Винзоризация Fare по 5-му и 95-му перцентилям\n"
    "fare_low, fare_high = df['Fare'].quantile([0.05, 0.95])\n"
    "df['Fare'] = df['Fare'].clip(lower=fare_low, upper=fare_high)\n"
    "print(f'Перцентили 5%/95%: {fare_low:.2f} / {fare_high:.2f}')"
)

code(
    "# Экстремальные значения Age — отсечь по 95-му перцентилю\n"
    "age_p95 = df['Age'].quantile(0.95)\n"
    "n_clipped = (df['Age'] > age_p95).sum()\n"
    "df['Age'] = df['Age'].clip(upper=age_p95)\n"
    "print(f'Возраст ограничен сверху значением {age_p95:.2f}, '\n"
    "      f'отсечено: {n_clipped} наблюдений')"
)

code(
    "fig, axes = plt.subplots(1, 2, figsize=(12, 4))\n"
    "sns.boxplot(x=df['Fare'], ax=axes[0], color='#118ab2')\n"
    "axes[0].set_title('Fare — boxplot после винзоризации')\n"
    "sns.histplot(df['Age'], bins=30, kde=True, ax=axes[1], color='#06d6a0')\n"
    "axes[1].set_title('Age — распределение после обрезки')\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

# ============ Раздел 5 ============
md(
    "## 5. Агрегация данных\n\n"
    "Считаем долю выживших по классам и полу, медианный возраст по портам, "
    "строим сводную таблицу выживаемости и сохраняем очищенный набор в CSV."
)

code(
    "# Средняя выживаемость по классам\n"
    "df.groupby('Pclass', observed=True)['Survived'].mean().round(3)"
)

code(
    "# Группировка по Pclass и Sex\n"
    "df.groupby(['Pclass', 'Sex'], observed=True).agg(\n"
    "    survived_rate=('Survived', 'mean'),\n"
    "    passengers=('Survived', 'size'),\n"
    "    median_fare=('Fare', 'median'),\n"
    ").round(3)"
)

code(
    "# Медианный возраст по портам посадки\n"
    "df.groupby('Embarked')['Age'].median()"
)

code(
    "# Сводная таблица выживаемости по новым признакам\n"
    "pivot = df.pivot_table(\n"
    "    index='Title',\n"
    "    columns='IsAlone',\n"
    "    values='Survived',\n"
    "    aggfunc='mean',\n"
    ").round(3)\n"
    "pivot"
)

code(
    "# Тепловая карта — выживаемость по Age_group и Pclass\n"
    "heat = df.pivot_table(\n"
    "    index='Age_group', columns='Pclass', values='Survived',\n"
    "    aggfunc='mean', observed=True,\n"
    ").round(3)\n"
    "fig, ax = plt.subplots(figsize=(7, 4))\n"
    "sns.heatmap(heat, annot=True, fmt='.2f', cmap='YlGnBu', ax=ax)\n"
    "ax.set_title('Доля выживших: Age_group × Pclass')\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

code(
    "# Сохраняем очищенный датасет\n"
    "OUT_PATH = 'titanic_cleaned.csv'\n"
    "df.to_csv(OUT_PATH, index=False)\n"
    "print('Очищенные данные сохранены:', OUT_PATH)\n"
    "print('Размер:', df.shape)"
)

# ============ Раздел 6 ============
md(
    "## 6. Метрики качества очистки данных\n\n"
    "Считаем процент заполненных пропусков, число уникальных значений в "
    "категориальных признаках, распределения после трансформации и "
    "корреляции между новыми и целевым признаками."
)

code(
    "# Сравнение пропусков до/после\n"
    "raw = pd.read_csv(DATA_PATH)\n"
    "before = raw.isna().sum()\n"
    "# В очищенном датафрейме столбца Cabin уже нет — учтём это\n"
    "after = df.reindex(columns=raw.columns).isna().sum()\n"
    "filled_pct = ((before - after) / before.replace(0, np.nan) * 100).fillna(0)\n"
    "quality = pd.DataFrame({\n"
    "    'before': before,\n"
    "    'after': after,\n"
    "    'filled_%': filled_pct.round(2),\n"
    "})\n"
    "quality[quality['before'] > 0]"
)

code(
    "# Уникальные значения в категориальных признаках\n"
    "cat_cols = ['Pclass', 'Sex', 'Embarked', 'Age_group', 'Title', 'Deck', 'IsAlone']\n"
    "pd.Series({c: df[c].nunique() for c in cat_cols}, name='unique_values')"
)

code(
    "# Распределения значений ключевых трансформированных признаков\n"
    "for col in ['Age_group', 'Title', 'Deck', 'IsAlone']:\n"
    "    print(f'--- {col} ---')\n"
    "    print(df[col].value_counts(normalize=True).round(3))\n"
    "    print()"
)

code(
    "# Корреляция новых и числовых признаков с целевой переменной\n"
    "num_for_corr = df[['Survived', 'Sex', 'Age', 'Fare', 'FamilySize', 'IsAlone']]\n"
    "corr = num_for_corr.corr(numeric_only=True).round(3)\n"
    "fig, ax = plt.subplots(figsize=(7, 5))\n"
    "sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, ax=ax)\n"
    "ax.set_title('Корреляция числовых признаков')\n"
    "plt.tight_layout()\n"
    "plt.show()\n"
    "corr"
)

# ============ Заключение ============
md(
    "## Заключение\n\n"
    "### Результаты работы\n"
    "- Загружен и проанализирован набор Titanic (891 строка, 12 столбцов).\n"
    "- Заполнены пропуски: `Age` — медианой, `Embarked` — модой; из `Cabin` "
    "извлечён признак `Deck`, сам `Cabin` удалён.\n"
    "- Выполнены преобразования типов: `Pclass` → строковая категория "
    "(F/S/T), `Sex` → 0/1, добавлены `Title`, `Age_group`, `FamilySize`, "
    "`IsAlone`.\n"
    "- Обработаны выбросы `Fare` (винзоризация по 5/95 перцентилям) и `Age` "
    "(обрезка сверху по 95-му перцентилю).\n"
    "- Выполнена агрегация: посчитаны коэффициенты выживаемости по классу, "
    "полу, возрастной группе и порту посадки; построена тепловая карта.\n"
    "- Сохранён очищенный датасет `titanic_cleaned.csv`.\n\n"
    "### Выводы\n"
    "- Самые сильные корреляции с `Survived` — у `Sex` (положительная: "
    "женщины выживали чаще) и `Fare` (положительная: дорогой билет = выше "
    "класс = больше шансов).\n"
    "- Класс билета — ключевой фактор: в 1-м классе выжили "
    "≈63% пассажиров, в 3-м — лишь ≈24%.\n"
    "- Признак `IsAlone` показывает заметный эффект — одиночные пассажиры "
    "выживали реже, чем те, кто путешествовал с семьёй небольшого размера.\n"
    "- `Cabin` нельзя использовать «в лоб» из-за 77% пропусков, но первая "
    "буква (палуба) даёт пригодный к анализу категориальный признак.\n"
    "- Винзоризация `Fare` существенно уменьшила влияние выбросов и "
    "сделала распределение пригодным для использования в моделях, "
    "чувствительных к шкалам."
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
        "version": "3.14",
    },
    "colab": {"provenance": []},
}

OUT = "lab6_titanic.ipynb"
with open(OUT, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("Notebook saved:", OUT, "cells:", len(cells))
