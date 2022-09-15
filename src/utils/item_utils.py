# Import libs
import logging
import sqlalchemy as sa
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import RequestValidationError
# ----------------------------------------------------------------------------------------------------------------------

# Import modules
from models.db_items import SystemItem,SystemItemHistory
from models.pyd_items import SystemItemImportRequest, SystemItemGetNode, \
    SystemItemHistoryResponse, SystemItemHistoryUnit
# ----------------------------------------------------------------------------------------------------------------------


class ItemNotFoundError(Exception):
    """
    Raises when item not found
    """
    pass


async def import_items(session: AsyncSession, items_request: SystemItemImportRequest):
    """
    Adds or update existed items in DB. Apply for all or no one.
    """
    # Loop through all items from request
    for item in items_request.items:

        parent_id = item.parent_id
        size_div = item.size

        # Update parents recursively
        while parent_id is not None:
            # Search for parent item in DB
            parent = await session.execute(sa.select(SystemItem).where(SystemItem.id == parent_id))
            parent = parent.scalars().one_or_none()

            # Validation check
            if parent.itemtype != "FOLDER":
                await session.rollback()
                raise RequestValidationError(errors=[])

            # Update parent info
            parent.date = items_request.update_date
            parent.size = parent.size + size_div
            await session.flush()

            # Save changes to SystemItemHistory DB table
            parent_dict = parent._asdict()
            parent_dict["item_id"] = parent_dict.pop("id")
            session.add(SystemItemHistory(**parent_dict))
            await session.flush()

            # Get new parent ref
            parent_id = parent.parent_id

        # Search for item in DB with same ID
        db_item = await session.execute(sa.select(SystemItem).where(SystemItem.id == item.id))
        db_item = db_item.scalars().one_or_none()

        # If item was found
        if db_item is not None:

            # If try to change item type, raise an exc
            if db_item.itemtype != item.itemtype:
                await session.rollback()
                raise RequestValidationError(errors=[])

            # Update item in DB
            await session.execute(sa.update(SystemItem).where(SystemItem.id == item.id) \
                                  .values(**item.dict(), date=items_request.update_date))

        else:
            # Adding new item to DB
            new_item = SystemItem(**item.dict(), date=items_request.update_date)
            session.add(new_item)

        # Flush session after adding/updating
        await session.flush()

        # Finally, save changes to SystemHistory DB table about created/updated item
        item_dict = item.dict()
        item_dict["item_id"] = item_dict.pop("id")
        session.add(SystemItemHistory(**item_dict, date=items_request.update_date))
        await session.flush()

    # Committing session
    await session.commit()


async def delete_item(session: AsyncSession, id: str, date: datetime):
    """
    Delete item by id. May raise ItemNotFoundError
    """
    # Search for item in db with same ID
    db_item = await session.execute(sa.select(SystemItem).where(SystemItem.id == id))
    db_item = db_item.scalars().one_or_none()

    # Raise exc if no item with that ID
    if db_item is None:
        raise ItemNotFoundError()

    # Save parent ID
    parent_id = db_item.parent_id
    child_size = db_item.size

    # Delete items CASCADE
    await session.execute(sa.delete(SystemItem).where(SystemItem.id == id))
    await session.flush()

    # Update parent update_date and size
    while parent_id is not None:
        # Get parent
        parent = await session.execute(sa.select(SystemItem).where(SystemItem.id == parent_id))
        parent = parent.scalars().one_or_none()

        # Update parent info
        parent.date = date
        parent.size = parent.size - child_size

        # Flush after updating info in DB obj
        await session.flush()

        # Save changes to SystemItemHistory DB table
        parent_dict = parent._asdict()
        parent_dict["item_id"] = parent_dict.pop("id")
        session.add(SystemItemHistory(**parent_dict))
        await session.flush()

        # Get new parent ref
        parent_id = parent.parent_id

    # Committing session
    await session.commit()


async def get_nodes(session: AsyncSession, id: str) -> SystemItemGetNode:
    """
    Get recursive structure of item with certain ID.
    Just find obj with ID and call get_nodes_by_model() func.
    """
    # Search for item in db with same ID
    db_item = await session.execute(sa.select(SystemItem).where(SystemItem.id == id))
    db_item = db_item.scalars().one_or_none()

    # If no item
    if db_item is None:
        raise ItemNotFoundError()

    return await get_nodes_by_model(session, db_item)


async def get_nodes_by_model(session: AsyncSession, db_item: SystemItem) -> SystemItemGetNode:
    """
    Creates node tree recursively.
    """
    # Create model for this item model
    db_item_dict = db_item._asdict()  # {key: value for (key, value) in db_item.items()}
    logging.debug(db_item_dict)
    item_node = SystemItemGetNode(**db_item_dict, children=None)

    if db_item.itemtype == "FILE":
        # If file, return itself
        return item_node
    else:
        # Init children list
        item_node.children = []

        # Get info about children
        children_objs = await session.execute(sa.select(SystemItem).where(SystemItem.parent_id == db_item.id))
        children_objs = children_objs.scalars().all()

        # Get node for each child and put into 'children' list
        for child in children_objs:
            item_node.children.append(await get_nodes_by_model(session, child))

    return item_node


async def get_recent_updated_files(session: AsyncSession, date: datetime) -> SystemItemHistoryResponse:
    """
    Search elements in SystemItem table, which is last updated was recently
    """

    # Query
    state = sa.select(SystemItem)\
        .where(SystemItem.date <= date)\
        .where(SystemItem.date >= date - timedelta(hours=24))
    items = await session.scalars(state)

    # Fill Response model
    updated_items = SystemItemHistoryResponse(items=[])
    for item in items:
        updated_items.items.append(SystemItemHistoryUnit(**item._asdict()))

    return updated_items


async def get_item_history_db(session: AsyncSession, id: str,
                              date_start: datetime, date_end: datetime) -> SystemItemHistoryResponse:
    """
    Create query to SystemItemHistory DB model, gets full history of item.
    """
    # Search for item in db with same ID
    db_item = await session.execute(sa.select(SystemItem).where(SystemItem.id == id))
    db_item = db_item.scalars().one_or_none()

    # If no item
    if db_item is None:
        raise ItemNotFoundError()

    # Get full history of item from DB
    state = sa.select(SystemItemHistory)\
        .where(SystemItemHistory.item_id == id)\
        .where(SystemItemHistory.date >= date_start)\
        .where(SystemItemHistory.date < date_end)
    history = await session.scalars(state)
    history = history.all()

    # Put query to pydantic response model
    resp = SystemItemHistoryResponse(items=[])
    for item in history:
        item_dict = item._asdict()
        item_dict["id"] = item_dict.pop("item_id")
        resp.items.append(SystemItemHistoryUnit(**item_dict))

    return resp
