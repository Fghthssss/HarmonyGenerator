import math

import math

def harmgen(count:int,
            phase:int|float,
            amplitude:int|float,
            rate:int,
            frenq:int|float,) -> list[float]:
    if rate <= 0:
        raise ValueError("rate must be positive")
    if count < 0:
        raise ValueError("count must be non-negative")
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
    return [round(value) for value in signal]

def parse_number(value:str) -> int|float:
    try:
        return int(value)
    except ValueError:
        return float(value)

def main():
    settings = {"count": None,
            "phase": None,
            "amplitude": None,
            "rate": None,
            "frenq": None,}

    url = "menu"
    com = "menu"

    while str(com[0]) != "quit":
        url = "menu"
        com = input(f"{url}: ").split()
        if str(com[0]) == "settings":
            url = "settings"
            while str(com[0]) != "menu":
                print("\nSettings:")
                print("\n".join([f"{name}: {settings[name]}" for name in settings]) + "\n")
                com = input(f"{url}: ").split()
                if str(com[0]) in ("count", "rate"):
                    settings[str(com[0])] = int(com[1])
                else:
                    settings[str(com[0])] = parse_number(com[1])
        elif str(com[0]) == "generate":
            if any(value is None for value in settings.values()):
                print("Error: settings are incomplete!")
                continue
            with open(str(com[1]), str(com[2]), encoding='utf-8') as file:
                signal = harmgen(count=settings["count"],
                             phase=settings["phase"],
                             amplitude=settings["amplitude"],
                             rate=settings["rate"],
                             frenq=settings["frenq"],)
                if str(com[3]) == "raw":
                    file.write("\n".join(map(str, signal)))
                elif str(com[3]) == "conv":
                    file.write("\n".join(map(str, convsignal(signal))))
            print("Succesful!\n")

if __name__ == "__main__":
    main()