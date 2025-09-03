from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from beanie import PydanticObjectId
from app.models import Jogador
