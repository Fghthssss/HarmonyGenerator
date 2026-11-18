
import math
import sys
from colorama import just_fix_windows_console

just_fix_windows_console()

REQUIRED = ("count", "phase", "amplitude", "rate", "frenq")

LABELS = {
    "count": "count: Количество отсчётов",
    "phase": "phase: Начальная фаза (°)",
    "amplitude": "amplitude: Амплитуда",
    "rate": "rate: Частота дискретизации (Гц)",
    "frenq": "frenq: Частота сигнала (Гц)"
}

COLOR = sys.stdout.isatty()


def harmgen(count:int,
            phase:int|float,
            amplitude:int|float,
            rate:int,
            frenq:int|float) -> list[float]:

    if rate <= 0:
        raise ValueError("rate must be positive")
    if count < 0:
        raise ValueError("count must be non-negative")
    if not math.isfinite(phase):
        raise ValueError("phase must be finite")
    if not math.isfinite(amplitude):
        raise ValueError("amplitude must be finite")
    if not math.isfinite(frenq) or not 0 <= frenq < rate/2:
        raise ValueError("frequency exceeds Nyquist limit")

    if isinstance(frenq, int):
        freq_num, freq_den = frenq, 1
    else:
        freq_num, freq_den = frenq.as_integer_ratio()

    phase_rad = math.radians(math.remainder(phase, 360))
    cycle_den = rate * freq_den

    return [
        amplitude * math.sin(math.remainder(
            math.tau * ((freq_num * time) % cycle_den / cycle_den) + phase_rad,
            math.tau
        )) + amplitude
        for time in range(count)
    ]


def convsignal(signal:list[float]) -> list[int]:
    return [min(4095, max(0, round(value))) for value in signal]


def parse_number(value:str) -> int|float:
    try:
        return int(value)
    except ValueError:
        return float(value)


def check_settings(settings:dict) -> list[str]:
    return [key for key in REQUIRED if settings.get(key) is None]


def style(text:str, code:str) -> str:
    return f"\033[{code}m{text}\033[0m" if COLOR else text


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def header(title:str) -> None:
    print()
    print(style("╭" + "─"*48 + "╮", "36"))
    print(style("│" + title.center(48) + "│", "1;36"))
    print(style("╰" + "─"*48 + "╯", "36"))


def draw_screen(title:str, content:list[str] = None) -> None:
    clear_screen()
    header(title)

    for line in content or []:
        print(line)


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


def show_settings(settings:dict) -> None:
    content = [
        f"  {LABELS[name]:<34} "
        f"{'Не задано' if value is None else value}"
        for name, value in settings.items()
    ]

    draw_screen("CURRENT SETTINGS", content)


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
            settings.update(dict.fromkeys(settings))
            success("Настройки сброшены")

        elif action in settings:
            if len(com) != 2:
                error(f"Использование: {action} <value>")
                continue

            try:
                value = int(com[1]) if action in ("count", "rate") else parse_number(com[1])
                settings[action] = value
                success(f"{action} = {value}")

            except ValueError:
                error("Некорректное значение")

        else:
            error("Неизвестный параметр")


def generate_file(settings:dict,
                  filename:str,
                  mode:str,
                  output_format:str) -> None:

    missing = check_settings(settings)

    if missing:
        error("Не заданы параметры: " + ", ".join(missing))
        return

    if output_format not in ("raw", "conv"):
        error("Формат должен быть raw или conv")
        return

    if mode not in ("w", "a"):
        error("Режим должен быть w или a")
        return

    try:
        signal = harmgen(**settings)

        if output_format == "conv":
            signal = convsignal(signal)

        with open(filename, mode, encoding="utf-8") as file:
            file.write("\n".join(map(str, signal)) + "\n")

        success(f"Сигнал сохранён: {filename}")
        info(f"Количество отсчётов: {len(signal)}")
        info(f"Формат: {output_format.upper()}")

    except (ValueError, OSError, OverflowError) as exc:
        error(str(exc))


def show_help() -> None:
    content = [
        style("MAIN MENU", "1;33"),
        "  settings                  Открыть настройки",
        "  generate FILE w|a FORMAT  Создать сигнал",
        "  construct                 Конструктор сигналов",
        "  help                      Справка",
        "  quit                      Выход",
        "",
        style("SETTINGS", "1;33"),
        "  count 6000                Количество отсчётов",
        "  phase 45.5                Начальная фаза",
        "  amplitude 2000            Амплитуда",
        "  rate 48000                Частота дискретизации",
        "  frenq 1000                Частота сигнала",
        "  reset                     Сбросить настройки",
        "  back                      Вернуться в меню",
        "",
        style("CONSTRUCTOR", "1;33"),
        "  add count=500 freq=440    Добавить участок",
        "  add amplitude=1500        Изменить амплитуду участка",
        "  list                      Список участков",
        "  remove 1                  Удалить участок",
        "  clear                     Очистить конструкцию",
        "  build FILE w|a FORMAT       Собрать сигнал",
        "  back                      Выйти из конструктора",
        "",
        style("OUTPUT FORMATS", "1;33"),
        "  raw                       Сохранение float",
        "  conv                      Сохранение int"
    ]

    draw_screen("COMMAND REFERENCE", content)
    input("Нажмите Enter для возврата...")


