import math

def harmgen(count:int,
            phase:int|float,
            amplitude:int|float,
            sample_rate:int,
            frenq:int|float,) -> list[float]:

    omega = math.tau*frenq
    phase_rad = math.radians(phase)

    signal = [
        math.fsum((
            amplitude*math.sin(math.fsum((
                omega*time/sample_rate,
                phase_rad
            ))),
            amplitude
        ))
        for time in range(count)
    ]

    return signal

def convsignal(signal:list[float],) -> list[int]:
    return [round(value) for value in signal]

def main():
    settings = {"count": None,
            "phase": None,
            "amplitude": None,
            "sample_rate": None,
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
                if str(com[0]) in settings:
                    settings[str(com[0])] = float(str(com[1])) if str(com[2]) == "float" else int(str(com[1]))
        elif str(com[0]) == "generate":
            with open(str(com[1]), str(com[2]), encoding='utf-8') as file:
                signal = harmgen(count=settings["count"],
                             phase=settings["phase"],
                             amplitude=settings["amplitude"],
                             sample_rate=settings["sample_rate"],
                             frenq=settings["frenq"],)
                if str(com[3]) == "raw":
                    file.write("\n".join(signal))
                elif str(com[3]) == "conv":
                    file.write("\n".join(convsignal(signal)))
            print("Succesful!\n")

if __name__ == "__main__":
    main()