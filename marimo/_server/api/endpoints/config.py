# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from starlette.authentication import requires
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse

from marimo import _loggers
from marimo._config.config import PartialMarimoConfig
from marimo._dependencies.dependencies import DependencyManager
from marimo._messaging.msgspec_encoder import asdict
from marimo._messaging.ops import MissingPackageAlert
from marimo._runtime.packages.utils import is_python_isolated
from marimo._runtime.requests import SetUserConfigRequest
from marimo._server.ai.mcp.config import is_mcp_config_empty
from marimo._server.api.deps import AppState
from marimo._server.api.utils import parse_request
from marimo._server.models.models import (
    SaveUserConfigurationRequest,
    SuccessResponse,
)
from marimo._server.router import APIRouter
from marimo._server.sessions import send_message_to_consumer
from marimo._types.ids import ConsumerId

if TYPE_CHECKING:
    from starlette.requests import Request

LOGGER = _loggers.marimo_logger()

# Router for config endpoints
router = APIRouter()


@router.post("/save_user_config")
@requires("edit")
async def save_user_config(
    *,
    request: Request,
) -> JSONResponse:
    """
    requestBody:
        content:
            application/json:
                schema:
                    $ref: "#/components/schemas/SaveUserConfigurationRequest"
    responses:
        200:
            description: Update the user config on disk and in the kernel. Only allowed in edit mode.
            content:
                application/json:
                    schema:
                        $ref: "#/components/schemas/SuccessResponse"
    """  # noqa: E501
    app_state = AppState(request)
    session_id = app_state.get_current_session_id()
    session = app_state.get_current_session()
    # Allow unknown keys to handle backward/forward compatibility
    body = await parse_request(
        request, cls=SaveUserConfigurationRequest, allow_unknown_keys=True
    )
    # TODO: we may want to validate deep-partial here, but validating with PartialMarimoConfig it too strict
    # so we just cast to PartialMarimoConfig
    config = app_state.config_manager.save_config(
        cast(PartialMarimoConfig, body.config)
    )

    async def handle_background_tasks() -> None:
        # Update the server's view of the config
        if config["completion"]["copilot"]:
            LOGGER.debug("Starting copilot server")
            await app_state.session_manager.start_lsp_server()

        # Reconfigure MCP servers if config changed
        mcp_config = config.get("mcp")

        # Handle missing MCP dependencies
        if (
            not is_mcp_config_empty(mcp_config)
            and not DependencyManager.mcp.has()
        ):
            # If we're in an edit session, send an package installation request
            if session_id is not None and session is not None:
                send_message_to_consumer(
                    session=session,
                    operation=MissingPackageAlert(
                        packages=["mcp"],
                        isolated=is_python_isolated(),
                    ),
                    consumer_id=ConsumerId(session_id),
                )

        try:
            from marimo._server.ai.mcp import get_mcp_client

            if mcp_config:
                LOGGER.debug("Reconfiguring MCP servers with updated config")
                mcp_client = get_mcp_client()
                await mcp_client.configure(mcp_config)
                LOGGER.info(
                    f"MCP servers reconfigured: {list(mcp_client.servers.keys())}"
                )
        except Exception as e:
            LOGGER.warning(f"Failed to reconfigure MCP servers: {e}")

    background_task = BackgroundTask(handle_background_tasks)

    # Update the kernel's view of the config
    # Session could be None if the user is on the home page
    session = app_state.get_current_session()
    if session is not None:
        session.put_control_request(
            SetUserConfigRequest(config),
            from_consumer_id=ConsumerId(
                app_state.require_current_session_id()
            ),
        )

    return JSONResponse(
        content=asdict(SuccessResponse()),
        background=background_task,
    )


@router.get("/server_config")
@requires("edit")
async def get_server_config(request: Request) -> JSONResponse:
    """
    Get server runtime configuration
    
    responses:
        200:
            description: Get the server runtime configuration
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            disable_home_page:
                                type: boolean
                                description: Whether the homepage is disabled
                            disable_terminal:
                                type: boolean
                                description: Whether terminal access is disabled
    """
    from marimo._cli.cli import GLOBAL_SETTINGS
    app_state = AppState(request)
    
    # Get the user config and check for server config
    user_config = app_state.config_manager.get_user_config()
    server_config = user_config.get("server", {})
    
    # Return runtime configuration combining user config and CLI flags
    # CLI flags override config file settings
    return JSONResponse(
        content={
            "browser": server_config.get("browser", "default"),
            "follow_symlink": server_config.get("follow_symlink", False),
            "disable_home_page": server_config.get("disable_home_page", False) or GLOBAL_SETTINGS.DISABLE_HOME_PAGE,
            "disable_terminal": server_config.get("disable_terminal", False) or GLOBAL_SETTINGS.DISABLE_TERMINAL,
            "disable_package_installation": server_config.get("disable_package_installation", False) or GLOBAL_SETTINGS.DISABLE_PACKAGE_INSTALLATION,
            "disabled_panels": server_config.get("disabled_panels", []) + GLOBAL_SETTINGS.DISABLED_PANELS,
        }
    )
