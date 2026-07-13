# -*- coding: utf-8 -*-
"""
Kamera + Görüntü İşleme Testi
Kameradan kare alır, mavi/kırmızı bölgeleri tespit eder,
sonuçları konsola yazdırır ve debug görüntüsünü kaydeder.
"""

import sys
import os
import time

# Proje dizinine config erişimi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
from vision import VisionProcessor

def test_camera():
    print("=" * 60)
    print("KAMERA + GÖRÜNTÜ İŞLEME TESTİ")
    print("=" * 60)

    vp = VisionProcessor()

    # Kamera başlat
    print("\n[1] Kamera başlatılıyor...")
    if not vp.start_camera():
        print("  ✗ Kamera açılamadı!")
        print("  → Bağlı kameraları kontrol edin:")
        os.system("ls -la /dev/video* 2>/dev/null || echo '  Hiç video cihazı bulunamadı'")
        print("\n  Sentetik test görüntüsü ile devam ediliyor...\n")
        use_synthetic = True
    else:
        print(f"  ✓ Kamera açıldı")
        use_synthetic = False

    # 5 kare yakala ve işle
    print("\n[2] Görüntü yakalama ve tespit başlıyor...\n")

    os.makedirs("debug_images", exist_ok=True)

    for i in range(5):
        print(f"--- Kare {i+1}/5 ---")

        if use_synthetic:
            # Sentetik test görüntüsü (mavi ve kırmızı dikdörtgenler)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = (60, 60, 60)  # Gri arka plan
            cv2.rectangle(frame, (100, 80), (280, 260), (255, 120, 0), -1)   # Mavi kare
            cv2.rectangle(frame, (400, 280), (500, 380), (0, 0, 230), -1)    # Kırmızı kare
            # Biraz gürültü ekle (gerçekçilik için)
            noise = np.random.randint(0, 20, frame.shape, dtype=np.uint8)
            frame = cv2.add(frame, noise)
        else:
            frame = vp.capture_frame()
            if frame is None:
                print("  ✗ Kare okunamadı, atlanıyor...")
                continue
            # İlk kareyi kamera ısınsın diye bekle
            if i == 0:
                time.sleep(0.5)
                frame = vp.capture_frame()

        print(f"  Görüntü boyutu: {frame.shape[1]}x{frame.shape[0]}")

        # Tespit yap
        detections = vp.detect_all(frame)

        # Mavi tespitler
        print(f"\n  MAVİ tespitler: {len(detections['blue'])} adet")
        for j, d in enumerate(detections['blue']):
            print(f"    [{j+1}] Merkez: ({d.center_pixel[0]}, {d.center_pixel[1]})")
            print(f"        Alan: {d.area:.0f} piksel²")
            print(f"        En-boy oranı: {d.aspect_ratio:.2f}")
            print(f"        Dikdörtgensellik: {d.rectangularity:.2f}")
            print(f"        Köşe sayısı: {d.corners}")
            print(f"        Güven skoru: {d.confidence:.1f}%")

        # Kırmızı tespitler
        print(f"\n  KIRMIZI tespitler: {len(detections['red'])} adet")
        for j, d in enumerate(detections['red']):
            print(f"    [{j+1}] Merkez: ({d.center_pixel[0]}, {d.center_pixel[1]})")
            print(f"        Alan: {d.area:.0f} piksel²")
            print(f"        En-boy oranı: {d.aspect_ratio:.2f}")
            print(f"        Dikdörtgensellik: {d.rectangularity:.2f}")
            print(f"        Köşe sayısı: {d.corners}")
            print(f"        Güven skoru: {d.confidence:.1f}%")

        # Debug görüntüsü kaydet
        annotated = vp.draw_detections(frame, detections)
        filename = f"debug_images/test_frame_{i+1}.jpg"
        cv2.imwrite(filename, annotated)
        print(f"\n  → Görüntü kaydedildi: {filename}")

        if not use_synthetic:
            time.sleep(0.3)

        print()

    # Temizlik
    vp.stop_camera()

    print("=" * 60)
    print("TEST TAMAMLANDI")
    print("=" * 60)
    print(f"\nDebug görüntüleri: {os.path.abspath('debug_images/')}")
    print("Görüntüleri incelemek için bu dizine bakın.")

if __name__ == "__main__":
    test_camera()
