# İklim Bilgilendirme Botu (Türkçe)

Bu proje, kara, deniz ve atmosfer (hava) ile ilgili iklim sorunlarını ve olası sonuçlarını Türkçe olarak anlatan basit bir Discord botudur.

🔧 Gereksinimler
- Python 3.8+
- `discord.py` ve `python-dotenv` (requirements.txt'de listelenmiştir)

Kurulum
1. Sanal ortam oluşturup etkinleştirin (isteğe bağlı)
2. Paketleri yükleyin:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. `.env.example` dosyasını `.env` olarak kopyalayın ve `DISCORD_TOKEN` değerini bot token'ınız ile değiştirin.
4. Botu çalıştırın:
   ```bash
   python bot.py
   ```

Kullanım
- `!yardım` - Tüm komutları listeler
- `!kara-iklim` / `!kara-sonuç`
- `!hava-iklim` / `!hava-sonuç`
- `!deniz-iklim` / `!deniz-sonuç`

Notlar
- Komutlar Türkçe ve kısa, etkili anlatım olacak şekilde tasarlanmıştır.
- Komutlar spam'a karşı kullanıcı başına 8 saniye cooldown'a sahiptir.

Görseller (opsiyonel)
- `!deniz-sonuç` komutu hem bilgilendirici metni gönderir hem de `assets/images/` klasöründe bulunan ilgili görselleri (açıklamalarıyla birlikte) paylaşır.
- Klasöre şu dosyaları koymanızı öneririz (isimler kritik değil ama tavsiye edilir):
  - `ice_polar_bear.jpg` — buz erimesi / habitat kaybı örneği
  - `dry_shore.jpg` — kıyı bozulması / çekilme örneği
  - `plastic_shore.jpg` — kıyıda plastik atık birikimi
- `!kara-sonuç` komutu da bilgilendirici metni gönderir ve `assets/images/` klasöründe "kara" ile ilgili görselleri (adı içinde `kara`, `kurak`, `su`, `orman` gibi anahtar kelimeler olan) açıklamalarıyla paylaşır.
- `!hava-sonuç` komutu bilgilendirici metni gönderir ve `assets/images/` klasöründe hava ile ilgili görselleri (dosya adlarında `smog`, `smoke`, `kirlilik`, `fırtına`, `sıcak` gibi anahtar kelimeler bulunan) açıklamalarıyla paylaşır.
- `!duyuru` komutu yalnızca kullanıcı ID'si `944306257706238044` olan kullanıcı tarafından kullanılabilir; bu kullanıcı anlık duyuru gönderebilir.
- Görüntüler eklenmemişse bot yalnızca metni gönderir ve eksik dosyalar için uyarı verir.

