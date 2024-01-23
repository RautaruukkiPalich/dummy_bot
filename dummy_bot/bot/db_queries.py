from dummy_bot.bot.models import TelegramUser


async def get_or_create_member(user: TelegramUser) -> None:
    print(f'Add: {user.group_id=} | {user.user_id=}: {user.username=}')
    return None


async def delete_member(user: TelegramUser) -> None:
    print(f'Delete: {user.group_id=} | {user.user_id=}: {user.username=}')
    return None


async def create_pokak(user: TelegramUser) -> None:
    print(f'Pokak successful: {user.group_id=} | {user.user_id=}: {user.username=}')
    return None


async def get_pokak_stat(period: str) -> dict:
    tmp_pokaks = {
        'rautaruukki': 4,
        'boris': 6,
        'britva': 5,
    }
    if period == "year":
        del tmp_pokaks['britva']
        tmp_pokaks['rautaruukki'] -= 2

    return tmp_pokaks
