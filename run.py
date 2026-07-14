from game import parse_game, Gamepad, Printer

with open("tea.ave") as f:
    game = parse_game(f)

gamepad = Gamepad()
printer = Printer()

while True:
    game.reset()
    printer.print_text(" ~ ".join(["AVE"] * 5))
    printer.print_newline()
    printer.print_text(game.title)
    printer.print_newline()
    printer.print_text(f"Written by {game.author}")
    printer.print_newline()
    printer.print_text(" ~ ".join(["AVE"] * 5))
    printer.print_newline()
    printer.print_newline()
    while True:
        if game.room_id == "__GAMEOVER__":
            printer.print_text("GAME OVER")
            printer.print_newline()
            printer.print_newline()
            printer.cut()
            break
        if game.room_id == "__GAMEOVER__":
            printer.print_text("GAME OVER")
            printer.print_newline()
            printer.print_newline()
            printer.cut()
            break

        printer.print_text(game.room_text())
        printer.print_newline()
        for b, o in zip(gamepad.buttons, game.options_text()):
            printer.print_text(f"{b[1]} {o}")
        printer.print_newline()
        printer.print_newline()

        targets = {
            button[0]: target
            for button, target in zip(gamepad.buttons, game.options_targets())
        }
        options = {
            button[0]: target for button, target in zip(gamepad.buttons, game.options())
        }
        while True:
            button = gamepad.get_button_pressed()
            if button in targets:
                game.update_inventory(options[button])
                game.room_id = targets[button]
                break
