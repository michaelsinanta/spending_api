import json
import os
from typing import Literal, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from mangum import Mangum


class Cost(BaseModel):
    cost: int
    type: Literal["spending", "saving"]
    id: Optional[str] = uuid4().hex


COST_FILE = "cost.json"
COSTS = []

if os.path.exists(COST_FILE):
    with open(COST_FILE, "r") as f:
        BOOKS = json.load(f)

app = FastAPI()
handler = Mangum(app)


@app.get("/list-costs")
async def list_costs():
    return BOOKS


@app.post("/add-costs")
async def add_costs(cost: Cost):
    cost.id = uuid4().hex
    json_cost= jsonable_encoder(cost)
    COSTS.append(json_cost)

    with open(COST_FILE, "w") as f:
        json.dump(COSTS, f)

    return {"id": cost.id}


@app.get("/get-cost")
async def get_cost(id: str):
    for cost in COSTS:
        if cost["id"] == id:
            return cost

    raise HTTPException(404, f"Cost ID {id} not found in database.")

@app.delete("/delete")
async def delete_cost(id: str):
    for cost in COSTS:
        if cost["id"] == id:
            COSTS.remove(cost)
            break

    with open(COST_FILE, "w") as f:
        json.dump(COSTS, f)

@app.patch("/edit")
async def edit_cost(id: str, costN:Cost):
    edit_cost = None
    for cost in COSTS:
        if cost["id"] == id:
            edit_cost = cost
            break

    json_cost = jsonable_encoder(costN)

    edit_cost['cost'] = json_cost['cost']
    edit_cost['type'] = json_cost['type']
    edit_cost['id'] = json_cost['id']

    with open(COST_FILE, "w") as f:
        json.dump(COSTS, f)