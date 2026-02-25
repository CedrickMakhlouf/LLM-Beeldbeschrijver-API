from pydantic import BaseModel, ConfigDict, Field, model_validator


class DescribeRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "image_url": "https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/MSFT-Microsoft-Edge-browser-window-RWN3c9?scl=1"
                }
            ]
        }
    )

    image_base64: str | None = Field(
        default=None,
        description="Base64-gecodeerde afbeelding (PNG/JPEG, zonder data-URL prefix)",
    )
    image_url: str | None = Field(
        default=None,
        description="Publiek toegankelijke afbeelding-URL (PNG/JPEG). Wordt opgehaald door de server.",
        examples=["https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/MSFT-Microsoft-Edge-browser-window-RWN3c9?scl=1"],
    )
    image_id: str | None = None

    @model_validator(mode="after")
    def check_image_provided(self) -> "DescribeRequest":
        if not self.image_base64 and not self.image_url:
            raise ValueError("Geef image_base64 of image_url op.")
        return self


class DescribeResponse(BaseModel):
    image_id: str | None
    description: str
    processing_ms: int
