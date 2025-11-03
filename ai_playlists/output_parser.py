from pydantic import BaseModel, Field

"""
    Output parser used by the LLM to return playlists
"""
class Output(BaseModel):
    # client intent
    playlist : list[list[str]] = Field(description="List of songs. A song is a list [artist, title]")
    invalid_request : bool = Field(description="Invalid request")