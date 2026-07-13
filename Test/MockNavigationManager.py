


logger = setup_logger("hardware_test")

class MockNavigationManager:
    """Cube olmadan görev akışını test etmek için sahte uçuş kontrolcüsü."""

    def __init__(self) -> None:
        self.vehicle = object()
        self.is_connected = False

        self._altitude = 0.0
        self._distance = 120.0
        self._mode = "STANDBY"

    def connect(self, _connection_string: str) -> bool:
        self.is_connected = True
        logger.info("SIMÜLASYON: Sahte Cube bağlantısı kuruldu")
        return True

    def disconnect(self) -> None:
        self.is_connected = False
        logger.info("SIMÜLASYON: Sahte Cube bağlantısı kapatıldı")

    def get_gps_fix(self):
        return 3

    def get_battery(self):
        return {
            "voltage": 16.2,
            "level": 92,
        }

    def get_location(self):
        # AUTO modunda kalkışı simüle et.
        if self._mode == "AUTO" and self._altitude < config.SEARCH_ALTITUDE:
            self._altitude = min(
                config.SEARCH_ALTITUDE,
                self._altitude + 2.5,
            )

        # RTL modunda inişi simüle et.
        elif self._mode == "RTL" and self._altitude > 0.0:
            self._altitude = max(
                0.0,
                self._altitude - 5.0,
            )

        return (
            config.SEARCH_AREA_CENTER_LAT,
            config.SEARCH_AREA_CENTER_LON,
            self._altitude,
        )

    def get_attitude(self):
        # roll, pitch, yaw (radyan)
        return 0.0, 0.0, 0.0

    def generate_search_pattern(
        self,
        center_lat: float,
        center_lon: float,
        length: float,
        width: float,
        spacing: float,
    ) -> List[Tuple[float, float]]:
        logger.info(
            "SIMÜLASYON: Arama paterni oluşturuldu "
            f"(merkez={center_lat:.6f},{center_lon:.6f})"
        )

        return [
            (center_lat, center_lon),
            (center_lat + 0.0001, center_lon),
            (center_lat + 0.0001, center_lon + 0.0001),
            (center_lat, center_lon + 0.0001),
        ]

    def create_search_mission(self, _waypoints) -> bool:
        logger.info("SIMÜLASYON: Arama misyonu yüklendi")
        return True

    def create_mission(
        self,
        blue_targets,
        red_targets,
    ) -> bool:
        self._distance = 40.0

        logger.info(
            "SIMÜLASYON: Yük bırakma misyonu oluşturuldu "
            f"(mavi={blue_targets}, kırmızı={red_targets})"
        )
        return True

    def arm(self) -> bool:
        logger.info("SIMÜLASYON: İHA ARM edildi")
        return True

    def set_mode(self, mode: str) -> bool:
        self._mode = mode

        # Her hedef navigasyonunun başlayabilmesi için mesafeyi yenile.
        if mode == "AUTO" and self._distance <= 0.0:
            self._distance = 40.0

        logger.info(f"SIMÜLASYON: Uçuş modu {mode}")
        return True

    def get_distance_to(
        self,
        target_lat: float,
        target_lon: float,
    ) -> float:
        # RTL sırasında home noktasına zaten ulaşılmış kabul edilir.
        if self._mode == "RTL":
            return 0.0

        # Normal hedef uçuşunda her çağrıda yaklaş.
        if self._distance > 0.0:
            self._distance = max(
                0.0,
                self._distance - 4.0,
            )

        return self._distance

    def check_battery_failsafe(self) -> bool:
        """Simülasyonda batarya failsafe oluşmadığını belirtir."""
        return False

    def emergency_rtl(self) -> bool:
        logger.warning("SIMÜLASYON: Acil RTL çağrıldı")
        self._mode = "RTL"
        return True
