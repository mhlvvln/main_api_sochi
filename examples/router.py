import openpyxl
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from database.database import get_session
from examples.models import Example

examples_router = APIRouter()


class AddSchema(BaseModel):
    name: str
    in_russia: float
    in_dpr: float
    in_lpr: float
    in_zaporozhie: float
    in_kherson: float


@examples_router.post("/add")
async def add(data: AddSchema, db: AsyncSession = Depends(get_session)):
    success = 0
    file_path = 'examples/examples.xlsx'
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    ignore_rows = [14, 21, 31, 42, 50, 82, 85]
    data = []
    for i in range(7, 87):
        if i in ignore_rows:
            continue
        row = []
        for j in range(2, 8):
            cell_value = sheet.cell(row=i, column=j).value
            row.append(cell_value)
        data.append(row)
    workbook.close()

    print("количество строк: ", str(len(data)))
    for row in data:
        if row[1] is not None and row[2] is not None and row[3] is not None:
            name = row[0] if row[0] == "..." else ""
            in_russia = float(row[1]) if row[1] == "..." else 0.0
            in_dpr = float(row[2]) if row[2] == "..." else 0.0
            in_lpr = float(row[3]) if row[3] == "..." else 0.0
            in_zaporozhie = float(row[4]) if row[4] == "..." else 0.0
            in_kherson = float(row[5]) if row[5] == "..." else 0.0

            new_example = Example(
                name=name,
                in_russia=in_russia,
                in_dpr=in_dpr,
                in_lpr=in_lpr,
                in_zaporozhie=in_zaporozhie,
                in_kherson=in_kherson
            )
            db.add(new_example)
            try:
                # await db.commit()
                success += 1
                print("Success: ", row)
            except Exception as e:
                print()
                print()
                print()
                print(e)
                print()
                print()
                print()

    print("Успешно строк передано: ", success)


@examples_router.get("/all")
async def get_all(db: AsyncSession = Depends(get_session)):
    examples = await db.execute(select(Example))
    examples = examples.fetchall()
    if examples is None:
        return JSONResponse(status_code=200, content=[])
    return [await example.to_dict() for example in examples[0]]


@examples_router.get("/getByName")
async def get_by_name(name: str, db: AsyncSession = Depends(get_session)):
    example = await db.execute(select(Example).where(Example.name == name).limit(1))
    example = example.fetchone()
    if example is None:
        return JSONResponse(status_code=404, content=[])

    example = example[0]
    return example.to_dict()
