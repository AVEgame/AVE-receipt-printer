import hid
from escpos.printer import Usb

buttons = [
    ["SQUARE", "SQUARE  ", lambda x: x[5] & 8 > 0],
    ["X", "X       ", lambda x: x[5] & 4 > 0],
    ["CIRCLE", "CIRCLE  ", lambda x: x[5] & 2 > 0],
    ["TRIANGLE", "TRIANGLE", lambda x: x[5] & 1 > 0],
    ["LEFT", "LEFT    ", lambda x: x[0] == 0],
    ["RIGHT", "RIGHT   ", lambda x: x[0] == 255],
    ["UP", "UP      ", lambda x: x[1] == 0],
    ["DOWN", "DOWN    ", lambda x: x[1] == 255],
    ["L1", "L1      ", lambda x: x[5] & 64 > 0],
    ["L2", "L2      ", lambda x: x[5] & 16 > 0],
    ["R1", "R1      ", lambda x: x[5] & 128 > 0],
    ["R2", "R2      ", lambda x: x[5] & 32 > 0],
    ["START", "START   ", lambda x: x[6] & 8 > 0],
    ["SELECT", "SELECT  ", lambda x: x[6] & 1 > 0],
]


class Game:
    def __init__(self):
        self.title = None
        self.desc = None
        self.authors = None
        self.rooms = {}
        self.items = {}

        self.room_id = None
        self.inventory = None

    def add(self, state, id, data):
        match state:
            case "ROOM":
                self.rooms[id] = data
            case "ITEM":
                self.items[id] = data
            case None:
                pass
            case _:
                raise ValueError(f"Unsupported state: {state}")

    def reset(self):
        self.room_id = "start"
        self.inventory = []

    def satisfies_conditions(self, data):
        for item in data["conditions"]["true"]:
            if item not in self.inventory:
                return False
        for item in data["conditions"]["false"]:
            if item in self.inventory:
                return False
        return True

    def update_inventory(self, data):
        for item in data["inventory"]["add"]:
            assert item not in self.inventory
            self.inventory.append(item)
        for item in data["inventory"]["remove"]:
            assert item in self.inventory
            self.inventory.remove(item)

    def room_text(self):
        parts = []
        for line in self.rooms[self.room_id]["text"]:
            if self.satisfies_conditions(line):
                self.update_inventory(line)
                parts.append(line["text"])
        return " ".join(parts).replace("<newline>", "\n")

    def options(self):
        options = []
        for option in self.rooms[self.room_id]["options"]:
            if self.satisfies_conditions(option):
                options.append(option)
        return options

    def options_text(self):
        return [i["text"] for i in self.options()]

    def options_targets(self):
        return [i["target"] for i in self.options()]


def parse_conditions(text, id="item"):
    bits = text.split()
    pre = []
    while len(bits) > 0:
        if bits[0] in ["+", "~", "?", "?!"]:
            break
        pre.append(bits[0])
        bits = bits[1:]
    out = {
        id: " ".join(pre),
        "inventory": {"add": [], "remove": []},
        "conditions": {"true": [], "false": []},
    }
    for op, id in zip(bits[::2], bits[1::2]):
        if id.startswith("("):
            raise NotImplementedError()
        match op:
            case "?":
                out["conditions"]["true"].append(id)
            case "?!":
                out["conditions"]["false"].append(id)
            case "+":
                out["inventory"]["add"].append(id)
            case "~":
                out["inventory"]["remove"].append(id)
            case _:
                raise NotImplementedError(f"Unsupported operator: {op}")
    return out


def parse_game(file):
    game = Game()
    state = None
    current_id = None
    current = {}

    for line in file:
        line = line.strip()
        if line == "":
            continue
        if "__NUMBER__" in line:
            raise NotImplementedError()

        if line.startswith("==") and line.endswith("=="):
            game.title = line[2:-2].strip()
        elif line.startswith("--") and line.endswith("--"):
            game.desc = line[2:-2].strip()
        elif line.startswith("**") and line.endswith("**"):
            game.authors = line[2:-2].strip()
        elif line.startswith("@@") and line.endswith("@@"):
            pass  # position in library
        elif line.startswith("vv") and line.endswith("vv"):
            pass  # version number
        elif line.startswith("::") and line.endswith("::"):
            pass  # minimum AVE version
        elif line.startswith("~~") and line.endswith("~~"):
            pass  # ~~ off ~~
        elif line.startswith("# "):
            game.add(state, current_id, current)
            state = "ROOM"
            current_id = line[2:].strip()
            current = {"text": [], "options": []}
        elif " => " in line:
            assert state == "ROOM"
            text, next = line.split(" => ")
            current["options"].append(
                {"text": text, **parse_conditions(next, "target")}
            )
        elif line.startswith("% "):
            game.add(state, current_id, current)
            state = "ITEM"
            current_id = line[2:].strip()
            current = {"names": []}
        else:
            if state == "ROOM":
                current["text"].append(parse_conditions(line, "text"))
            elif state == "ITEM":
                current["names"].append(parse_conditions(line, "name"))
            else:
                raise NotImplementedError()
    game.add(state, current_id, current)
    return game


class Gamepad:
    def __init__(self):
        self.buttons = [
            i
            for i in buttons
            if i[0]
            in [
                "SQUARE",
                "X",
                "CIRCLE",
                "TRIANGLE",
                "L1",
                "L2",
                "R1",
                "R2",
            ]
        ]

        self.pad = hid.Device(0x12BD, 0xE002)

    def get_status(self):
        while True:
            report = self.pad.read(64)
            if report:
                return [i[0] for i in self.buttons if i[2](report)]

    def get_button_pressed(self):
        while len(self.get_status()) > 0:
            pass
        while True:
            status = self.get_status()
            if len(status) == 1:
                return status[0]


class Printer:
    def __init__(self):
        self.printer = Usb(0x0483, 0x5743)

    def print_text(self, text):
        self.printer.text("Hello World\n")

    def print_newline(self):
        self.printer.text("\n")

    def cut(self):
        self.printer.cut()
