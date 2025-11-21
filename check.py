import json

SCIDOCS_COLLECTION_PATH = r"/home/product/datasets/scidocs/corpus.jsonl"

def load_corpus_and_index(path):
    count = 0
    missing_text_count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            doc = json.loads(line)
            if doc.get("text", None):
                count += 1

            if count > 11164:
                print(doc)
                return

            if count >= 11313:
                return


if __name__ == "__main__":
    load_corpus_and_index(SCIDOCS_COLLECTION_PATH)