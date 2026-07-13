import pytest
from game import parse_game

with open("tea.ave") as f:
    game = parse_game(f)


@pytest.mark.parametrize("id", game.rooms.keys())
def test_number_of_options(id):
    assert len(game.rooms[id]["options"]) <= 8


def test_kettle_room():
    with open("tea.ave") as f:
        game = parse_game(f)
    game.reset()
    game.room_id = "kettle"

    for line in game.rooms["kettle"]["text"]:
        print(line)
    assert game.room_text() == "The kettle doesn't turn on."

    game.inventory.append("kettleplug")

    assert (
        game.room_text()
        == "The kettle explodes in a shower of sparks. How could you forget that your kettle is broken? That's why you left it unplugged. The sparks prove fatal."
    )
