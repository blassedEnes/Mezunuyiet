import os
import textwrap
import logging
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise RuntimeError('DISCORD_TOKEN environment variable not found. Copy .env.example to .env and set DISCORD_TOKEN=<your token>')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

logging.basicConfig(level=logging.INFO)

# Utility: simple embed builder
def make_embed(title: str, description: str, color=0x2ECC71):
    e = discord.Embed(title=title, description=description, color=color)
    return e

# --- Bildirim & zamanlayıcı ayarları
ANNOUNCE_CHANNEL_ID = 1424404764031979589  # Duyuruların gönderileceği kanal ID
AUTHORIZED_USER_ID = 944306257706238044   # Sadece bu kullanıcı ID'si !duyuru komudunu kullanabilir
# Logo dosyası (duyurular için kullanılır)
ANNOUNCE_LOGO = 'assets/images/bak-logo.png'

# 24 adet pazartesi için bilgilendirici uzun metin (örnekler)
MONDAY_MESSAGES = [
    """İklim değişikliği küresel bir tehdittir: sera gazı emisyonlarının artması gezegenin ortalama sıcaklığını yükseltiyor, ekosistemleri ve insanların geçim kaynaklarını tehdit ediyor. Azaltım ve adaptasyon politikalarıyla emisyonları düşürmek, toplulukların dayanıklılığını artırmak hayati önemdedir.""",
    """Enerji dönüşümü: Fosil yakıtlardan yenilenebilir enerji kaynaklarına geçiş hızlandırılmalıdır. Hem kamu hem de özel sektör yatırımlarında temiz enerjiye öncelik verilmesi ekonomik fırsatlar yaratır ve emisyonları azaltır.""",
    """Tarım ve gıda güvenliği: İklim değişikliği tarımsal verimliliği etkileyerek gıda arzını tehdit eder. Sürdürülebilir tarım uygulamaları, su verimliliği ve dirençli çeşitlerin kullanımı önemlidir.""",
    """Su kıtlığı: Kuraklık olayları ve değişen yağış modelleri su kaynaklarını baskı altına alıyor. Etkin su yönetimi, tasarruf teknolojileri ve suyu koruyan tarımsal yöntemler kaçınılmazdır.""",
    """Ormanların korunması: Ormanlar karbon depolarıdır ve biyolojik çeşitliliği korur. Yeniden ağaçlandırma ve orman yönetimi orman kaybını azaltır, iklim düzenlemesine katkı sağlar.""",
    """Kentleşme ve ısı adası etkisi: Şehirlerde sıcaklık artışları insan sağlığını ve enerji talebini etkiler. Yeşil altyapılar, ağaçlandırma ve soğutma stratejileri gereklidir.""",
    """Deniz seviyesi yükselmesi: Kıyı alanları erozyon ve taşkına daha duyarlı hale geliyor. Kıyı koruma, geri çekilme planları ve uyum stratejileri yaşam alanlarını korur.""",
    """Biyoçeşitliliğin korunması: Tür kayıpları ekosistemlerin işlevini bozar. Habitat koruma ve bağlantılı ekosistem planlaması biyoçeşitliliğin sürdürülmesine katkı sağlar.""",
    """Hava kirliliği ve sağlık: Endüstriyel emisyonlar ve ulaşım kaynaklı kirlilik solunum yolu hastalıklarını artırır. Temiz hava politikaları hem sağlık hem de iklim faydası getirir.""",
    """Aşırı hava olayları: Fırtınalar, seller ve yangınlar daha sık ve şiddetli hale geliyor. Erken uyarı sistemleri, afet hazırlığı ve dayanıklılık yatırımları can kaybını azaltır.""",
    """Ekonomik etkiler: İklim değişikliği altyapıyı, tarımı ve iş gücünü etkileyerek ekonomik maliyetlere yol açar. Yeşil yatırımlar uzun vadede ekonomik istikrarı destekler.""",
    """Gençlik ve eğitim: İklim eğitimi gençlerin bilincini artırır ve sürdürülebilir davranışları teşvik eder. Toplum temelli eğitim programları yerel çözümler üretir.""",
    """Döngüsel ekonomi: Atık azaltma, geri dönüşüm ve kaynak verimliliği emisyonları düşürür. Endüstriyel süreçlerde verimlilik ve atık yönetimi önemlidir.""",
    """Ulaşımda temiz yakıtlar: Elektrikli ve düşük emisyonlu ulaşım çözümleri kentlerde hava kalitesini iyileştirir. Toplu taşımanın güçlendirilmesi ulaşım kaynaklı emisyonları azaltır.""",
    """Sağlık altyapısı: İklim kaynaklı hastalık riskine karşı sağlık sistemleri güçlendirilmeli. Özellikle sıcak dalgalarına ve hava kirliliğine hazırlıklı olunmalı.""",
    """Tarımsal direnç: Kuraklığa dayanıklı tohumlar ve sürdürülebilir sulama tarımsal verimliliği korur. Ayrıca küçük üreticilere destek programları gereklidir.""",
    """Kıyı yönetimi: Kıyı ekosistemleri ve yerleşimler korunmalı; deniz koruma alanları ve adaptasyon planları geliştirilmeli.""",
    """İklim göçü: İklim etkileri nedeniyle yer değiştirmeler artıyor; planlama ve koruma politikaları göçü yönetmede rol oynar.""",
    """Sera gazı azaltımı: Enerji verimliliği, yenilenebilir enerji ve karbon yönetimi ile emisyonlar düşürülebilir. Uluslararası iş birliği önem taşır.""",
    """Finansman ve yatırım: İklim amaçlı finansman mekanizmaları ve yeşil tahviller sürdürülebilir projelere kaynak sağlar.""",
    """Toplum dayanıklılığı: Yerel kapasite artışı, afet yönetimi ve sosyal güvenlik ağları toplumları güçlendirir.""",
    """Hukuk ve politika araçları: Etkili mevzuat, izleme ve raporlama mekanizmaları politika hedeflerine ulaşılmasını sağlar.""",
    """Toplumsal katılım: Yerel topluluklar, sivil toplum ve özel sektör birlikte çalışmalı; bireysel sorumluluk teşvik edilmelidir.""",
]

