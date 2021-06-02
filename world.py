from __future__ import annotations
from logging import getLogger

import numpy as np

logger = getLogger(__name__)

R = 8.314510e3


class Substance:
    def __init__(self, name: str, mol: float, T: float, p: float, vp_func: function, max_p_error=0.0) -> None:
        self.name: str = name
        self.mol: float = mol
        self.mol_gas: float = mol
        self.vp_func: float = vp_func
        self.T: float = T
        self.v: float = mol * R * T / p
        self.max_p_error: float = max_p_error
        logger.info("{0} {1}mol {2}K {3}P {4}L".format(
            self.name, self.mol, self.T, self.p, self.v))

    def __repr__(self) -> str:
        return "{0} {1}mol({2}mol) {3}K {4}P {5}L".format(
            self.name, self.mol, self.mol_gas, self.T, self.p, self.v)

    @classmethod
    def vp_func_generator(cls, samples) -> function:
        """
        s(samples):
        [絶対温度, 蒸気圧]の例を２つ持つ配列
        """
        # 参考: http://mikecat.org/chem/chem071110c.pdf
        T1, p1 = samples[0]
        T2, p2 = samples[1]
        L = np.log(p2/p1) * R / (1/T1 - 1/T2)
        C = np.exp(np.log(p1) + L / (R * T1))

        def vp_funv(T):
            return C * np.exp(-L/(R * T))

        return vp_funv

    @property
    def mol_liquid(self) -> float:
        n = self.mol - self.mol_gas
        assert n >= 0
        return n

    @property
    def p(self):
        return self.mol_gas * R * self.T / self.v

    @property
    def is_equi(self) -> bool:
        max_p_error = self.max_p_error
        return self.p <= max_p_error + self.vp_func(self.T) and not (self.p <= self.vp_func(self.T) - max_p_error and self.mol_liquid > 0)

    def change_temp(self, delta_T: float) -> float:
        self.T = self.T + delta_T
        return self.p, self.is_equi

    def change_v(self, delta_v: float) -> float:
        self.v += delta_v
        logger.debug("v:  {}".format(delta_v))
        assert self.v >= 0
        return self.v

    def move_equi(self, delta_mol: float) -> float:
        if self.p <= self.vp_func(self.T) - self.max_p_error and self.mol_liquid > 0:
            self.mol_gas += delta_mol
            logger.debug("⇡ " + self.name)
            if self.mol_gas > self.mol:
                self.mol_gas = self.mol
            return self.p

        if self.p > self.vp_func(self.T) + self.max_p_error:
            self.mol_gas -= delta_mol
            logger.debug("↓ " + self.name)
            if self.mol_gas < 0:
                self.mol_gas = 0
            return self.p

        return self.p


class Room:
    def __init__(self, v: float, substances: list[Substance]) -> None:
        self.substances = substances

    def __repr__(self) -> str:
        return str(self.substances)

    @ property
    def p(self) -> float:
        return sum([s.p for s in self.substances])

    @ property
    def v(self) -> float:
        return self.substances[0].v

    @ property
    def mol_gas(self) -> float:
        return sum([s.mol_gas for s in self.substances])

    @ property
    def mol_liquid(self) -> float:
        return sum([s.mol_liquid for s in self.substances])

    @ property
    def T(self) -> float:
        return self.substances[0].T

    @ property
    def is_equi(self) -> bool:
        return sum([s.is_equi for s in self.substances]) == len(self.substances)

    def change_temp(self, delta_T) -> list:
        is_equi = True
        res_p = []
        for s in self.substances:
            p, _is_equi = s.change_temp(delta_T)
            res_p.append(p)
            is_equi = is_equi and _is_equi
        return [res_p, is_equi]

    def change_v(self, delta_v) -> bool:
        if self.v - delta_v < 0:
            return False

        for s in self.substances:
            s.change_v(delta_v)

        return True

    def move_equi(self, delta_n):
        for s in self.substances:
            s.move_equi(delta_n)
