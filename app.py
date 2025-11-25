import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
import altair as alt

# Streamlit sayfa ayarları
st.set_page_config(page_title="SmartMarket AI", layout="wide")

# Ana başlık
st.title(" SmartMarket AI")



# ================= SIDEBAR / SOL PANEL =================

st.sidebar.header("Piyasa Ayarları")

# Kullanıcının piyasa türü seçimi (Kripto / Borsa)
market_type = st.sidebar.radio("Piyasa Türü", ["Kripto", "Borsa"])

# Seçilen piyasa türüne göre varlık listesi belirlenir
if market_type == "Kripto":
    symbols = [
        "BTC-USD","ETH-USD","BNB-USD","SOL-USD",
        "XRP-USD","AVAX-USD","DOGE-USD","ADA-USD"
    ]
else:
    symbols = [
        "ASELS.IS","THYAO.IS","TUPRS.IS","FROTO.IS",
        "BIMAS.IS","GARAN.IS","ISCTR.IS","YKBNK.IS"
    ]

# Kullanıcının seçtiği varlık
symbol = st.sidebar.selectbox("Varlık Seç", symbols)

# Tarih aralığı seçimi (TR format)
start_date = st.sidebar.date_input("Başlangıç Tarihi", datetime(2024,1,1), format="DD.MM.YYYY")
end_date = st.sidebar.date_input("Bitiş Tarihi", datetime.today(), format="DD.MM.YYYY")


# ================= VERİ ÇEKME =================
# Seçilen varlık ve tarih aralığına göre Yahoo Finance üzerinden veri alınır
data = yf.download(symbol, start=start_date, end=end_date)

# Sayfa ikiye bölünür (grafik + AI panel)
col1, col2 = st.columns([3,1])


# ================= GRAFİK PANELİ =================

with col1:
    st.subheader(f"Fiyat Grafiği ({symbol})")

    if not data.empty:
        # Grafik için sadece Date ve Close sütunları kullanılır
        df = data.reset_index()[["Date", "Close"]]

        # Altair ile modern ve etkileşimli çizgi grafik
        chart = alt.Chart(df).mark_line(color="#00b4d8").encode(
            x=alt.X("Date:T", title="Tarih"),
            y=alt.Y("Close:Q", title="Fiyat"),
            tooltip=["Date:T", "Close:Q"]  # Hover ile değer gösterimi
        ).interactive().properties(
            height=450
        )

        st.altair_chart(chart, use_container_width=True)

    else:
        st.warning("Veri bulunamadı.")


# ================= AI ANALİZ PANELİ =================

with col2:
    st.subheader(" AI Piyasa Yorumu")

    # Yeterli veri varsa analiz yapılır
    if not data.empty and len(data["Close"]) > 10:

        close_prices = data["Close"].astype(float)

        # İlk ve son fiyatlar
        first_price = float(close_prices.iloc[0])
        last_price = float(close_prices.iloc[-1])

        # Yüzdelik değişim hesabı
        change = ((last_price - first_price) / first_price) * 100

        # 5 günlük hareketli ortalama
        moving_avg = float(close_prices.rolling(window=5).mean().iloc[-1])

        # Fiyat ortalamanın üstünde mi altında mı?
        trend_direction = "ÜZERİNDE" if last_price > moving_avg else "ALTINDA"

        # Volatilite (fiyat dalgalanma seviyesi)
        volatility = float(close_prices.std())
        avg_price = float(close_prices.mean())
        volatility_level = "Yüksek" if volatility > avg_price * 0.05 else "Düşük"

        # Momentum (son 5 günün hareket gücü)
        momentum = last_price - float(close_prices.iloc[-5])

        # AI karar mantığı
        if change > 5:
            panel = st.success
            yorum = f"""
 GÜÇLÜ YÜKSELİŞ TRENDİ

 Toplam Değişim: %{round(change,2)}
 Fiyat, kısa vadeli ortalamanın {trend_direction} seyrediyor.

 Teknik Analiz:
Yükseliş hareketi istikrarlı. Momentum pozitif, alım isteği güçlü.

 Volatilite Seviyesi: {volatility_level}

 Strateji:
Kısa vadede kar satışları gelebilir. Kademeli alım önerilir.
"""
        elif change < -5:
            panel = st.error
            yorum = f"""
BELİRGİN DÜŞÜŞ TRENDİ

 Toplam Değişim: %{round(change,2)}
 Fiyat, kısa vadeli ortalamanın {trend_direction} bulunuyor.

 Teknik Analiz:
Satış baskısı güçlü, momentum negatif.

 Volatilite Seviyesi: {volatility_level}

Strateji:
Net toparlanma görülmeden pozisyon açmak risklidir.
"""
        else:
            panel = st.info
            yorum = f"""
➖ YATAY / KARARSIZ PİYASA

Toplam Değişim: %{round(change,2)}
Fiyat, kısa vadeli ortalamanın {trend_direction} konumunda.

Teknik Analiz:
Piyasa yönsüz. Kararsızlık hakim.

 Volatilite Seviyesi: {volatility_level}

 Strateji:
Net yön oluşana kadar gözlem tavsiye edilir.
"""

        # AI paneline sonucu yazdır
        panel(yorum)
    else:
        st.info("AI analiz için yeterli veri toplanıyor.")


# ================= ALT METRİKLER =================

st.markdown("---")
st.subheader(" Fiyat İstatistikleri")

colA, colB, colC = st.columns(3)

if not data.empty:
    # Para birimi belirleme
    para = "₺" if symbol.endswith(".IS") else "$"

    # İstatistiksel değerler
    colA.metric("🔺 En Yüksek", f"{round(float(data['Close'].max()),2)} {para}")
    colB.metric("🔻 En Düşük", f"{round(float(data['Close'].min()),2)} {para}")
    colC.metric("📌 Ortalama", f"{round(float(data['Close'].mean()),2)} {para}")