def parse_arguments(arguments:list[str]) -> dict:
    result = {}

    for argument in arguments:
        key, separator, value = argument.partition("=")

        if not separator or not key or not value:
            raise ValueError(f"Некорректный аргумент: {argument}")

        if key not in ("count", "amplitude", "frenq", "freq"):
            raise ValueError(f"Недопустимый параметр участка: {key}")

        if key == "freq":
            key = "frenq"

        result[key] = parse_number(value)

    return result


def construct_menu(settings:dict) -> None:
    construction = []
    base_settings = settings.copy()

    while True:
        content = [
            "Команды: add | list | remove | clear | build | back",
            "",
            "Участки:"
        ]

        if construction:
            content.extend(
                f"  #{index} | N={segment['count']} | "
                f"F={segment['frenq']} Hz | A={segment['amplitude']}"
                for index, segment in enumerate(construction, 1)
            )
        else:
            content.append("  Список пуст")

        draw_screen("SIGNAL CONSTRUCTOR", content)

        com = read_command("construct")

        if not com:
            continue

        action = com[0].lower()

        if action in ("back", "exit"):
            return

        elif action == "add":
            try:
                segment = base_settings.copy()
                segment.update(parse_arguments(com[1:]))

                missing = check_settings(segment)

                if missing:
                    error("Не заданы параметры: " + ", ".join(missing))
                    continue

                harmgen(**segment)

                construction.append(segment)
                success(f"Участок #{len(construction)} добавлен")

            except (ValueError, OverflowError) as exc:
                error(str(exc))

        elif action == "list":
            continue

        elif action == "remove":
            if len(com) != 2 or not com[1].isdigit():
                error("Использование: remove <номер>")
                continue

            index = int(com[1]) - 1

            if 0 <= index < len(construction):
                construction.pop(index)
                success("Участок удалён")
            else:
                error("Участок не найден")

        elif action == "clear":
            construction.clear()
            success("Конструкция очищена")

        elif action == "build":
            if len(com) != 4:
                error("Использование: build FILENAME w|a raw|conv")
                continue

            filename = com[1]
            mode = com[2].lower()
            output_format = com[3].lower()

            if mode not in ("w", "a"):
                error("Режим должен быть w или a")
                continue

            if output_format not in ("raw", "conv"):
                error("Формат должен быть raw или conv")
                continue

            if not construction:
                error("Нет участков для сборки")
                continue

            try:
                signal = []
                current_phase = construction[0]["phase"]

                for segment in construction:
                    part = harmgen(
                        count=segment["count"],
                        phase=current_phase,
                        amplitude=segment["amplitude"],
                        rate=segment["rate"],
                        frenq=segment["frenq"]
                    )

                    signal.extend(part)

                    current_phase = math.degrees(math.remainder(
                        math.radians(current_phase) +
                        math.tau * segment["frenq"] *
                        segment["count"] / segment["rate"],
                        math.tau
                    ))

                if output_format == "conv":
                    signal = convsignal(signal)

                with open(filename, mode, encoding="utf-8") as file:
                    file.write("\n".join(map(str, signal)) + "\n")

                success(f"Сигнал сохранён: {filename}")
                info(f"Участков: {len(construction)}")
                info(f"Всего отсчётов: {len(signal)}")
                info(f"Формат: {output_format.upper()}")
                info(f"Режим: {mode}")

            except (ValueError, OSError, OverflowError) as exc:
                error(str(exc))

        else:
            error("Неизвестная команда. Введите help.")


def main() -> int:
    settings = dict.fromkeys(REQUIRED)

    while True:
        content = [
            style("Signal generation utility, by: ocidn; fghthssss; paradigma", "2"),
            "",
            style("MAIN MENU", "1;33"),
            "  [1] settings    Настройки",
            "  [2] generate    Генерация сигнала",
            "  [3] construct   Конструктор сигналов",
            "  [4] help        Справка",
            "  [0] quit        Выход"
        ]

        draw_screen("HARMONIC SIGNAL GENERATOR", content)

        com = read_command("harmgen")

        if not com:
            continue

        action = com[0].lower()

        if action in ("quit", "exit", "0"):
            print(style("\nQuitting!", "36"))
            return 0

        elif action in ("settings", "1"):
            settings_menu(settings)

        elif action in ("generate", "2"):
            if len(com) == 3:
                filename, output_format = com[1], com[2]
                mode = "w"

            elif len(com) == 4:
                filename, mode, output_format = com[1:]

            else:
                error("Использование: generate FILE w|a raw|conv")
                input("Нажмите Enter...")
                continue

            generate_file(settings, filename, mode, output_format)
            input("Нажмите Enter для продолжения...")

        elif action in ("construct", "3"):
            construct_menu(settings)

        elif action in ("help", "4"):
            show_help()

        else:
            error("Unknown command. Enter help.")
            input("Нажмите Enter...")


if __name__ == "__main__":
    raise SystemExit(main())
