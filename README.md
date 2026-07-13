# Teknofest Uluslararası İHA Yarışması - Otonom Görev Sistemi

## 📋 Genel Bakış

Bu sistem, Teknofest Uluslararası İHA Yarışması için geliştirilmiş otonom görev yazılımıdır. **Orange Cube+** uçuş kontrolcüsü ile MAVLink/DroneKit üzerinden haberleşerek:

1. **Görüntü İşleme** ile mavi (4x4) ve kırmızı (2x2) bölgeleri tespit eder
2. Tespit edilen bölgelerin **GPS koordinatlarını** hesaplar
3. Mission Planner uyumlu **waypoint/misyon** oluşturur
4. Önce mavi, sonra kırmızı bölgeye uçup **faydalı yük bırakır**

## 🏗️ Proje Yapısı

```
teknofest_iha/
├── config.py              # Tüm konfigürasyon parametreleri
├── main.py                # Ana görev kontrolcüsü (state machine)
├── vision.py              # Görüntü işleme (mavi/kırmızı tespit)
├── coordinate_transform.py # Piksel → GPS dönüşümü
├── navigation.py          # MAVLink navigasyon yönetimi
├── payload.py             # Servo ile yük bırakma
├── logger_config.py       # Loglama yapılandırması
├── requirements.txt       # Python bağımlılıkları
├── logs/                  # Log dosyaları (otomatik oluşur)
└── debug_images/          # Debug görüntüleri (otomatik oluşur)
```

## ⚙️ Kurulum

### 1. Python Bağımlılıkları
```bash
pip install -r requirements.txt
```

### 2. Orange Cube+ Ayarları (Mission Planner)
- **Servo Kanalı:** `SERVO9_FUNCTION = 0` (GPIO modu - AUX1)
- **Baud Rate:** 57600
- **MAVLink Protokolü:** MAVLink 2

### 3. Kamera Kalibrasyonu (Opsiyonel ama Önerilen)
```bash
# OpenCV kamera kalibrasyonu yapın ve sonuçları config.py'ye girin:
# CAMERA_MATRIX ve CAMERA_DIST_COEFFS değerlerini güncelleyin
```

## 🚀 Kullanım

### Gerçek Uçuş
```bash
python3 main.py
```

### SITL Simülasyon Testi
```bash
# 1. SITL simülatörünü başlatın (ayrı terminal):
sim_vehicle.py -v ArduPlane --console --map

# 2. Görev yazılımını başlatın:
python3 main.py --sitl
```

### Test Modları
```bash
# SITL + kamerasız test:
python3 main.py --sitl --no-camera

# Özel bağlantı stringi ile:
python3 main.py --connection tcp:192.168.1.100:5760
```

### Modül Testleri
```bash
# Görüntü işleme testi:
python3 vision.py

# Koordinat dönüşüm testi:
python3 coordinate_transform.py

# Payload (servo) testi:
python3 payload.py
```

## 📊 Görev Akışı

```
INIT → TAKEOFF → SEARCH → PROCESS → NAVIGATE_BLUE → DROP_BLUE → NAVIGATE_RED → DROP_RED → RTL → COMPLETE
```

| Durum | Açıklama |
|-------|----------|
| `INIT` | Sistem başlatma, bağlantı kontrolü, GPS fix bekleme |
| `TAKEOFF` | Kalkış, arama rotası yükleme |
| `SEARCH` | Seyir uçuşu + görüntü işleme ile hedef arama |
| `PROCESS` | Tespitleri değerlendirme, GPS ortalaması, misyon oluşturma |
| `NAVIGATE_BLUE` | Mavi bölgeye otonom uçuş |
| `DROP_BLUE` | Servo → 1100µs → Yük 1 bırakma |
| `NAVIGATE_RED` | Kırmızı bölgeye otonom uçuş |
| `DROP_RED` | Servo → 1900µs → Yük 2 bırakma |
| `RTL` | Eve dönüş |
| `COMPLETE` | Görev tamamlandı |

## 🎯 Görüntü İşleme Detayları

### Renk Tespiti (HSV)
- **Mavi:** H(100-130), S(80-255), V(50-255)
- **Kırmızı:** H(0-10) + H(170-179), S(80-255), V(50-255)

### Şekil Doğrulaması
- Kontur analizi ile dikdörtgen/kare tespiti
- En-boy oranı kontrolü (0.6 - 1.4)
- Dikdörtgensellik skoru (min %70)
- Köşe sayısı kontrolü (3-6 arası)
- Güven skoru hesaplama (min %60)

### Piksel → GPS Dönüşümü
1. Piksel → Kamera koordinatları (intrinsic matris)
2. Kamera → NED çerçevesi (roll/pitch/yaw rotasyonu)
3. NED → GPS (irtifa projeksiyonu + Haversine)

## 🔧 Konfigürasyon

Tüm ayarlar `config.py` dosyasından yapılır:

### Önemli Parametreler
| Parametre | Varsayılan | Açıklama |
|-----------|-----------|----------|
| `CONNECTION_STRING` | `/dev/ttyACM0` | MAVLink bağlantısı |
| `SERVO_CHANNEL` | 9 (AUX1) | Servo kanalı |
| `SERVO_PAYLOAD_1_PWM` | 1100 | Yük 1 bırakma PWM |
| `SERVO_PAYLOAD_2_PWM` | 1900 | Yük 2 bırakma PWM |
| `SEARCH_ALTITUDE` | 50m | Arama yüksekliği |
| `DROP_ALTITUDE` | 30m | Yük bırakma yüksekliği |
| `WAYPOINT_REACHED_RADIUS` | 10m | Waypoint varış yarıçapı |

### HSV Renk Ayarı
Farklı ışık koşullarında HSV değerlerini ayarlamak için:
```python
# config.py içinde:
BLUE_HSV_LOWER = np.array([100, 80, 50])
BLUE_HSV_UPPER = np.array([130, 255, 255])
```

## ⚠️ Güvenlik

- **Batarya Failsafe:** Voltaj 10.5V altına düşerse otomatik RTL
- **Görev Süresi:** 10 dakikayı aşarsa otomatik RTL
- **GPS Fix:** Minimum 3D fix gerekli
- **CTRL+C:** Güvenli kapatma (servo nötre, bağlantı kapat)

## 📝 Notlar

1. **Kamera Kalibrasyonu** piksel→GPS dönüşüm doğruluğunu önemli ölçüde etkiler
2. **HSV değerleri** yarışma alanının ışık koşullarına göre ayarlanmalıdır
3. `config.py`'daki **GPS koordinatları** yarışma alanına göre güncellenmelidir
4. İlk testleri mutlaka **SITL simülatöründe** yapın
5. Gerçek uçuş öncesi **servo çalışma yönlerini** doğrulayın