async def send_announcement(channel, message_text):
    """Belirtilen kanala duyuru gönderir; logo mevcutsa altına ekler."""
    embed = make_embed('📢 İklim Duyurusu', message_text)

    # Logo dosyası mevcutsa ekle
    if os.path.exists(ANNOUNCE_LOGO):
        try:
            file = discord.File(ANNOUNCE_LOGO, filename=os.path.basename(ANNOUNCE_LOGO))
            embed.set_image(url=f'attachment://{os.path.basename(ANNOUNCE_LOGO)}')
            await channel.send(content='@everyone', embed=embed, file=file, allowed_mentions=discord.AllowedMentions(everyone=True))
        except Exception as e:
            logging.exception('Duyuru gönderilirken hata: %s', e)
            await channel.send(content='@everyone', embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))
    else:
        await channel.send(content='@everyone', embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))

async def hourly_monday_announcer():
    """Her saat başında (yerel saatle) Pazartesi günleri ilgili mesajı gönderir."""
    # Bot başlatıldığında bir sonraki saat başına kadar bekle
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now()
        # bir sonraki saat başını hesapla
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=5, microsecond=0)
        wait_seconds = (next_hour - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        now = datetime.now()
        # Sadece Pazartesi (weekday()==0) ise gönder
        if now.weekday() == 0:
            hour_index = now.hour % len(MONDAY_MESSAGES)
            message_text = MONDAY_MESSAGES[hour_index]
            try:
                channel = bot.get_channel(ANNOUNCE_CHANNEL_ID) or await bot.fetch_channel(ANNOUNCE_CHANNEL_ID)
                if channel:
                    await send_announcement(channel, message_text)
                    logging.info('Pazartesi duyurusu gönderildi: saat %s', now.hour)
                else:
                    logging.warning('Duyuru kanalı bulunamadı: %s', ANNOUNCE_CHANNEL_ID)
            except Exception as ex:
                logging.exception('Duyuru gönderilirken hata: %s', ex)

# -- Yardım komutu
@bot.command(name='yardım', aliases=['yardim'])
@commands.cooldown(1, 8, commands.BucketType.user)
async def yardim(ctx):
    """Tüm komutları ve kısa açıklamalarını gösterir."""
    text = textwrap.dedent(
        """
        **Kullanılabilir Komutlar**

        🔹 **!yardım** - Tüm komutları ve bot işlevlerini listeler.

        🌿 **Kara Komutları**
        • **!kara-iklim** - Kara ekosistemindeki iklim sorunlarını açıklar.
        • **!kara-sonuç** - Bu sorunların gelecekteki sonuçlarını ve çözüm önerilerini gösterir.

        ☁️ **Hava Komutları**
        • **!hava-iklim** - Atmosfer ve hava olaylarına ilişkin iklim sorunlarını açıklar.
        • **!hava-sonuç** - Atmosfer sorunlarının gelecekteki etkilerini ve çözümlerini anlatır.

        🌊 **Deniz Komutları**
        • **!deniz-iklim** - Denizlerdeki iklim değişikliği etkilerini açıklar.
        • **!deniz-sonuç** - Deniz sorunlarının gelecekteki etkileri ve çözüm önerilerini gösterir.

        Komutları basit ve etkili şekilde özetler; örnek: `!kara-iklim` veya `!deniz-sonuç`.
        """
    )
    embed = make_embed('📚 Yardım - Komut Listesi', text, color=0x3498DB)
    await ctx.send(embed=embed)

# -- Kara: sorunlar
@bot.command(name='kara-iklim')
@commands.cooldown(1, 8, commands.BucketType.user)
async def kara_iklim(ctx):
    """Kara ekosistemindeki iklim sorunlarını açıklar."""
    text = textwrap.dedent(
        """
        **Kara Ekosistemi - Temel İklim Sorunları**

        • **Ormansızlaşma:** Habitat kaybı, karbon tutma kapasitesinin azalması.
        • **Kuraklık:** Su kaynaklarının azalması, tarım verim düşüşü.
        • **Erozyon:** Toprak kaybı ve verim düşüşü.
        • **Toprak verimsizliği:** Besin döngüsünde bozulma, azalmuş ürün kalitesi.
        • **Tarım alanlarının zarar görmesi:** Gıda güvencesi riskleri.
        """
    )
    embed = make_embed('🌿 Kara - İklim Sorunları', text)
    await ctx.send(embed=embed)

# -- Kara: sonuç ve çözümler
@bot.command(name='kara-sonuç')
@commands.cooldown(1, 8, commands.BucketType.user)
async def kara_sonuc(ctx):
    """Kara ekosistemindeki sorunların sonuçlarını ve çözüm önerilerini sunar."""
    text = textwrap.dedent(
        """
        **Olası Sonuçlar (Gelecek Senaryoları)**

        • **Tarım krizleri:** Gıda arzında dalgalanmalar, fiyat artışları.
        • **Su kıtlığı:** Yerel ve bölgesel su stresi.
        • **Biyoçeşitliliğin azalması:** Tür kayıpları ve ekosistem işlevselliğinin bozulması.

        **Çözüm Önerileri**
        • Yeniden ormanlandırma ve koruma programları.
        • Sürdürülebilir tarım ve su yönetimi.
        • Toprak koruma ve erozyon önleme yöntemleri.
        """
    )
    embed = make_embed('🌿 Kara - Sonuçlar & Çözümler', text, color=0xE67E22)
    await ctx.send(embed=embed)

    # Dinamik görsel tarama: assets/images içinde kara ile ilgili görselleri gönder
    images_dir = 'assets/images'
    allowed_exts = ('.jpg', '.jpeg', '.png', '.gif')

    if not os.path.isdir(images_dir):
        logging.warning('Görsel klasörü yok: %s', images_dir)
        await ctx.send(f'⚠️ Görsel klasörü bulunamadı: `{images_dir}` — lütfen görselleri ekleyin.')
        return

    files = [f for f in os.listdir(images_dir) if f.lower().endswith(allowed_exts)]
    # Filtreleme: kara ile ilgili görseller (dosya adında kara/kurak/orman/forest/su gibi anahtar kelimeler varsa)
    land_keywords = ('kara', 'kurak', 'drought', 'su', 'dry', 'orman', 'forest', 'tarla', 'soil', 'erozyon', 'çöl', 'desert')
    land_files = [f for f in files if any(k in f.lower() for k in land_keywords)]

    if not land_files:
        await ctx.send('⚠️ `assets/images/` klasöründe kara ile ilgili görsel bulunamadı. Yine de metin gönderildi.')
        return

    def make_land_caption(filename: str) -> str:
        name = filename.lower()
        if any(k in name for k in ('kurak', 'drought', 'dry', 'su yok')):
            return 'Kuraklık ve su kıtlığı sonucunda çatlamış toprak ve azalan ürün verimi — tarımsal üretime etkiler.'
        if any(k in name for k in ('orman', 'forest', 'deforest', 'ağac', 'agac')):
            return 'Ormansızlaşma sonucu habitat kaybı ve karbon depolama kapasitesinde azalma.'
        if any(k in name for k in ('erozyon', 'soil', 'toprak')):
            return 'Erozyon ve toprak verimsizliği — toprağın kaybı ve tarım alanlarının bozulması.'
        return f'Görsel: `{filename}` — kara ekosistemine ilişkin bir etkiyi gösterir.'

    for filename in sorted(land_files):
        path = os.path.join(images_dir, filename)
        try:
            file = discord.File(path, filename=filename)
            caption = make_land_caption(filename)
            e = discord.Embed(description=caption)
            e.set_image(url=f'attachment://{filename}')
            await ctx.send(embed=e, file=file)
        except Exception as ex:
            logging.exception('Görsel gönderilemedi: %s', ex)
            await ctx.send('Görsel gönderilirken bir hata oluştu.')

# -- Hava: sorunlar
@bot.command(name='hava-iklim')
@commands.cooldown(1, 8, commands.BucketType.user)
async def hava_iklim(ctx):
    """Atmosfer ve hava olaylarına ilişkin sorunları açıklar."""
    text = textwrap.dedent(
        """
        **Atmosfer - Temel İklim Sorunları**

        • **Sera gazı artışı:** Küresel ısınma ve iklim değişikliği.
        • **Hava kirliliği:** Sağlık sorunları, asit yağmurları.
        • **Aşırı sıcaklık değişimleri:** Isı dalgaları ve soğuk dalgalar.
        • **Ani hava olayları:** Şiddetli fırtınalar ve seller.
        """
    )
    embed = make_embed('☁️ Hava - İklim Sorunları', text, color=0x9B59B6)
    await ctx.send(embed=embed)

# -- Hava: sonuç ve çözümler
@bot.command(name='hava-sonuç')
@commands.cooldown(1, 8, commands.BucketType.user)
async def hava_sonuc(ctx):
    """Atmosfer sorunlarının gelecek etkilerini, çözüm önerilerini ve ilgili görselleri gönderir."""
    text = textwrap.dedent(
        """
        **Olası Sonuçlar (Gelecek Senaryoları)**

        • **Fırtına ve kasırgalar:** Altyapı hasarları, göçler.
        • **Hava kirliliği kaynaklı hastalıklar:** Solunum yolu hastalıkları artışı.
        • **Ozon tabakası problemleri:** UV maruziyeti artışı.

        **Çözüm Önerileri**
        • Emisyon azaltımı (yenilenebilir enerji, enerji verimliliği).
        • Kirlilik kontrolü ve temiz ulaşım çözümleri.
        • Erken uyarı sistemleri ve afet yönetimi planları.

        Aşağıdaki görseller, atmosferle ve hava olaylarıyla ilişkili bazı sonuçları göstermektedir.
        """
    )
    embed = make_embed('☁️ Hava - Sonuçlar & Çözümler', text, color=0xF1C40F)
    await ctx.send(embed=embed)

    # Dinamik görsel tarama: assets/images içinde hava ile ilgili görselleri gönder
    images_dir = 'assets/images'
    allowed_exts = ('.jpg', '.jpeg', '.png', '.gif')

    if not os.path.isdir(images_dir):
        logging.warning('Görsel klasörü yok: %s', images_dir)
        await ctx.send(f'⚠️ Görsel klasörü bulunamadı: `{images_dir}` — lütfen görselleri ekleyin.')
        return

    files = [f for f in os.listdir(images_dir) if f.lower().endswith(allowed_exts)]
    # Filtreleme: hava ile ilgili görseller (dosya adında hava/asmog/smoke/pollut gibi anahtar kelimeler varsa)
    air_keywords = ('hava', 'smog', 'smoke', 'pollut', 'pollution', 'hava kirlili', 'kirlilik', 'fırtına', 'storm', 'sıcak', 'heat', 'sıcaklık', 'dust', 'toz')
    air_files = [f for f in files if any(k in f.lower() for k in air_keywords)]

    if not air_files:
        await ctx.send('⚠️ `assets/images/` klasöründe hava ile ilgili görsel bulunamadı. Yine de metin gönderildi.')
        return

    def make_air_caption(filename: str) -> str:
        name = filename.lower()
        if any(k in name for k in ('smog', 'smoke', 'pollut', 'kirlilik')):
            return 'Sanayi ve insan kaynaklı emisyonlar sonucu oluşan hava kirliliği — solunum yolu hastalıkları ve çevresel etkiler.'
        if any(k in name for k in ('fırtına', 'storm', 'wind', 'gök')):
            return 'Ani hava olayları ve fırtınalara bağlı hasarlar — altyapı ve insan güvenliği riskleri.'
        if any(k in name for k in ('sıcak', 'heat')):
            return 'Aşırı sıcaklık ve ısı dalgaları — tarım, sağlık ve ekosistemler üzerinde baskı.'
        return f'Görsel: `{filename}` — atmosfer ve hava olaylarına ilişkin bir etkiyi gösterir.'

    for filename in sorted(air_files):
        path = os.path.join(images_dir, filename)
        try:
            file = discord.File(path, filename=filename)
            caption = make_air_caption(filename)
            e = discord.Embed(description=caption)
            e.set_image(url=f'attachment://{filename}')
            await ctx.send(embed=e, file=file)
        except Exception as ex:
            logging.exception('Görsel gönderilemedi: %s', ex)
            await ctx.send('Görsel gönderilirken bir hata oluştu.')

# -- Deniz: sorunlar
@bot.command(name='deniz-iklim')
@commands.cooldown(1, 8, commands.BucketType.user)
async def deniz_iklim(ctx):
    """Denizlerdeki iklim değişikliği etkilerini açıklar."""
    text = textwrap.dedent(
        """
        **Denizler - Temel İklim Sorunları**

        • **Deniz seviyesinin yükselmesi:** Kıyı erozyonu ve taşkın riski.
        • **Mercan beyazlaşması:** Mercan ekosistemlerinin çöküşü.
        • **Okyanus asitlenmesi:** Deniz canlılarının yaşamını tehdit eder.
        • **Deniz canlılarının yok olması:** Balıkçılık ve ekosistem kayıpları.
        """
    )
    embed = make_embed('🌊 Deniz - İklim Etkileri', text, color=0x1ABC9C)
    await ctx.send(embed=embed)

# -- Deniz: sonuçlar ve çözümler
@bot.command(name='deniz-sonuç')
@commands.cooldown(1, 8, commands.BucketType.user)
async def deniz_sonuc(ctx):
    """Denizlerdeki sorunların sonuçlarını, çözüm önerilerini ve ilgili görselleri gönderir."""
    text = textwrap.dedent(
        """
        **Olası Sonuçlar (Gelecek Senaryoları)**

        • **Kıyı şehirlerinin su altında kalması:** Yer değiştirmeler ve altyapı kayıpları.
        • **Balık stoklarının azalması:** Gıda güvenliği riskleri.
        • **Eko-sistem çöküşleri:** Ekonomik ve biyolojik etkiler.

        **Çözüm Önerileri**
        • Kıyı koruma ve iklim adaptasyon planları.
        • Deniz koruma alanları ve sürdürülebilir balıkçılık.
        • Karbon azaltım politikaları ve küresel iş birliği.

        Aşağıdaki görseller, denizlerle ve kıyılarla ilgili bazı olası sonuçları ve insan/iklim etkilerini göstermektedir.
        """
    )
    embed = make_embed('🌊 Deniz - Sonuçlar & Çözümler', text, color=0x2980B9)
    await ctx.send(embed=embed)

    # Dinamik görsel tarama: assets/images içinde bulunan bütün görselleri gönder
    images_dir = 'assets/images'
    allowed_exts = ('.jpg', '.jpeg', '.png', '.gif')

    if not os.path.isdir(images_dir):
        logging.warning('Görsel klasörü yok: %s', images_dir)
        await ctx.send(f'⚠️ Görsel klasörü bulunamadı: `{images_dir}` — lütfen görselleri ekleyin.')
        return

    files = [f for f in os.listdir(images_dir) if f.lower().endswith(allowed_exts)]
    if not files:
        await ctx.send('⚠️ `assets/images/` klasöründe görsel bulunamadı. Yine de metin gönderildi.')
        return

    def make_caption(filename: str) -> str:
        name = filename.lower()
        if any(k in name for k in ('ayi', 'bear', 'polar', 'buz')):
            return 'Buz parçacığında mahsur kalan kutup ayısı — artan deniz sıcaklıkları ve buzulların erimesi nedeniyle habitat kaybı.'
        if any(k in name for k in ('dry', 'kurum', 'cekil', 'çekil', 'kıyı', 'kiyi', 'shore')):
            return 'Kurumuş/çekilmiş kıyı manzarası — deniz seviyesi değişimleri ve aşırı iklim olaylarıyla kıyı ekosistemlerinin bozulması.'
        if any(k in name for k in ('plastic', 'trash', 'pis', 'cop', 'cop', 'çöp', 'atik', 'plasti')):
            return 'Kıyıda birikmiş plastik atıklar — insan faaliyetleri ve zayıf atık yönetimi nedeniyle deniz kirliliğinin artması.'
        return f'Görsel: `{filename}` — deniz ve kıyı etkilerini gösteren görsel.'

    for filename in sorted(files):
        path = os.path.join(images_dir, filename)
        try:
            file = discord.File(path, filename=filename)
            caption = make_caption(filename)
            e = discord.Embed(description=caption)
            e.set_image(url=f'attachment://{filename}')
            await ctx.send(embed=e, file=file)
        except Exception as ex:
            logging.exception('Görsel gönderilemedi: %s', ex)
            await ctx.send('Görsel gönderilirken bir hata oluştu.')

@bot.command(name='duyuru')
@commands.cooldown(1, 8, commands.BucketType.user)
async def duyuru(ctx, index: int = None):
    """Yetkili rolü olan kullanıcılar için anlık duyuru gönderme komutu. İsteğe bağlı index 0-23."""
    # Yetki kontrolü — komut DM'den veya sunucudan çalıştırılabilir.
    # Kontrol: kullanıcının hedef duyuru kanalının sunucusunda (guild) yetkili role sahip olup olmadığı.
    try:
        channel = bot.get_channel(ANNOUNCE_CHANNEL_ID) or await bot.fetch_channel(ANNOUNCE_CHANNEL_ID)
    except Exception as e:
        logging.exception('Duyuru kanalı alınamadı: %s', e)
        return await ctx.send('Duyuru kanalı bulunamadı; lütfen yöneticinize bildirin.')

    target_guild = getattr(channel, 'guild', None)
    if target_guild is None:
        return await ctx.send('Duyuru kanalı bir sunucuya bağlı değil; yapılandırmayı kontrol edin.')

    # Member'ı hedef sunucudan alın (DM veya farklı sunucudan da çalıştırılsa doğru kontrol sağlanır)
    member = None
    if isinstance(ctx.author, discord.Member) and ctx.guild == target_guild:
        member = ctx.author
    else:
        try:
            member = target_guild.get_member(ctx.author.id) or await target_guild.fetch_member(ctx.author.id)
        except discord.NotFound:
            member = None
        except Exception as e:
            logging.exception('Üye bilgisi alınırken hata: %s', e)
            return await ctx.send('Kullanıcı bilgileri alınamadı; lütfen sunucuda tekrar deneyin.')

    if member is None:
        return await ctx.send('Bu sunucuda üye olarak görünmüyorsunuz; komutu sunucuda yetkili kullanıcıyla veya DM üzerinden kullanamazsınız.')

    # Sadece belirli kullanıcı ID'sine izin ver
    if getattr(member, 'id', None) != AUTHORIZED_USER_ID:
        return await ctx.send('Bu komutu kullanmak için yetkili kullanıcı olmanız gerekir.')

    if index is None:
        hour = datetime.now().hour
        message = MONDAY_MESSAGES[hour % len(MONDAY_MESSAGES)]
    else:
        if index < 0 or index >= len(MONDAY_MESSAGES):
            return await ctx.send(f'Geçersiz index. 0 ile {len(MONDAY_MESSAGES)-1} arasında olmalı.')
        message = MONDAY_MESSAGES[index]

    try:
        channel = bot.get_channel(ANNOUNCE_CHANNEL_ID) or await bot.fetch_channel(ANNOUNCE_CHANNEL_ID)
        if not channel:
            return await ctx.send('Duyuru kanalı bulunamadı.')

        embed = make_embed('📢 İklim Duyurusu (Yetkili Gönderimi)', message)

        # Logo dosyası mevcutsa ekle
        if os.path.exists(ANNOUNCE_LOGO):
            try:
                file = discord.File(ANNOUNCE_LOGO, filename=os.path.basename(ANNOUNCE_LOGO))
                embed.set_image(url=f'attachment://{os.path.basename(ANNOUNCE_LOGO)}')
                await channel.send(content='@everyone', embed=embed, file=file, allowed_mentions=discord.AllowedMentions(everyone=True))
            except Exception as e:
                logging.exception('Duyuru gönderilirken hata: %s', e)
                await channel.send(content='@everyone', embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))
        else:
            await channel.send(content='@everyone', embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))

        await ctx.send('Duyuru gönderildi ✅')
    except Exception as ex:
        logging.exception('Duyuru gönderilemedi: %s', ex)
        await ctx.send('Duyuru gönderilirken hata oluştu.')

# -- Genel hata yönetimi: bilinmeyen komut
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Komut bulunamadı. Yardım için `!yardım` yazın.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Lütfen bekleyin. Bu komutu tekrar kullanmak için {round(error.retry_after)} saniye bekleyin.")
    else:
        # Log other errors
        logging.exception('Komut hatası: %s', error)
        await ctx.send('Bir hata oluştu; lütfen daha sonra tekrar deneyin.')

@bot.event
async def on_ready():
    print(f'Bot hazır. Kullanıcı: {bot.user} (ID: {bot.user.id})')
    await bot.change_presence(activity=discord.Game(name='!yardım | İklim bilgilendirme'))
    # Başlat: Pazartesi saatlik duyuru görevini başlat
    if not hasattr(bot, 'monday_task'):
        bot.monday_task = bot.loop.create_task(hourly_monday_announcer())
        print('Pazartesi saatlik duyuru görevi başlatıldı.')

if __name__ == '__main__':
    # Bot token should be provided via DISCORD_TOKEN environment variable (see .env)
    bot.run('token')
