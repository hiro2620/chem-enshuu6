from __future__ import annotations
import pathlib
from logging import getLogger

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

from world import Room, Substance

logger = getLogger(__name__)


class Animation:
    def __init__(self, rooms: list[Room], chart_lims, subplot_funcs=[], frame_size=(16.0, 9.0), out_dir="./out"):
        self.rooms = rooms
        self.frames = []
        self.p_history = {}
        self.T_history = []
        self.frame_size = frame_size
        self.subplot_funcs = subplot_funcs
        self.chart_lims = chart_lims
        self.frame_cnt = 0

        self.out_dir = pathlib.Path(out_dir)
        self.out_dir.mkdir(exist_ok=True)
        logger.info("out path: {}".format(str(self.out_dir)))

        self.all_substances = []
        for r in self.rooms:
            for s in r.substances:
                self.all_substances.append(s)

        self.p_history["total"] = []  # total
        for s in self.all_substances:
            self.p_history[s.name] = []

    def create_frame(self):
        fig = plt.figure(figsize=self.frame_size)
        ax0 = fig.add_subplot(1, 2, 1)
        ax0.set_position([0.05, 0.35, 0.44, 0.4])
        ax1 = fig.add_subplot(1, 2, 2)
        ax1.set_position([0.6, 0.18, 0.35, 0.64])

        self.render_room(ax0)
        self.render_chart(ax1)

        self.frames.append(fig)
        self.frame_cnt += 1

        fig.savefig(str(self.out_dir / "{}.png".format(self.frame_cnt)))
        plt.clf()
        plt.close()

    def render_room(self, ax):
        total_v = sum([r.v for r in self.rooms])
        max_liquid_r = 0.036
        start_pos = 0
        ax.set_title("{:.1f}K".format(self.rooms[0].T), fontsize=20)
        for room in self.rooms:
            width = room.v / total_v
            rect = patches.Rectangle(xy=(start_pos, 0), width=width,
                                     height=1.0, ec='#444', fill=False, fc="r")

            radius = max_liquid_r * np.sqrt(room.mol_liquid /
                                            (room.mol_gas + room.mol_liquid))
            liquid = patches.Circle(
                xy=(start_pos + radius, 0), radius=radius, fc='b', ec='b')

            ax.add_patch(rect)
            ax.add_patch(liquid)
            start_pos += width

    def render_chart(self, ax):
        ax.set_xlim(self.chart_lims["x"])
        ax.set_ylim(self.chart_lims["y"])
        ax.set_xlabel("T [K]")
        ax.set_ylabel("P [Pa]")

        T = np.arange(273, 373, 1)
        for f in self.subplot_funcs:
            ax.plot(T, f(T))

        self.T_history.append(self.rooms[0].T)
        ax.axvline(self.T_history[-1])

        self.p_history["total"].append(self.rooms[0].p)
        for s in self.all_substances:
            self.p_history[s.name].append(s.p)

        for key in self.p_history:
            ax.scatter(self.T_history, self.p_history[key], label=key)

        ax.legend()

    def save_anim(self, out_gif_name="out.gif", frame_duration=30):
        images = []
        for i in range(self.frame_cnt):
            file_name = str(self.out_dir / "{}.png".format(i+1))
            im = Image.open(file_name)
            images.append(im)

        images[0].save(out_gif_name, save_all=True,
                       append_images=images[1:], loop=0, duration=frame_duration)
