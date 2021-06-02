from __future__ import annotations
from logging import DEBUG, INFO, getLogger

from world import Room

logger = getLogger(__name__)
logger.setLevel(INFO)


class Solver:
    def __init__(self, rooms: list[Room], init_temp: float, **kwargs) -> None:
        self.rooms = rooms
        self.init_temp = init_temp
        self.subs_cnt = 0
        self.max_p_diff_in_rooms: int = kwargs.get(
            "max_p_diff_in_rooms") or 1e2
        logger.info("max_p_diff_in_rooms: {}".format(self.max_p_diff_in_rooms))

        self.max_iter: int = kwargs.get("max_iter") or 100
        logger.info("max_iter: {}".format(self.max_iter))

        self.delta_n_in_adjust: float = kwargs.get("delta_n_in_adjust") or 1e-2
        logger.info("delta_n_in_adjust: {}".format(self.delta_n_in_adjust))

        for r in rooms:
            self.subs_cnt += len(r.substances)
        logger.info("{} substances".format(self.subs_cnt))

    @property
    def is_same_p(self) -> bool:
        same_p = True
        for r in self.rooms:
            same_p = same_p and abs(
                r.p - self.p_avg) < self.max_p_diff_in_rooms / 2
            logger.debug("diff in p: {}".format(r.p - self.p_avg))
        return same_p

    @property
    def p_avg(self) -> float:
        return sum([r.p for r in self.rooms]) / len(self.rooms)

    def adjust_p(self) -> list[Room]:
        i = 0
        while i < self.max_iter:
            R = 8.314510e3
            delta_v = 0.5 * self.rooms[0].mol_gas * R * \
                self.rooms[0].T * abs(1/self.p_avg - 1/self.rooms[0].p)
            abs_total_p_diff = sum([abs(r.p - self.p_avg) for r in self.rooms])

            changed = True
            for r in self.rooms:
                sign = 1 if r.p > self.p_avg else -1
                changed = changed and r.change_v(sign * delta_v *
                                                 abs(r.p - self.p_avg) / abs_total_p_diff)

            if self.is_same_p or not changed:
                break
            else:
                i += 1

        else:
            logger.warning("値が収束する前に最大計算回数に達しました (pループ)")

        return self.rooms

    def change_temp(self, delta: float) -> list[Room]:
        res = []
        for room in self.rooms:
            res.append(room.change_temp(delta))

        logger.debug("res: {}".format(res))

        iter_cnt = 0
        while iter_cnt < self.max_iter:
            if sum([r[1] for r in res]) != len(self.rooms):
                # 気液平衡では無い
                logger.debug("NOT vapor-liquid equilibrium")
                logger.debug("p_avg: {}".format(self.p_avg))

                # debug
                for i, r in enumerate(self.rooms):
                    logger.debug("p{0}: {1}".format(i, r.p))

                for room in self.rooms:
                    room.move_equi(self.delta_n_in_adjust)

            if not self.is_same_p:
                self.adjust_p()

            if sum([room.is_equi for room in self.rooms]) == len(self.rooms):
                break

            else:
                iter_cnt += 1

        else:
            logger.warning("値が収束する前に最大計算回数に達しました(メインループ)")

        logger.info("T = {:.2f}".format(self.rooms[0].T))
        logger.debug(self.rooms)
        return self.rooms
