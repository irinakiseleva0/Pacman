from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

ActionType = Literal["exit", "switch", "push", "pop"]

@dataclass(frozen=True)
class SceneAction:
    type: ActionType
    index: Optional[int] = None  # used for switch/push
