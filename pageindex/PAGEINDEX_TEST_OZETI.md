# PageIndex Testi: Blog Arşivi Üzerinde Değerlendirme

**Tarih:** 8 Kasım 2026
**Repo:** https://github.com/VectifyAI/PageIndex (MIT lisansı)
**Veri:** `anlkaynar.WordPress.2026-08-10.xml`: 341 yayınlanmış yazı, 2017–2024, ~44 bin kelime, yazı başına ortalama ~130 kelime
**Klasör:** `~/Documents/makeindex/` (`PageIndex/` repo, `blogtest/` test dosyaları)

---

## 1. PageIndex nedir?

Vektörsüz, akıl yürütmeye dayalı bir RAG yöntemi. Embedding ve chunking yok. Bunların yerine:

1. **İndeksleme:** Belgeden içindekiler benzeri bir **ağaç** çıkarır. Her düğümde başlık, sayfa aralığı ve özet bulunur.
2. **Retrieval:** LLM bir ajan gibi bu ağaçta gezinir. İki araç kullanır:
   - `get_document_structure()`: İskeleti getirir (başlık, sayfa, özet; **metin yok**)
   - `get_page_content(pages)`: Sadece seçilen sayfaların metnini getirir

Modeller LiteLLM üzerinden seçilebiliyor (OpenAI, Ollama vb.). `claude-code/` önekiyle Claude aboneliği de API anahtarı olmadan kullanılabiliyor.

---

## 2. Yapılanlar

| # | Adım | Sonuç |
|---|---|---|
| 1 | Repo klonlandı, kuruldu, birim testleri çalıştırıldı | **1122 geçti**, 107 atlandı (isteğe bağlı `anthropic` paketi kurulu değil), 0 hata |
| 2 | Blog XML'i tek PDF'e çevrildi (yıl → yazı başlıkları + yer imleri) | 174 sayfa |
| 3 | Flash modunda indekslendi: `claude-code/haiku` | 50 sn, ~628 bin token, 272 düğüm |
| 4 | 5 test sorusu soruldu: `claude-code/opus` | **5/5 doğru**, cevaplar orijinal XML ile doğrulandı |
| 5 | Yerel web arayüzü yapıldı | Sohbet, ağaç diyagramı, PDF'te kaynak sayfa |
| 6 | Ollama `gpt-oss:20b-cloud` ile indeksleme ve soru-cevap | 163 sn, 3/5 iyi, 1 hatalı, 1 bozuk metin |
| 7 | Markdown modu denendi (yıl → ay → yazı) | 420 düğüm, birebir yapı, ama soru-cevap yok |
| 8 | Vektör RAG (embeddinggemma) ile 8 soruluk karşılaştırma | Opus ile PageIndex 8/8, vektör 6/8; gpt-oss ile vektör 5/8, PageIndex 2/8 |

---

## 3. Soru-cevap sonuçları

| Soru | Claude Opus | gpt-oss:20b |
|---|---|---|
| Vagrant CentOS ssh sorunu | ✅ | ✅ |
| Archer VR300 Tivibu ayarı | ✅ Ekran görüntüsünün eksik olduğunu belirtti | ⚠️ Doğru ama yazıda olmayan menü yolu ekledi |
| Raspberry Pi yazıları | ✅ 7/7 + ilgili 4 yazı | ⚠️ İngilizce, 1 yazı eksik, 1 yıl yanlış |
| OpenAI'nin yapamadıkları | ✅ Detaylı ve doğru | ❌ Ana fikir doğru ama metin bozuk |
| Helm yazısı var mı? (yok) | ✅ "Yok" dedi, alternatif önerdi | ✅ "Yok" dedi, uydurmadı |
| Soru başına süre | 10–20 sn | 7–19 sn |

**Önemli gözlem:** Olmayan bir şey sorulduğunda iki model de uydurmadı. Kaynaklar sayfa numarasıyla geldi, doğrulamak kolay.

---

## 4. Nasıl çalışıyor? (ölçülen)

