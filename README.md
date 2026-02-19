# COMMANDS

| command               | description                                                                    |
|:----------------------|:-------------------------------------------------------------------------------|
| ```/start```          | join current group to bot (available only for administrators)                  |
| ```/join```           | join current user to pokak challenge                                           |
| ```/leave```          | leave current user from pokak challenge                                        |
| ```/setpokakmedia```  | set animation or sticker to trigger pokak  (available only for administrators) |
| ```/pokakstatweek```  | pokak stats (top-10) current week, starts from Monday                          | 
| ```/pokakstatmonth``` | pokak stats (top-10) current month, starts from 1st day                        |
| ```/pokakstatyear```  | pokak stats (top-10) current year, starts from 1st January                     |
| ```/pokakstatall```   | pokak stats (top-10) of all time                                               |

-----

# MUTE

### Admins can mute chat member (except administrators and bots) using reply to message

```commandline
!w <period> <reason:optional>
```

### Periods table

| symbol | description | usages          |
|:-------|:------------|:----------------|
| `s`    | second      | `43s` or `123s` |
| `m`    | minute      | `1h` or `13h`   |
| `h`    | hour        | `23h` or `23h`  |
| `d`    | day         | `51d` or `1d`   |

### Limits:

##### Mute cant be less than 30 seconds and greater than 365 days

### Examples:

`!w 1m` - mute for 1 minute

`!w 48h Spam` - mute for 48 hours with reason "Spam"

`!w 3d gambling spam` - mute for 3 days with reason "gambling spam"

----- 

# Starting the app

1) install Git, Docker

2) clone repo
   ```bash
   git clone https://github.com/RautaruukkiPalich/dummy_bot
   ```
3) rename `example.env` file to `.env` and edit variables

4) use command to create and start containers

   Windows:
   ```bash
   docker-compose up -d --build
   ```

   Linux/Mac:
   ```bash
   docker compose up -d --build
   ```

5) use command to create migration

   Windows:
   ```bash
   docker-compose exec bot alembic upgrade head
   ```

   Linux/Mac:
   ```bash
   docker compose exec bot alembic upgrade head
   ```

be careful with `down` command. it will remove all data
