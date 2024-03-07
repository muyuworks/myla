from myla.tools import Context, Tool
import time
import asyncio

class SyncTool(Tool):
    def execute(self, context: Context) -> None:
        for i in range(10):
            print(f"SyncTool: {i}")
            time.sleep(3)

class AsyncTool(Tool):
    async def execute(self, context: Context) -> None:
        for i in range(10):
            print(f"AsyncTool: {i}")
            await asyncio.sleep(3)
