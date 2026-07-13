
class MockPayloadManager:
    """Servo olmadan yük bırakma adımlarını test eder."""

    def __init__(self) -> None:
        self.vehicle = None
        self.payload_1_dropped = False
        self.payload_2_dropped = False

    def set_vehicle(self, vehicle) -> None:
        self.vehicle = vehicle
        logger.info("SIMÜLASYON: Payload sahte vehicle'a bağlandı")

    def reset_servo(self) -> bool:
        logger.info("SIMÜLASYON: Servo nötr komutu verildi")
        return True

    def drop_payload_1(self) -> bool:
        self.payload_1_dropped = True
        logger.info("SIMÜLASYON: MAVİ yük bırakıldı")
        return True

    def drop_payload_2(self) -> bool:
        self.payload_2_dropped = True
        logger.info("SIMÜLASYON: KIRMIZI yük bırakıldı")
        return True

    def get_status(self):
        return {
            "payload_1": (
                "BIRAKILDI"
                if self.payload_1_dropped
                else "HAZIR"
            ),
            "payload_2": (
                "BIRAKILDI"
                if self.payload_2_dropped
                else "HAZIR"
            ),
        }
