from typing import TypedDict, Annotated, Optional
import operator

class AppState(TypedDict):
    messages: Annotated[list, operator.add]
    intent: Optional[str]
    user_data: dict
    stage: Optional[str]