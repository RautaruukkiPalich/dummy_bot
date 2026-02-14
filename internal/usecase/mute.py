from internal.dto.dto import MuteRequestDTO, MuteResponseDTO
from internal.utils.time_parser import TimeParser


class MuteUseCase:
    def __init__(self, logger):
        self._logger = logger

    async def mute(self, req: MuteRequestDTO) -> MuteResponseDTO|None:
        _, dur, *reason = req.text.split(" ")
        delta = TimeParser.parse_str_to_duration(dur)
        if not delta:
            return None

        if 30 >= delta.total_seconds() or delta.total_seconds() >= 60 * 60 * 24 * 365:
            return None

        delta_str = TimeParser.format_timedelta(delta)

        return MuteResponseDTO(
            delta=delta,
            delta_str=delta_str,
            reason=' '.join(reason),
        )