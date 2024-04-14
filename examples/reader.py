import openpyxl
import requests
import json

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from examples.models import Example

file_path = 'examples.xlsx'

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


async def my_endpoint(db: AsyncSession = Depends(get_session)):
    for row in data:
        new_example = Example(name=row[0],
                              in_russia=row[1],
                              in_dpr=row[2],
                              in_lpr=row[3],
                              in_zaporozhie=row[4],
                              in_kherson=row[5])
        db.add(new_example)
    await db.commit()


