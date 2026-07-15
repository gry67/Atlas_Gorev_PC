# -*- coding: utf-8 -*-
"""
Teknofest Uluslararası İHA Yarışması - Ana Görev Kontrolcüsü
===============================================================
State machine (durum makinesi) tabanlı otonom görev yönetimi.

Görev Akışı:
  INIT → TAKEOFF → SEARCH → PROCESS → NAVIGATE_BLUE → DROP_BLUE
  → NAVIGATE_RED → DROP_RED → RTL → COMPLETE

Kullanım:
  python3 main.py [--sitl] [--no-camera]

Orange Cube+ (ArduPilot) uyumlu.
"""
import numpy as np
import os
import sys
import time
import signal
import argparse
import math
from typing import Optional, Tuple, List

import config
from config import MissionState
from logger_config import setup_logger
from vision import VisionProcessor, DetectionResult
from coordinate_transform import CoordinateTransformer
from NavigationManager import NavigationManager
from PayloadManager import PayloadManager
from  MissionController import MissionController




# =============================================================================
# ANA GİRİŞ NOKTASI
# =============================================================================
def main():
    """Ana fonksiyon - komut satırı argümanlarını işler ve görevi başlatır."""

    parser = argparse.ArgumentParser(
        description="Teknofest İHA Otonom Görev Sistemi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python3 main.py                    # Gerçek uçuş (Orange Cube+ + Kamera)
  python3 main.py --sitl             # SITL simülatörü ile test
  python3 main.py --sitl --no-camera # SITL + kamerasız test
        """
    )

    parser.add_argument(
        '--sitl',
        action='store_true',
        help='SITL simülatörü kullan (test amaçlı)'
    )
    parser.add_argument(
        '--no-camera',
        action='store_true',
        help='Kamera kullanma (test amaçlı)'
    )
    parser.add_argument(
        '--connection',
        type=str,
        default=None,
        help='Özel MAVLink bağlantı stringi'
    )

    args = parser.parse_args()

    # Bağlantı stringi override
    if args.connection:
        config.CONNECTION_STRING = args.connection

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     TEKNOFEST ULUSLARARASI İHA YARIŞMASI               ║")
    print("║     Otonom Görev Sistemi v1.0                           ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print(f"║  Mod: {'SITL Simülasyon' if args.sitl else 'GERÇEK UÇUŞ':42s}  ║")
    print(f"║  Kamera: {'Kapalı' if args.no_camera else 'Açık':40s}  ║")
    print(f"║  Bağlantı: {config.SITL_CONNECTION if args.sitl else config.CONNECTION_STRING:38s}  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # Görev kontrolcüsünü oluştur ve başlat
    controller = MissionController(
        use_sitl=args.sitl,
        use_camera=not args.no_camera
    )

    controller.run()


if __name__ == "__main__":
    main()