### İndeksleme
- **Flash (varsayılan):** Ağacın iskeletini **LLM değil, PDF düzeni** çıkarır (yazı boyutu, kalınlık, yer imleri). LLM sadece küçük düğümleri birleştirme sonrası genişletme ve **özet** için kullanılır. Kısa yazıları kurala göre birleştirdiği için 341 yazı 264 yazı düğümüne indi.
- **Standard:** Ağacı baştan sona LLM kurar (içindekiler sayfasını bulma, sayfa eşleme, doğrulama). Taranmış ya da düzeni bozuk PDF'ler için. Yavaş ve pahalı.
- **Markdown:** `#` başlıklarından ağacı birebir kurar, LLM sadece özet yazar.
- **Cloud (ücretli):** OCR, görsel ve tablo desteği, çok belgeli arama.

### Retrieval (Tivibu sorusunda izlendi)
```
get_document_structure  part 1-4  → ~260 bin karakter  (iskeletin tamamı)
get_page_content("165")           →   ~3 bin karakter  (tek sayfa metin)
```
- Metinler dahil tüm belge ~1,14 milyon karakter. Model sadece **~3 bin karakterini** okudu.
- Ama iskeletin **tamamını** okudu. Blog ağacı düz ve geniş (8 yıl × ~35 yazı) olduğu için model hangi dala gideceğine karar verebilmek için her şeye bakmak zorunda kalıyor.

---

## 5. Güçlü ve zayıf yanlar

### ✅ Güçlü
- Chunking ve embedding ayarı yok, "chunk sınırında bilgi bölündü" sorunu yok.
- Cevaplar **izlenebilir**: sayfa veya bölüm referansı veriyor.
- Belgede olmayanı uydurmuyor.
- Takip soruları sorulabiliyor (çok turlu konuşma).
- Yerelde çalışıyor, Claude aboneliği ya da Ollama ile ekstra API maliyeti olmadan.
- İndeksleme ucuz ve hızlı (bu blog için ~1 dk).

