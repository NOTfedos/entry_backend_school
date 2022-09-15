import asyncio
import typer
import os

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import text
from utils.db import engine


cli = typer.Typer()


async def init_models():
    async with engine.begin() as conn:
        f = open(os.path.join(".", "utils",  "init_db.sql"), "r", encoding="utf-8")
        for s in f.read().split(";"):
            # print(s)
            if len(s) != 0:
                await conn.execute(text(s))
        # await conn.cursor.execute(text(f.read()), multi=True)
        # await conn.execute(text(f.read()), multi=True)
        # await conn.run_sync(conn.execute(text(f.read())))
        # await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all)


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")


if __name__ == "__main__":
    cli()
