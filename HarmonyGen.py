import math
import sys
from colorama import just_fix_windows_console

just_fix_windows_console()

def harmgen(count:int,
            phase:int|float,
            amplitude:int|float,
            rate:int,
            frenq:int|float,) -> list[float]:
    if rate <= 0:
        raise ValueError("rate must be positive")
    if count < 0:
        raise ValueError("count must be non-negative")
    if not math.isfinite(phase):
        raise ValueError("phase must be finite")
    if not math.isfinite(frenq) or not 0 <= frenq < rate/2:
        raise ValueError("frequency exceeds Nyquist limit")

    if isinstance(frenq, int):
        freq_num, freq_den = frenq, 1
    else:
        freq_num, freq_den = frenq.as_integer_ratio()

    phase_rad = math.radians(math.remainder(phase, 360))
    cycle_den = rate*freq_den

    signal = [
        amplitude*math.sin(math.remainder(
            math.tau*((freq_num*time)%cycle_den/cycle_den)+phase_rad,
            math.tau
        ))+amplitude
        for time in range(count)
    ]

    return signal


def convsignal(signal:list[float],) -> list[int]:
    return [min(4095, max(0, round(value))) for value in signal]


def parse_number(value:str) -> int|float:
    try:
        return int(value)
    except ValueError:
        return float(value)



COLOR = sys.stdout.isatty()

def style(text:str, code:str) -> str:
    return f"\033[{code}m{text}\033[0m" if COLOR else text


def header(title:str) -> None:
    print()
    print(style("╭" + "─"*48 + "╮", "36"))
    print(style("│" + title.center(48) + "│", "1;36"))
    print(style("╰" + "─"*48 + "╯", "36"))


def success(message:str) -> None:
    print(f"{style('[OK]', '32')} {message}")


def error(message:str) -> None:
    print(f"{style('[ERROR]', '31')} {message}")


def info(message:str) -> None:
    print(f"{style('[INFO]', '36')} {message}")


def read_command(prompt:str) -> list[str]:
    try:
        return input(style(f"{prompt} >>> ", "1;36")).strip().split()
    except EOFError:
        return ["quit"]


# Settings

def show_settings(settings:dict) -> None:
    labels = {
        "count": "Количество отсчётов",
        "phase": "Начальная фаза (°)",
        "amplitude": "Амплитуда",
        "rate": "Частота дискретизации (Гц)",
        "frenq": "Частота сигнала (Гц)"
    }

    header("CURRENT SETTINGS")

    for name, value in settings.items():
        value = "Не задано" if value is None else str(value)
        print(f"  {labels[name]:<34} {value}")

    print()


def settings_menu(settings:dict) -> None:
    while True:
        show_settings(settings)

        info("Введите параметр и значение")
        info("Команды: show | reset | back")

        com = read_command("settings")

        if not com:
            continue

        action = com[0].lower()

        if action in ("back", "menu", "0"):
            return

        elif action == "show":
            continue

        elif action == "reset":
            for name in settings:
                settings[name] = None
            success("Настройки сброшены")
            continue

        elif action in settings:
            if len(com) != 2:
                error(f"Использование: {action} <value>")
                continue

            try:
                if action in ("count", "rate"):
                    value = int(com[1])
                else:
                    value = parse_number(com[1])

                settings[action] = value
                success(f"{action} = {value}")

            except ValueError:
                error("Некорректное значение")

        else:
            error("Неизвестный параметр")


def generate_file(settings:dict, filename:str, mode:str, output_format:str) -> None:
    missing = [name for name, value in settings.items() if value is None]

    if missing:
        error("Не заданы параметры: " + ", ".join(missing))
        return
    if output_format not in ("raw", "conv"):
        error("Формат должен быть raw или conv")
        return

    try:
        signal = harmgen(
            count=settings["count"],
            phase=settings["phase"],
            amplitude=settings["amplitude"],
            rate=settings["rate"],
            frenq=settings["frenq"]
        )

        if output_format == "conv":
            signal = convsignal(signal)

        with open(filename, mode, encoding="utf-8") as file:
            file.write("\n".join(map(str, signal)))

        success(f"Сигнал сохранён: {filename}")
        info(f"Количество отсчётов: {len(signal)}")
        info(f"Формат: {output_format.upper()}")

    except (ValueError, OSError, OverflowError) as exc:
        error(str(exc))


def show_help() -> None:
    header("COMMAND REFERENCE")

    print(style("MAIN MENU", "1;33"))
    print("  settings                  Открыть настройки")
    print("  generate FILE w FORMAT    Создать сигнал")
    print("  construct FILE FORMAT     Конструктор сигнала")
    print("  help                      Справка")
    print("  quit                      Выход")

    print()
    print(style("SETTINGS", "1;33"))
    print("  count 6000                Количество отсчётов")
    print("  phase 45.5                Начальная фаза")
    print("  amplitude 2000            Амплитуда")
    print("  rate 48000                Частота дискретизации")
    print("  frenq 1000                Частота сигнала")
    print("  reset                     Сбросить настройки")
    print("  back                      Вернуться в меню")

    print()
    print(style("OUTPUT FORMATS", "1;33"))
    print("  raw                       Сохранение float")
    print("  conv                      Сохранение int")
    print()



def main() -> int:
    settings = {
        "count": None,
        "phase": None,
        "amplitude": None,
        "rate": None,
        "frenq": None
    }

    header("HARMONIC SIGNAL GENERATOR")
    print(style("  Python signal generation utility", "2"))
    print()

    while True:
        print(style("MAIN MENU", "1;33"))
        print("  [1] settings    Настройки")
        print("  [2] generate    Генерация сигнала")
        print("  [3] help        Справка")
        print("  [0] quit        Выход")

        com = read_command("harmgen")

        if not com:
            continue

        action = com[0].lower()

        if action in ("quit", "exit", "0"):
            print(style("\nQuiting!", "36"))
            return 0
        elif action in ("settings", "1"):
            settings_menu(settings)
        elif action in ("generate", "2"):
            if len(com) == 3:
                filename = com[1]
                mode = "w"
                output_format = com[2]
            elif len(com) == 4:
                filename = com[1]
                mode = com[2]
                output_format = com[3]
            else:
                error("Using: generate FILE w raw|conv")
                continue

            generate_file(settings, filename, mode, output_format)
        elif action in ("help", "3"):
            show_help()
        else:
            error("Unknown command. Enter help.")

if __name__ == "__main__":
    raise SystemExit(main())