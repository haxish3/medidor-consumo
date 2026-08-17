from datetime import datetime
from pathlib import Path
from time import monotonic, sleep

import clr

from .database import get_daily_totals, get_day_totals, initialize_db, save_sample

EXTRA_POWER_W = 50
PRICE_PER_KWH_BRL = 0.82

TARGET = ["CPU Package", "GPU Package"]


def main() -> None:

    root = Path(__file__).resolve().parents[2]
    lib_path = root / "lib" / "LibreHardwareMonitorLib.dll"
    db_path = root / "data" / "consum.db"

    if not lib_path.exists():
        raise FileNotFoundError(
            f"O arquivo DLL não foi encontrado no caminho: {lib_path}"
        )

    clr.AddReference(str(lib_path))

    from LibreHardwareMonitor.Hardware import Computer, SensorType

    computer = Computer()
    computer.IsCpuEnabled = True
    computer.IsGpuEnabled = True
    computer.Open()

    try:
        last_sample_time = monotonic()
        session_kwh = 0.0

        today = datetime.now().astimezone().date().isoformat()

        initialize_db(db_path)
        saved_kwh, saved_cost_brl = get_day_totals(db_path, today)
        print(get_daily_totals(db_path))

        while True:
            sensor_totals = {}
            for hardware in computer.Hardware:
                hardware.Update()

                for sensor in hardware.Sensors:
                    if sensor.SensorType == SensorType.Power and sensor.Name in TARGET:
                        sensor_totals[sensor.Name] = sensor.Value

            now = monotonic()
            elapsed = now - last_sample_time
            recorded_at = datetime.now().astimezone().isoformat()
            last_sample_time = now

            cpu = sensor_totals["CPU Package"]
            gpu = sensor_totals["GPU Package"]
            total = sum(sensor_totals.values()) + EXTRA_POWER_W

            interval_kwh = total * elapsed / 3_600_000
            session_kwh += interval_kwh
            interval_cost_brl = interval_kwh * PRICE_PER_KWH_BRL
            session_cost_brl = session_kwh * PRICE_PER_KWH_BRL

            save_sample(
                db_path, recorded_at, cpu, gpu, total, interval_kwh, interval_cost_brl
            )

            print(
                f"\r\x1b[KCPU Power:  {cpu:>6.2f} W\n"
                f"\r\x1b[KGPU Power:  {gpu:>6.2f} W\n"
                f"\r\x1b[KTotal:      {total:>6.2f} W\n\n"
                f"\r\x1b[KEnergy:     {session_kwh + saved_kwh:>6.6f} kWh\n"
                f"\r\x1b[KCost:    R$ {session_cost_brl + saved_cost_brl:>6.6f}\n"
                "\x1b[6A",
                end="",
                flush=True,
            )

            sleep(2.5)
    except KeyboardInterrupt:
        print("\rProgram stopped by user.")
    finally:
        computer.Close()
