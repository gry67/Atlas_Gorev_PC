# -*- coding: utf-8 -*-
"""
Donanımsız ana görev testi
=========================

Kamera gerçek çalışır.
Cube, GPS, uçuş hareketi ve servo simüle edilir.

Kullanım:
    python main_test.py
"""

from typing import List, Tuple

import config
from logger_config import setup_logger
from main import MissionController
from Test.MockNavigationManager import * 
from Test.MockPayloadManager import *

def main() -> None:
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       DONANIMSIZ GÖREV TESTİ                            ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  Kamera      : GERÇEK                                   ║")
    print("║  Cube / GPS  : SİMÜLASYON                               ║")
    print("║  Servo       : SİMÜLASYON                               ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    controller = MissionController(
        use_sitl=False,
        use_camera=True,
    )

    # Gerçek donanım modüllerini sahte modüllerle değiştir.
    controller.navigation = MockNavigationManager()
    controller.payload = MockPayloadManager()

    # Her renk için 3 başarılı tespit yeterli.
    controller._detection_threshold = 3

    controller.run()


if __name__ == "__main__":
    main()
