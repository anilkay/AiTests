"""PageIndex ile bir PDF'e soru sorma: küçük örnek.

Kurulum:
    pip install -U "pageindex[claude]"

Kullanım:
    python ornek.py belge.pdf "Sorum ne?"                  # Claude aboneliği (claude-code)
    python ornek.py belge.pdf "Sorum ne?" --model ollama   # Ollama, gpt-oss:20b-cloud
    python ornek.py belge.pdf                              # soru vermezsen etkileşimli sohbet

İlk çalıştırmada PDF indekslenir (ağaç çıkarılır) ve ./.pageindex_ornek altına kaydedilir.
Aynı PDF için sonraki çalıştırmalar kayıtlı indeksi kullanır.
"""
import argparse
import json
import os
import time

from pageindex import PageIndexClient

OLLAMA = {"api_base": os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")}
MODELS = {
    # İndeksleme için basit bir model yeterli; soru-cevap için güçlü model şart.
    "claude": {"index": "claude-code/haiku", "chat": "claude-code/opus", "backend": None},
    "ollama": {"index": "ollama_chat/gpt-oss:20b-cloud",
               "chat": "ollama_chat/gpt-oss:20b-cloud", "backend": OLLAMA},
}


def make_client(name: str, storage: str) -> PageIndexClient:
    m = MODELS[name]
    index = {"model": m["index"], "storage_path": storage}
    chat = m["chat"]
    if m["backend"]:
        index["backend"] = m["backend"]
        index["summary_concurrency"] = 8          # Ollama'yı boğmamak için
        chat = {"model": m["chat"], "backend": m["backend"]}
    return PageIndexClient(index=index, chat=chat)


def get_doc_id(client: PageIndexClient, pdf: str, storage: str) -> str:
    """PDF daha önce indekslendiyse doc_id'yi tekrar kullan, değilse indeksle."""
    cache_file = os.path.join(storage, "ornek_docs.json")
    cache = json.load(open(cache_file)) if os.path.exists(cache_file) else {}
    key = os.path.abspath(pdf)
    if key in cache:
        return cache[key]

    print(f"İndeksleniyor: {pdf} ...")
    t = time.time()
    result = client.submit_document(pdf)
    print(f"Bitti: {time.time() - t:.0f} sn, doc_id={result['doc_id']}")

    cache[key] = result["doc_id"]
    os.makedirs(storage, exist_ok=True)
    json.dump(cache, open(cache_file, "w"), indent=1)
    return result["doc_id"]


def print_tree(client: PageIndexClient, doc_id: str, depth: int = 2) -> None:
    """Ağacın ilk seviyelerini göster: başlık + sayfa aralığı."""
    def walk(nodes, level):
        for n in nodes or []:
            print("  " * level + f"- {n['title']}  (s. {n['start_index']}-{n['end_index']})")
            if level + 1 < depth:
                walk(n.get("nodes"), level + 1)
    walk(client.get_tree(doc_id, include_text=False)["result"], 0)


def ask(client: PageIndexClient, doc_id: str, messages: list) -> str:
    """Cevabı akış halinde yaz, tamamını döndür."""
    answer = ""
    for chunk in client.chat(messages, doc_id=doc_id, stream=True, show_process=False):
        if isinstance(chunk, str):
            print(chunk, end="", flush=True)
            answer += chunk
    print()
    return answer


def main():
    ap = argparse.ArgumentParser(description="PageIndex ile PDF'e soru sor")
    ap.add_argument("pdf")
    ap.add_argument("soru", nargs="?")
    ap.add_argument("--model", choices=MODELS, default="claude")
    ap.add_argument("--agac", action="store_true", help="indeks ağacını yazdır")
    ap.add_argument("--storage", default=".pageindex_ornek")
    args = ap.parse_args()

    storage = os.path.join(args.storage, args.model)  # her model kendi indeksini kullanır
    client = make_client(args.model, storage)
    doc_id = get_doc_id(client, args.pdf, storage)

    if args.agac:
        print_tree(client, doc_id)

    if args.soru:
        ask(client, doc_id, args.soru)
        return

    # Etkileşimli sohbet: geçmiş mesaj listesi olarak gönderilir, takip soruları çalışır.
    history = []
    print("Soru sorun (çıkmak için boş satır).")
    while True:
        q = input("\n> ").strip()
        if not q:
            break
        history.append({"role": "user", "content": q})
        t = time.time()
        history.append({"role": "assistant", "content": ask(client, doc_id, history)})
        print(f"[{time.time() - t:.1f} sn]")


if __name__ == "__main__":
    main()
