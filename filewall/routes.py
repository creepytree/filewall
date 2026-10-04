"""page routes rendering the gallery"""

from fastapi import APIRouter, Request

from filewall.shell import druids

pages = APIRouter()


@pages.get("/")
async def main_page(request: Request):
    return druids.templates.TemplateResponse(request, "main.jinja2", {})
