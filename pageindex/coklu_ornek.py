"""PageIndex ile birden fazla PDF: submit + tek belgeye / tüm belgelere soru.

Kurulum:
    pip install -U "pageindex[claude]"

Kullanım:
    python coklu_ornek.py a.pdf b.pdf c.pdf
    python coklu_ornek.py a.pdf b.pdf --model ollama   # tamamen yerel (Ollama)

İndeksleme: gpt-oss:20b (Ollama). Cevap: Claude Opus (claude-code) veya --model ollama ile gpt-oss.
Her dosya için ayrı submit_document çağrısı yapılır; doc_id listesi chat()'e verilir.
"""
import argparse
import os
import sys
import time

from pageindex import PageIndexClient

OLLAMA = {"api_base": os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")}
OSS = "ollama_chat/gpt-oss:20b-cloud"


def make_client(model: str, storage: str) -> PageIndexClient:
    index = {"model": OSS, "backend": OLLAMA, "storage_path": storage}
    chat = "claude-code/opus" if model == "claude" else {"model": OSS, "backend": OLLAMA}
    return PageIndexClient(index=index, chat=chat)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--model", choices=["claude", "ollama"], default="claude")
    ap.add_argument("--storage", default=".pageindex_coklu")
    args = ap.parse_args()

    client = make_client(args.model, args.storage)

    # 1) Her PDF ayrı submit edilir (sırayla: Ollama eşzamanlı çok isteği reddedebilir)
    doc_ids = []
    for path in args.pdfs:
        t = time.time()
        r = client.submit_document(path)
        doc_ids.append(r["doc_id"])
        print(f"{os.path.basename(path)} -> {r['doc_id']} ({time.time() - t:.0f} sn)")

    # 2) Kayıtlı belgeler ve indekslemede otomatik üretilen açıklamalar
    print("\nBelgeler:")
    for d in client.list_documents()["documents"]:
        print(f"- {d['name']} ({d['pageNum']} sayfa): {d['description'][:110]}...")

    # 3) Tek belgeye soru: doc_id string
    q1 = f"{os.path.basename(args.pdfs[0])} belgesi ne anlatıyor? İki cümleyle yaz."
    print(f"\nSORU (tek belge): {q1}")
    print(client.chat(q1, doc_id=doc_ids[0]))

    # 4) Tüm belgelere soru: doc_id liste
    if len(doc_ids) > 1:
        q2 = "Her belge neyle ilgili? Belge adını belirterek birer cümleyle yaz."
        print(f"\nSORU (tüm belgeler): {q2}")
        print(client.chat(q2, doc_id=doc_ids))


if __name__ == "__main__":
    sys.exit(main())
