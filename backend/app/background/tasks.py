from loguru import logger
import asyncio

async def dummy_background_task(task_name: str, duration: int = 5):
    """
    A placeholder background task to demonstrate background processing.
    """
    logger.info(f"Starting background task: {task_name}")
    await asyncio.sleep(duration)
    logger.info(f"Completed background task: {task_name}")
