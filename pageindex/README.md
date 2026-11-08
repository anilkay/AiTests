# PageIndex

[PageIndex](https://github.com/VectifyAI/PageIndex) (vektörsüz, akıl yürütmeye dayalı RAG) denemeleri.

| Dosya | İçerik |
|---|---|
| [`PAGEINDEX_TEST_OZETI.md`](PAGEINDEX_TEST_OZETI.md) | Blog arşivi (341 yazı) üzerinde yapılan testler, nasıl çalıştığı ve vektör RAG ile 8 soruluk karşılaştırma |
| [`ornek.py`](ornek.py) | Bir PDF'i indeksleyip soru soran küçük örnek |

## Örneği çalıştırma

```bash
pip install -U "pageindex[claude]"

# Claude aboneliği ile (API anahtarı gerekmez; Claude Code'da giriş yapılmış olmalı)
python ornek.py belge.pdf "Bu belge ne hakkında?"

# Ollama ile (ollama çalışıyor olmalı)
python ornek.py belge.pdf "Bu belge ne hakkında?" --model ollama

# Ağacı da göster
python ornek.py belge.pdf --agac "Özetle"

# Etkileşimli sohbet (takip soruları çalışır, boş satır çıkar)
python ornek.py belge.pdf
```

İlk çalıştırmada PDF indekslenir ve `.pageindex_ornek/<model>/` altına kaydedilir. Sonraki sorular kayıtlı indeksi kullanır.

**Örnek çıktı** (repodaki `2023-annual-report-truncated.pdf`, 50 sayfa, Ollama `gpt-oss:20b-cloud`): indeksleme 42 sn, kayıtlı indeksle soru başına ~5 sn.

```
- Preface  (s. 1-5)
- About the Federal Reserve  (s. 5-6)
- 1 Overview  (s. 7-8)
- 2 Monetary Policy and Economic Developments  (s. 9-20)
  - March 2024 Summary  (s. 9-14)
  - June 2023 Summary  (s. 15-20)
- 3 Financial Stability  (s. 21-30)
...
```

## Kısa sonuç

- Güçlü bir cevap modeliyle (Claude Opus) PageIndex, vektör RAG'den daha doğru. Fark özellikle "hepsini listele" tipi sorularda belirgin.
- Küçük bir modelle (gpt-oss:20b) vektör RAG daha güvenilir.
- İndeksleme için basit bir model yeterli. Soru-cevap için güçlü model şart.

Detaylar: [`PAGEINDEX_TEST_OZETI.md`](PAGEINDEX_TEST_OZETI.md)
