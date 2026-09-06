<h1 align="center">Luna No. 7</h1>

<p align="center">
  Gece vardiyasındaki minyatür bir lunapark. Tek dosya, tek sahne,<br>
  üç atmosfer modu — açtığınız anda dönmeye başlar.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/dosya-1-FF4D4F?style=flat-square" alt="1 dosya">
  <img src="https://img.shields.io/badge/atmosfer%20modu-3-FF4D4F?style=flat-square" alt="3 mod">
  <img src="https://img.shields.io/badge/three.js-0.128.0-FF4D4F?style=flat-square" alt="three 0.128.0">
</p>

---

## Ne yapıyor

`index.html` tarayıcıda çalışan bir WebGL sahnesi açar: dönme dolap, kapalı
devre bir hız treni, atlıkarınca ve üç satış standı. Kamera OrbitControls ile
sürüklenip yakınlaştırılır; kullanıcı üç saniye dokunmazsa kendi kendine tur
atmaya döner.

| Etkileşim | Sonuç |
|---|---|
| Sürükle | Sahneyi yatay/dikey döndürür (`maxPolarAngle` ile ufkun altına inilemez) |
| Tekerlek / iki parmak | 14–34 birim arasında yakınlaşma |
| **Gündüz** | Mavi gökyüzü, yıldızlar kapanır, neon yayımı %7'ye düşer |
| **Normal Gece** | Varsayılan mod: lacivert gökyüzü, tam neon, 450 yıldız |
| **Festival** | Mor gökyüzü, %175 neon, nokta ışıkları renk döngüsüne girer |

Mod geçişleri anlık değil: arka plan, sis, ışık şiddetleri ve tone-mapping
pozlaması her karede hedefe doğru yumuşatılır.

## Nasıl çalıştırılır

```bash
git clone https://github.com/umutseve4/luna-no-7.git
cd luna-no-7
python3 -m http.server 8000   # ya da dosyayı doğrudan tarayıcıya sürükleyin
```

Derleme adımı, paket yöneticisi ve yapılandırma dosyası yoktur.

## Nasıl doğrulanıyor

`qa` iş akışı her push ve her PR'da çalışır ve sahnenin bağlı olduğu
değişmezleri denetler: tam olarak iki dış betik ve ikisi de `https`, tek ve
sabitlenmiş `three` sürümü, `data-m` düğmelerinin day/night/festival üçlüsü ile
`T` palet tablosundaki karşılıkları, `prefers-reduced-motion` sorgusu, görünür
klavye odak halkası, `aria-label` ve — sayfanın çevrimdışı kalması için — hiçbir
`fetch(`, `XMLHttpRequest`, `localStorage`, `sessionStorage` ya da `sendBeacon`
kullanımının bulunmaması. Bu README'nin yukarıdaki sözleşmeyi anlatmayı
sürdürdüğü de aynı adımda doğrulanır.

## Sınırlar

- **Bağımlılık CDN'den geliyor.** `three` 0.128.0 ve `OrbitControls` jsDelivr
  üzerinden yükleniyor; ağ yoksa sayfa siyah kalır. Sürüm sabit, ama dosyalar
  bu depoda değil.
- **Ölçülmüş bir kare hızı iddiası yok.** Piksel oranı 1.6 ile sınırlandı ve
  gölge haritası 1024×1024'te tutuldu; bunlar makul varsayılanlar, ölçüm değil.
  Depoda benchmark yok.
- **`prefers-reduced-motion` hareketi yavaşlatır, kaldırmaz.** Dönme dolap,
  tren ve atlıkarınca %18 hızla dönmeye devam eder; otomatik kamera turu ise
  tamamen kapanır.
- **Festival modundaki renk döngüsü, azaltılmış hareket tercihinde durur** —
  ancak yüksek neon parlaklığı yerinde kalır.
- **Sahne tamamen elle modellenmiştir; gerçek bir lunaparkı temsil etmez.**
  Ölçüler, isimler ve yerleşim uydurmadır.
- **Bu depo `neon-lunapark-webgl`'in küçük öncülüdür.** Daha büyük, daha
  ayrıntılı sahne orada yaşıyor; bu dosya kasıtlı olarak sade tutuldu.

---

MIT — bkz. [`LICENSE`](./LICENSE).
