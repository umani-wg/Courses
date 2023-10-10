import logging
from src.helpers.jwt_helper import get_token
from fastapi import APIRouter, Request, Body, status, Query, Path
from typing import Annotated
from src.helpers import grant_access, validate_body, log
from fastapi.responses import JSONResponse
from datetime import datetime
import starlette


from src.controllers.account import Account
from src.controllers.menu import Menu
from src.schemas import MenuSchema, UpdateSchema, UpdateItemSchema
from src.helpers.exceptions import error
from enum import Enum

router = APIRouter()
logger = logging.getLogger(__name__)


class Status(str, Enum):
    published = "published"
    pending = "pending"
    not_published = "not_published"
    rejected = "rejected"


@router.get("/menu", status_code=status.HTTP_200_OK)
@grant_access
@log
def get_menu(request: Request, status: Annotated[Status, Query()]):
    grp_id = get_token(request=request).get("grp_id")
    menu = Menu()

    if status is status.published:
        response = menu.view_accepted_menu(grp_id=grp_id)
    else:
        response = menu.get_menu_by_status(grp_id=grp_id, status=status)

    if len(response) == 0:
        logger.error("No menu found error")
        return JSONResponse(
            status_code=starlette.status.HTTP_400_BAD_REQUEST,
            content=error(
                code=404,
                message="No such menu found.",
            ),
        )
    else:
        logger.debug("GET Menu response -> {response}")
        date = response[0][1]
        items = [item[0] for item in response]
        return dict(menu_id=response[0][2], date=date, items=items)


@router.post("/menu", status_code=status.HTTP_201_CREATED)
@grant_access
@validate_body(MenuSchema)
@log
def post_menu(request: Request, body: Annotated[dict, Body()]):
    menu = Menu()
    items = body["items"]
    logger.debug(f"POST /menu called with body -> {body}")
    name = get_token(request=request).get("username")
    grp_id = get_token(request=request).get("grp_id")
    date = body["date"]
    datetime_object = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    response = menu.propose_menu(items, datetime_object, name, grp_id)
    logger.debug(f"POST /menu returned response -> {response}")
    return dict(message=response)


@log
@grant_access
@validate_body(UpdateSchema)
@router.put("/menu", status_code=status.HTTP_200_OK)
def put_menu(request: Request, body: Annotated[dict, Body()]):
    logger.debug(f"PUT /menu caled with body -> {body}")
    grp_id = get_token(request=request).get("grp_id")
    menu = Menu()
    menu_id = body["menu_id"]
    status = body["status"]

    if status == "published":
        response = menu.get_menu_by_status(grp_id=grp_id, status="not published")
        date = response[0][1]
        menu.publish_menu(menu_id=menu_id, grp_id=grp_id, menu_date=date)
        account = Account()
        account.update_balance(amount=137, grp_id=grp_id)
        logger.debug("PUT /menu successful")
        return dict(message="success")

    elif status == "rejected":
        comments = body["comments"]
        username = get_token(request=request).get("username")
        response = menu.reject_menu(
            menu_id=menu_id, comments=comments, username=username
        )
        logger.debug("PUT /menu successful")
        return dict(message=response)
    else:
        logger.debug("PUT /menu successful")
        response = menu.update_menu_status(status, menu_id)
        return dict(message=response)


@router.patch("/menu/{menu_id}", status_code=status.HTTP_200_OK)
@validate_body(UpdateItemSchema)
@grant_access
@log
def patch_menu(
    request: Request, body: Annotated[dict, Body()], menu_id: Annotated[int, Path()]
):
    logger.debug(f"PATCH /menu/{menu_id} called with body -> {body}")
    menu = Menu()
    menu.update_menu(
        menu_id=menu_id, old_item=body["old_item"], new_item=body["new_item"]
    )
    return dict(message="success", new_item=body["new_item"], menu_id=menu_id)
