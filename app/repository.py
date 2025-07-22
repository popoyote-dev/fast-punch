from dataclasses import dataclass, field
from random import shuffle

from model import Player, Question


@dataclass
class PlayerRepository:
    players: dict[str, Player] = field(default_factory=dict)

    def add_player(self, player: Player) -> bool:
        if self.players.get(player.__hash__()):
            return False

        self.players[player.__hash__()] = player
        return True

    def get_player(self, key: int) -> Player:
        return self.players.get(key)

    def reset(self):
        self.players.clear()

    def players_by_points(self) -> list[Player]:
        return sorted(self.players.values(), key=lambda p: p.total, reverse=True)


@dataclass
class QuizzRepository:
    _qs: list[Question] = field(default_factory=list)

    def add_questions(self, qs: dict):
        for q in qs:
            self._qs.append(Question(**q))

    def get_question(self, index: int) -> Question | None:
        if index is None:
            return None
        return self._qs[index] if index < self.total else None

    @property
    def total(self) -> int:
        return len(self._qs)

    def shoufle(self):
        shuffle(self._qs)

    def reset(self, total: int = 0):
        total = total | self.total
        for i in range(total):
            q = self.get_question(i)
            if q is not None:
                q.reset_answers()

        self.shoufle()

    def clear(self):
        self._qs.clear()
