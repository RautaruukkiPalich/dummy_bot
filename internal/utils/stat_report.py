from typing import List

from internal.dto.dto import UserStatInfoDTO
from internal.utils.stat_flter import PeriodEnum

class ReportStat:
    def __init__(
            self,
            period: PeriodEnum,
            data: List[UserStatInfoDTO],
            limit: int = 10,
    ) -> None:
        self.period = period
        self.data = data
        self.limit = limit

    def prepare(self) -> str:
        return "\n\n".join([self._header(), self._body()])

    def _header(self) -> str:
        header = f"Toп-{self.limit} засранцев"

        match self.period:
            case PeriodEnum.WEEK:
                return f"{header} текущей недели:"
            case PeriodEnum.MONTH:
                return f"{header} текущего месяца:"
            case PeriodEnum.YEAR:
                return f"{header} текущего года:"
            case PeriodEnum.ALL:
                return f"{header} за всё время:"

    def _body(self) -> str:
        self.data = sorted(self.data, key=lambda x: x.count, reverse=True)

        lines = [
            self.__format_line(num, data)
            for num, data in enumerate(self.data, 1)
        ][:self.limit]

        return "\n".join(lines)

    def __format_line(self, num: int, data: UserStatInfoDTO) -> str:
        username = data.username or data.fullname
        ending = self.__get_ending(data.count)
        return f"<b>{num}</b>: {username} - <i>{data.count} {ending}</i>"

    @staticmethod
    def __get_ending(num: int) -> str:
        if 11 < num % 100 < 15:
            return "раз"
        if 1 < num % 10 < 5:
            return "раза"
        return "раз"

    def __str__(self) -> str:
        return f"Creating report for {self.period}"