### ⚠️ Zayıf
- **Her soru iskeletin tamamını okuyor** (bu blogda ~60–70 bin token). Belge büyüdükçe maliyet ve gecikme doğrusal artar. Asıl ölçeklenme sınırı bu.
- **Soru başına 5–20 sn.** Vektör araması 1 saniyenin altında.
- **Görseller kayboluyor** (yerel modda). Ekran görüntüsündeki bilgi bulunamıyor.
- Yerel `chat()` **sadece PDF** kabul ediyor. Markdown ağacıyla doğrudan soru-cevap yapılamıyor.
- Küçük modellerde (gpt-oss:20b) cevap kalitesi belirgin şekilde düşüyor. İndeksleme için küçük model yeterli, **soru-cevap için güçlü model şart**.
- Markdown modunda eşzamanlılık sınırı yok (Ollama'yı boğdu, betikte sınırlamak gerekti). Üst düğümlerin özeti de boş kalıyor (`"# 2023"`).

---

## 6. Klasik (similarity) RAG ile karşılaştırma

> **Not:** Aşağıdaki genel karşılaştırma yöntemin yapısına dayanıyor. Ölçülmüş sonuçlar için bkz. **§6a**.

| | Similarity RAG | PageIndex |
|---|---|---|
| Arama | Sorunun embedding'ine en yakın chunk'lar | LLM ağaçta akıl yürüterek gezinir |
| "X hakkında ne yazmışım?" gibi **liste/kapsam** soruları | Zayıf (top-k sınırı) | **Güçlü** (Raspberry: 7/7 + 4) |
| Belgede **olmayan** konu | Benzer ama alakasız chunk getirir, uydurma riski | "Yok" diyor |
| Kesin terim / kod / sayı arama | Embedding kaçırabilir | Başlık veya özette varsa iyi |
| Hız | < 1 sn | 5–20 sn |
| Soru başına maliyet | Çok düşük | Yüksek (iskelet okuması) |
| Çok sayıda belge (binlerce) | İyi ölçeklenir | Zayıf (iskelet büyür) |
| Kurulum ve ayar | Chunk boyutu, overlap, embedding modeli | Neredeyse yok |

**Bu blog gibi bir arşiv için:** Güçlü bir modelle PageIndex daha doğru, özellikle liste sorularında. Küçük bir modelle ise similarity RAG daha iyi sonuç veriyor (bkz. §6a). Anlık arama ve çok büyük arşivlerde similarity RAG daha uygun. İkisini birlikte kullanmak da mümkün: önce vektörle aday yazıları daraltmak, sonra PageIndex ile akıl yürütmek.

---

## 6a. Ölçülen karşılaştırma: PageIndex ve Vektör RAG

**Kurulum:**
- **Vektör RAG:** `embeddinggemma` (Ollama, 768 boyut). Yazılar 200 kelimelik parçalara bölündü (40 kelime örtüşme), toplam 424 parça. Embedding 8 sn sürdü. Kosinüs benzerliğiyle en yakın 6 parça seçildi.
- **Adil karşılaştırma için** iki sistemde de cevabı aynı model yazdı: gpt-oss:20b ve Claude Opus. Prompt'ta "sadece parçalara dayan, kaynak ver, yoksa söyle" talimatı vardı.
- 8 soru: önceki 5 soru + 3 yeni (iki detay sorusu, bir liste sorusu). Doğru cevaplar önceden orijinal XML'den çıkarıldı.

**Sonuçlar** (✅ doğru ve eksiksiz · ⚠️ kısmen doğru, eksik veya ufak uydurma · ❌ yanlış, ciddi eksik veya uydurma):

| # | Soru (tür) | PageIndex + Opus | Vektör + Opus | PageIndex + gpt-oss | Vektör + gpt-oss |
|---|---|---|---|---|---|
| 1 | Vagrant ssh (detay) | ✅ | ✅ | ✅ | ✅ |
| 2 | Tivibu ayarı (detay) | ✅ | ✅ | ⚠️ menü yolu uydurdu | ✅ |
| 3 | Raspberry Pi yazıları (**liste**, 7 yazı) | ✅ 7/7 | ❌ 3/7 | ⚠️ 6/7, yıl hatası | ❌ 3/7 |
| 4 | OpenAI'nin yapamadıkları (detay) | ✅ | ✅ | ❌ bozuk metin | ⚠️ |
| 5 | Helm yazısı (**olmayan konu**) | ✅ | ✅ | ✅ | ✅ |
| 6 | Vagrant RAM (detay) | ✅ | ✅ | ⚠️ sonuç uydurdu | ✅ |
| 7 | SonarQube erişim (detay) | ✅ | ✅ | ❌ yazıda olmayan 4 adım ekledi | ✅ |
| 8 | Docker yazıları (**liste**, 5 yazı) | ✅ 5/5 | ⚠️ 4/5 | ❌ 3/5 | ⚠️ 4/5 |
| | **Tam doğru** | **8/8** | **6/8** | **2/8** | **5/8** |
| | **Medyan süre** | 12,5 sn | 8 sn | 11 sn | 4,4 sn |
| | **Modele giden bağlam** | ~250 bin+ karakter (iskelet) + sayfalar | ~6–8 bin karakter | ~250 bin+ karakter | ~6–8 bin karakter |

**Bulgular:**
1. **Güçlü modelle (Opus) PageIndex kazandı.** Fark tamamen **liste sorularından** geliyor. Vektör RAG en yakın 6 parçayla sınırlı. Raspberry sorusunda 6 parçanın 3'ü aynı kitap incelemesinden geldi, bu yüzden 4 yazıyı hiç göremedi. PageIndex ise iskeletin tamamına baktığı için hepsini buldu. Tek bir yazıyı soran detay sorularında ikisi eşit.
2. **Küçük modelle (gpt-oss:20b) vektör RAG kazandı.** PageIndex'te küçük model ~250 bin karakterlik iskeleti okuyup kendisi karar vermek zorunda. Bu durumda yolunu kaybediyor ve uyduruyor (SonarQube'da yazıda olmayan adımlar, Vagrant RAM'de olmayan bir sonuç). Vektör RAG'de ise modelin önüne sadece ilgili 6 parça konuyor ve iş kolaylaşıyor.
3. **Olmayan konu (Helm) sorusunda dört sistem de doğru "yok" dedi.** Vektör + Opus ayrıca "sadece 6 parça gördüm, kesin söyleyemem" diye dürüst bir uyarı ekledi.
4. **Vektör RAG yaklaşık 1,5–2,5 kat daha hızlı ve modele ~30–40 kat daha az bağlam gönderiyor.** Bu da soru başına maliyetin çok daha düşük olması demek.

**Sonuç:** "PageIndex similarity'den daha iyi" ifadesi **güçlü bir cevap modeliyle ve özellikle "hepsini listele" tipi sorularda** doğru. Tek bir bilgiyi soran sorularda fark yok, vektör RAG daha hızlı ve ucuz. Küçük modelle ise vektör RAG daha güvenilir.

**Sınırlar:** Örneklem küçük (8 soru), puanlamayı tek kişi yaptı. Vektör tarafında top-k=6 kullanıldı; liste sorularında k artırılırsa vektör RAG'in skoru yükselebilir. Vektör + Opus'un ilk sorusu 937 sn sürdü; bu `claude -p` ilk çağrısında bir takılmaydı ve medyana dahil edilmedi.

**Dosyalar:** `vector_rag.py` (vektör RAG), `compare.py` (karşılaştırma), `compare_results.json` (tüm cevaplar ve süreler), `vector_index.json` (embedding'ler).

---

## 7. Dosyalar

| Dosya | Açıklama |
|---|---|
| `blogtest/anil-blog.pdf` | Blogdan üretilen PDF (174 sayfa) |
| `blogtest/anil-blog.md` | Blogdan üretilen Markdown (yıl → ay → yazı) |
| `blogtest/tree.json` | Flash ağacı (Claude haiku) |
| `blogtest/tree_ollama.json` | Flash ağacı (gpt-oss) |
| `blogtest/tree_md.json` | Markdown ağacı (gpt-oss özetleri) |
| `blogtest/answers.txt`, `answers_ollama.txt` | Test cevapları |
| `blogtest/server.py`, `index.html` | Web arayüzü |
| `blogtest/ask.py`, `ollama_test.py`, `md_index.py` | Test betikleri |
| `blogtest/vector_rag.py`, `compare.py`, `compare_results.json` | Vektör RAG ve karşılaştırma |

**Arayüzü başlatmak için:**
```bash
cd ~/Documents/makeindex/blogtest && ../PageIndex/.venv/bin/python server.py
# http://127.0.0.1:8765, sağ üstten model seçilir (Claude Opus / gpt-oss)
```

---

## 8. Önerilen sonraki adımlar

1. ~~**Similarity RAG ile karşılaştırma**~~ ✅ Yapıldı (bkz. §6a). Sonraki adım: soru setini 20–30 soruya çıkarmak ve vektör tarafında farklı top-k değerlerini denemek.
2. **Hibrit retrieval:** Soru tipine göre yönlendirme. Detay soruları vektör RAG'e (hızlı ve ucuz), liste ve kapsam soruları PageIndex'e. Ya da önce vektörle aday yazıları daraltıp sonra PageIndex ile akıl yürütmek.
3. **Hibrit model:** İndeksleme gpt-oss (Ollama) ile, soru-cevap Claude Opus ile. PageIndex'te soru-cevap için küçük model kullanılmamalı (§6a).
4. **Derin ağaç ve hiyerarşik özet:** Yıl ve ay düğümlerine alt yazılardan özet eklemek. Model önce 8 yılı görür, ilgili dalı açar. Her soruda ~250 bin karakter yerine birkaç bin karakter okur, maliyet ve gecikme ciddi düşer.
5. **Markdown ağacı için soru-cevap katmanı:** PDF'e çevirmeden, kod blokları ve orijinal başlıklar korunarak.
6. **Görseller:** Ekran görüntüsü içeren yazılar için bulut OCR ya da görsel okuyabilen bir model.
