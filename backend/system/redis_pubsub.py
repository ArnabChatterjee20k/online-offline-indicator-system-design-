from .cache import Cache
import asyncio
from typing import Callable, Awaitable
class PubSub:
    """
        Listening for shadowkey:<actual key> expiry -> delete actual key -> call callback operation
    """
    def __init__(self):
        self._cache = Cache()
        self.client = self._cache.client
        self.pubsub = None
        self.pubsub_task = None
    
    async def setup_keyspace_notification(self,callback:Callable[..., Awaitable[None]]):
        """
            generally this happens when we listen
            {'type': 'message', 'pattern': b'__keyevent@0__:expired', 'channel': b'__keyevent@0__:expired', 'data': b'shadowKey:testkey'}
        """
        keyevent_expiry_event = "Ex" # to monitor only expiry event and not all operations
        await self.client.config_set("notify-keyspace-events",keyevent_expiry_event)

        self.pubsub = self.client.pubsub()
        await self.pubsub.subscribe("__keyevent@0__:expired")
        self.pubsub_task = asyncio.create_task(self._listen_for_events(callback))
        print("Redis keyspace notifications for expired keys set up successfully")

    async def close(self):
        if self.pubsub:
            await self.pubsub.close()
        if self.pubsub_task:
            self.pubsub_task.cancel()

    async def _listen_for_events(self,callback:Callable[..., Awaitable[None]]):
        try:
            async for message in self.pubsub.listen():
                print("message received ",message)
                if message["type"] == "message":
                    key = message["data"].decode()
                    # grab the shadow key
                    if key.startswith("shadowkey:"):
                        original_key = key.split("shadowkey:")[1]
                        # since it is hset
                        value = await self.client.hget(original_key,"timestamp")
                        if value:
                            value = value.decode()
                            # deleting the actual key
                            await self.client.delete(original_key)
                        # it will give error if callback is not async and not returning a coroutine
                        if asyncio.iscoroutinefunction(callback):
                            await callback(original_key,value)
                        else:
                            callback(original_key,value)

        except asyncio.CancelledError:
            print("Redis pubsub listener task cancleed")
        except Exception as e:
            print(f"Error in Redis pubsub listener",e)