import re
from datetime import timedelta as td
from typing import Tuple, Union, Callable, Dict


class TimeParser:
    @staticmethod
    def parse_str_to_duration(raw: str) -> td | None:
        units = {
            's': 'seconds',
            'm': 'minutes',
            'h': 'hours',
            'd': 'days',
        }

        match = re.match(r'^(\d+)([smhd])$', raw.lower().strip())
        if not match:
            print(f"Неверный формат: {raw}")
            return None

        value, unit = match.groups()
        return td(**{units[unit]: int(value)})

    @staticmethod
    def format_timedelta(delta: td) -> str:
        forms = {
            's': ('секунду', 'секунды', 'секунд'),
            'm': ('минуту', 'минуты', 'минут'),
            'h': ('час', 'часа', 'часов'),
            'd': ('день', 'дня', 'дней'),
        }

        return TimeParser._format_time(
            delta.total_seconds(),
            TimeParser._plural,
            forms,
        )


    @staticmethod
    def _plural(number: int, forms: Tuple) -> str:
        number = abs(number)
        if number % 10 == 1 and number % 100 != 11:
            return forms[0]
        elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
            return forms[1]
        else:
            return forms[2]

    @staticmethod
    def _format_time(
            delta: Union[td, int, float],
            plural_func: Callable[[int, Tuple[str, ...]], str],
            forms: Dict[str, Tuple[str, ...]]
    ) -> str:
        if isinstance(delta, (int, float)):
            delta = td(seconds=delta)

        total_seconds = int(delta.total_seconds())

        if total_seconds < 60:
            value = total_seconds
            unit = plural_func(value, forms['s'])
            return f"{value} {unit}"

        elif total_seconds < 3600:
            value = total_seconds // 60
            unit = plural_func(value, forms['m'])
            return f"{value} {unit}"

        elif total_seconds < 86400:
            value = total_seconds // 3600
            unit = plural_func(value, forms['h'])
            return f"{value} {unit}"

        else:
            value = total_seconds // 86400
            unit = plural_func(value, forms['d'])
            return f"{value} {unit}"
