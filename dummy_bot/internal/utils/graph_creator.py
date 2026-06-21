from datetime import date
from io import BytesIO
from typing import List

import matplotlib
from matplotlib.axes import Axes

matplotlib.use('Agg')

import numpy as np
from matplotlib import pyplot as plt, ticker

from dummy_bot.internal.dto.dto import PeriodStats, UserStatInfoDTO


class GraphCreator:

    @staticmethod
    async def from_daily_stats(stats: PeriodStats, top_n: int = 10, cumulative: bool = True) -> BytesIO | None:
        try:
            if not stats:
                return None

            top_users = stats.get_top_users(n=top_n)
            dates = stats.get_dates()

            fig, ax = plt.subplots(figsize=(14, 7))

            for user in top_users:
                GraphCreator._plot_timeline(ax, stats, user, dates, cumulative)

            GraphCreator._fill_axes(ax, y_label="покаки")

            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            buf = BytesIO()
            plt.savefig(buf, format='webp', dpi=150, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            plt.close(fig)

            return buf
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    @staticmethod
    def _plot_timeline(
            ax: plt.Axes,
            stats: PeriodStats,
            user: UserStatInfoDTO,
            dates: List[date],
            cumulative: bool = False,
            alpha: float = 0.3) -> None:

        timeline = stats.get_user_timeline(user.username)
        daily_counts = np.array([timeline.get(d, 0) for d in dates])

        y_values = np.cumsum(daily_counts) if cumulative else daily_counts

        y_smoothed = np.zeros_like(y_values, dtype=float)
        y_smoothed[0] = y_values[0]

        if len(y_values) > 0:
            GraphCreator._approximate(y_values, y_smoothed, alpha=alpha)

        ax.plot(dates, y_smoothed, linewidth=2.5, alpha=0.8,
                label=f"{user.username or user.fullname} ({user.count})")

    @staticmethod
    def _approximate(
            y_original: np.ndarray,
            y_smoothed: np.ndarray,
            alpha: float = 0.3
    ) -> np.ndarray:
        for i in range(1, len(y_original)):
            current_alpha = alpha if y_original[i] > 5 else alpha * 0.5
            y_smoothed[i] = current_alpha * y_original[i] + (1 - current_alpha) * y_smoothed[i - 1]

        y_smoothed[-1] = y_original[-1]

        return y_smoothed

    @staticmethod
    def _fill_axes(
            ax: Axes,
            y_label: str = '',
            x_label: str = '',
    ) -> Axes:
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_visible(False)

        ax.grid(True, alpha=0.3, linestyle='-', axis='y')
        ax.set_axisbelow(True)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=10))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=10))
        ax.set_ylabel(y_label, fontsize=12)
        ax.set_xlabel(x_label, fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, frameon=False)

        return ax
