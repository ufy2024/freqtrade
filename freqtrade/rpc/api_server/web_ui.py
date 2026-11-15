from pathlib import Path

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette.responses import FileResponse, Response


router_ui = APIRouter(include_in_schema=False, tags=["Web UI"])
NO_STORE = {"Cache-Control": "no-store"}


@router_ui.get("/favicon.ico")
async def favicon():
    return FileResponse(str(Path(__file__).parent / "ui/favicon.ico"))


@router_ui.get("/fallback_file.html")
async def fallback():
    return FileResponse(str(Path(__file__).parent / "ui/fallback_file.html"))


@router_ui.get("/ui_version")
async def ui_version():
    from freqtrade.commands.deploy_ui import read_ui_version

    uibase = Path(__file__).parent / "ui/installed/"
    version = read_ui_version(uibase)

    return {
        "version": version if version else "not_installed",
    }


@router_ui.get("/equity_curve.json")
async def equity_curve():
    path = Path("/freqtrade/user_data/equity_curve.json")
    if not path.is_file():
        return Response(content='{"curves":{}}', media_type="application/json", headers=NO_STORE)
    return FileResponse(str(path), media_type="application/json", headers=NO_STORE)


@router_ui.get("/{rest_of_path:path}")
async def index_html(rest_of_path: str):
    """
    Emulate path fallback to index.html.
    """
    if rest_of_path.startswith(("api", ".")):
        raise HTTPException(status_code=404, detail="Not Found")
    uibase = (Path(__file__).parent / "ui/installed/").resolve()
    filename = (uibase / rest_of_path).resolve()
    # It's security relevant to check "relative_to".
    # Without this, Directory-traversal is possible.
    media_type: str | None = None
    if filename.suffix == ".js":
        # Force text/javascript for .js files - Circumvent faulty system configuration
        media_type = "application/javascript"
    if filename.is_file() and filename.is_relative_to(uibase):
        return FileResponse(str(filename), media_type=media_type, headers=NO_STORE)

    index_file = uibase / "index.html"
    if not index_file.is_file():
        return FileResponse(str(uibase.parent / "fallback_file.html"), headers=NO_STORE)
    # Fall back to index.html, as indicated by vue router docs
    return FileResponse(str(index_file), headers=NO_STORE)
