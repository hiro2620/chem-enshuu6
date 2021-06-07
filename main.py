from logging import basicConfig, getLogger, DEBUG, INFO

from world import Room, Substance
from solver import Solver
from animation import Animation

basicConfig(level=INFO)
# basicConfig(level=DEBUG)
logger = getLogger(__name__)

init_temp = 273 + 100
target_temp = 273
atm = 1.013e5

max_p_error = 5.0

chart_lims = {
    "x": [target_temp, init_temp],
    "y": [0, atm * 1000 / 760]
}
solver_option = {
    "max_p_diff_in_rooms": 200,
    "delta_n_in_adjust": 1e-3,
    "max_iter": 100,
}

s_a = Substance("diethyl ether", 1, init_temp, atm * 800/760,
                Substance.vp_func_generator([[293, atm * 450/760], [313, atm * 900/760]]), max_p_error=max_p_error)

s_b = Substance("ethanol", 0.5, init_temp, atm * 400/760, Substance.vp_func_generator(
    [[293, atm*50/760], [353, 800/760*atm]]), max_p_error=max_p_error)

s_c = Substance("nitrogen", 0.5, init_temp, atm*400/760, lambda _: 1e7)

r_a = Room(s_a.v, [s_a])
r_b = Room(s_b.v, [s_b, s_c])

solver = Solver([r_a, r_b], init_temp, **solver_option)

animation = Animation([r_a, r_b], chart_lims, subplot_funcs=[
                      s_a.vp_func, s_b.vp_func])
animation.create_frame()

step_r: int = 1  # 逆数
for T in range((init_temp-target_temp) * step_r, 0, -1):
    solver.change_temp(- 1/step_r)
    animation.create_frame()

animation.save_anim(frame_duration=50)
