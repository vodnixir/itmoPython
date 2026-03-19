import json, re, os
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = "reworked_dataset.json"   # <- твой файл с мета-тегами в начале текста
OUT_DIR = "plots"
os.makedirs(OUT_DIR, exist_ok=True)

tag_re = re.compile(r"\[(ADDRESSEE|TOPIC|DOC|HAS_ATTACH|LEN)=([^\]]*)\]")

def parse_tags(text: str):
    tags = {k: v for k, v in tag_re.findall(text)}

    # booleans
    for k in ["ADDRESSEE", "DOC", "HAS_ATTACH"]:
        if k in tags:
            tags[k] = 1 if tags[k].strip() == "1" else 0
        else:
            tags[k] = 0

    # TOPIC: считаем "присутствует", если значение не пустое
    if "TOPIC" in tags:
        tags["TOPIC_PRESENT"] = 1 if tags["TOPIC"].strip() else 0
    else:
        tags["TOPIC_PRESENT"] = 0

    # LEN bucket
    tags["LEN_BUCKET"] = (tags.get("LEN", "") or "NA").strip() or "NA"
    return tags

# ---- load ----
with open(DATA_PATH, "r", encoding="utf-8") as f:
    rows = json.load(f)

parsed = []
for r in rows:
    text = r.get("text", "")
    tags = parse_tags(text)
    parsed.append({
        "idx": r.get("idx"),
        "label": r.get("label"),
        **tags
    })

df = pd.DataFrame(parsed)

# ---- 1) Label distribution (top-15 + Other) ----
label_counts = df["label"].value_counts()
top_n = 15
top = label_counts.head(top_n)
other = label_counts.iloc[top_n:].sum()
plot_series = top.copy()
if other > 0:
    plot_series["Другое"] = other

plt.figure()
plot_series.sort_values().plot(kind="barh")
plt.title(f"Распределение классов (топ-{top_n} + Другое)")
plt.xlabel("Количество писем")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "01_label_distribution_top15.png"), dpi=200)
plt.close()

# ---- 2) Long-tail view: counts per label on log scale ----
plt.figure()
label_counts_sorted = label_counts.sort_values(ascending=False).reset_index(drop=True)
plt.plot(range(1, len(label_counts_sorted)+1), label_counts_sorted.values)
plt.yscale("log")
plt.title("Длинный хвост классов (log по оси Y)")
plt.xlabel("Ранг класса (1 = самый частый)")
plt.ylabel("Количество (log)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "02_label_long_tail_log.png"), dpi=200)
plt.close()

# ---- 3) Meta coverage bar (percent) ----
coverage = {
    "ADDRESSEE": df["ADDRESSEE"].mean() * 100,
    "TOPIC": df["TOPIC_PRESENT"].mean() * 100,
    "DOC": df["DOC"].mean() * 100,
    "HAS_ATTACH": df["HAS_ATTACH"].mean() * 100,
}
plt.figure()
plt.bar(list(coverage.keys()), list(coverage.values()))
plt.title("Покрытие мета-полей (%)")
plt.ylabel("Доля писем, %")
plt.ylim(0, 100)
for i, v in enumerate(coverage.values()):
    plt.text(i, v + 1, f"{v:.1f}%", ha="center")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "03_meta_coverage.png"), dpi=200)
plt.close()

# ---- 4) LEN bucket distribution ----
len_counts = df["LEN_BUCKET"].value_counts().sort_index()
plt.figure()
plt.bar(len_counts.index.astype(str), len_counts.values)
plt.title("Распределение длины текста (LEN bucket)")
plt.xlabel("LEN bucket")
plt.ylabel("Количество писем")
for i, v in enumerate(len_counts.values):
    plt.text(i, v + max(len_counts.values)*0.01, str(int(v)), ha="center", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "04_len_bucket.png"), dpi=200)
plt.close()

# ---- 5) Coverage per label: DOC vs TOPIC (top-12 labels) ----
top_labels = label_counts.head(12).index.tolist()
sub = df[df["label"].isin(top_labels)].copy()

agg = sub.groupby("label").agg(
    count=("label", "size"),
    topic_rate=("TOPIC_PRESENT", "mean"),
    doc_rate=("DOC", "mean"),
).sort_values("count", ascending=False)

plt.figure()
x = range(len(agg))
plt.plot(x, (agg["topic_rate"]*100).values, marker="o", label="TOPIC %")
plt.plot(x, (agg["doc_rate"]*100).values, marker="o", label="DOC %")
plt.xticks(x, agg.index, rotation=60, ha="right")
plt.title("Покрытие TOPIC и DOC по самым частым классам")
plt.ylabel("Доля писем, %")
plt.ylim(0, 100)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "05_topic_doc_by_top_labels.png"), dpi=200)
plt.close()

# ---- 6) Correlation heatmap (meta fields) ----
meta_cols = ["ADDRESSEE", "TOPIC_PRESENT", "DOC", "HAS_ATTACH"]
corr = df[meta_cols].astype(int).corr()

plt.figure()
plt.imshow(corr.values, aspect="auto")
plt.xticks(range(len(meta_cols)), meta_cols, rotation=45, ha="right")
plt.yticks(range(len(meta_cols)), meta_cols)
plt.title("Корреляция между мета-признаками")
for i in range(len(meta_cols)):
    for j in range(len(meta_cols)):
        plt.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center", fontsize=8)
plt.colorbar()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "06_meta_corr.png"), dpi=200)
plt.close()

print("Готово! Картинки сохранены в:", OUT_DIR)
for fn in sorted(os.listdir(OUT_DIR)):
    print(" -", os.path.join(OUT_DIR, fn))
