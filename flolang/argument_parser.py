class ArgumentParser:
    def __init__(self, argv, toggles: list[str] = [], keys: list[str] = []):
        switches, keyvalues, args = self.parse(argv[1:], toggles, keys)
        self._switches = switches
        self._keyvalues = keyvalues
        self._arguments = args

    def parse(self, argv, toggles: list[str], keys: list[str]) -> tuple[list[str], dict[str, str], list[str]]:
        switches: list[str] = []
        keyvalues: dict[str, str] = {}
        args: list[str] = []

        while len(argv) > 0:
            arg = argv[0]
            if arg.startswith("--"):
                stripped = arg[2:]
                if stripped in toggles:
                    switches.append(stripped)
                    argv = argv[1:]  # consume this arg
                elif stripped in keys:
                    keyvalues[stripped] = argv[1]
                    argv = argv[2:]  # consume this 2 args
                else:
                    raise ValueError(f"Encountered unknown switch or key: {arg}")
            elif arg.startswith("-"):
                for char in arg[1:]:
                    if char in toggles:
                        switches.append(char)
                argv = argv[1:]  # consume this arg
            else:
                args.append(arg)
                argv = argv[1:]  # consume this arg

        return switches, keyvalues, args

    def switch(self, switch: str) -> bool:
        if switch in self._switches:
            return True
        s = switch[0]
        return s in self._switches

    def switches(self) -> list[str]:
        return self._switches

    def key(self, key: str) -> str | None:
        if key in self._keyvalues:
            return self._keyvalues[key]
        return None

    def keyvalues(self) -> dict[str, str]:
        return self._keyvalues

    def args(self) -> list[str]:
        return self._arguments
