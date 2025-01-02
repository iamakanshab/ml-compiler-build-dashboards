import asyncio
import json
import logging
from datetime import datetime, timedelta
import websockets
from typing import Optional, Callable, Dict, Any
import jwt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuildDashboardClient:
    def __init__(self, config: dict):
        self.config = config
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.callbacks: Dict[str, Callable] = {}
        self.reconnect_delay = 1
        self.max_reconnect_delay = 60
        self.installation_id = config.get('installation_id')

    def on(self, event_type: str, callback: Callable):
        """Register a callback for specific event types"""
        self.callbacks[event_type] = callback

    async def connect(self):
        """Establish WebSocket connection with automatic reconnection"""
        while True:
            try:
                # Generate JWT token for authentication
                token = self._generate_jwt()
                
                # Connect to WebSocket server
                async with websockets.connect(
                    self.config['server_url'],
                    extra_headers={'Authorization': f'Bearer {token}'}
                ) as websocket:
                    logger.info("Connected to build dashboard server")
                    self.websocket = websocket
                    self.reconnect_delay = 1  # Reset delay on successful connection
                    
                    # Subscribe to repositories
                    for repo in self.config.get('repositories', []):
                        await self.subscribe_to_repository(repo)
                    
                    await self._handle_messages()
                    
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Connection closed, attempting to reconnect...")
                await self._handle_reconnection()
            except Exception as e:
                logger.error(f"Connection error: {e}")
                await self._handle_reconnection()

    def _generate_jwt(self) -> str:
        """Generate JWT token for GitHub App authentication"""
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'exp': now + timedelta(minutes=10),
            'iss': self.config['github_app_id'],
            'installation_id': self.installation_id
        }
        return jwt.encode(
            payload,
            self.config['github_private_key'],
            algorithm='RS256'
        )

    async def _handle_reconnection(self):
        """Handle reconnection with exponential backoff"""
        await asyncio.sleep(self.reconnect_delay)
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)

    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        async for message in self.websocket:
            try:
                data = json.loads(message)
                message_type = data.get('type')
                
                if message_type in self.callbacks:
                    await self._execute_callback(message_type, data)
                else:
                    logger.warning(f"No handler for message type: {message_type}")
                    
            except json.JSONDecodeError:
                logger.error("Failed to decode message")
            except Exception as e:
                logger.error(f"Error handling message: {e}")

    async def _execute_callback(self, event_type: str, data: dict):
        """Execute callback for event type with error handling"""
        try:
            callback = self.callbacks[event_type]
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logger.error(f"Error in callback for {event_type}: {e}")

    async def send_message(self, message: dict):
        """Send a message to the WebSocket server"""
        if not self.websocket:
            raise ConnectionError("Not connected to server")
        
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def subscribe_to_repository(self, repository: str):
        """Subscribe to repository events"""
        await self.send_message({
            'type': 'subscription',
            'repository': repository,
            'action': 'subscribe'
        })

    async def unsubscribe_from_repository(self, repository: str):
        """Unsubscribe from repository events"""
        await self.send_message({
            'type': 'subscription',
            'repository': repository,
            'action': 'unsubscribe'
        })

    async def send_build_start(self, data: dict):
        """Send build start event"""
        await self.send_message({
            'type': 'build_start',
            **data
        })

    async def send_build_update(self, data: dict):
        """Send build update event"""
        await self.send_message({
            'type': 'build_update',
            **data
        })

    async def send_build_complete(self, data: dict):
        """Send build complete event"""
        await self.send_message({
            'type': 'build_complete',
            **data
        })

    async def query_build(self, build_id: str = None, repository: str = None):
        """Query build information"""
        await self.send_message({
            'type': 'build_query',
            'build_id': build_id,
            'repository': repository
        })

    async def close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

# Example usage
if __name__ == "__main__":
    async def main():
        config = {
            'server_url': 'ws://localhost:8080',
            'github_app_id': 'your_app_id',
            'github_private_key': 'your_private_key',
            'installation_id': 'your_installation_id',
            'repositories': ['iree-org/iree']
        }
        
        client = BuildDashboardClient(config)
        
        # Register event handlers
        def on_build_start(data):
            print(f"Build started: {data}")
        
        def on_build_update(data):
            print(f"Build update: {data}")
        
        def on_build_complete(data):
            print(f"Build complete: {data}")
        
        client.on('build_started', on_build_start)
        client.on('build_update', on_build_update)
        client.on('build_complete', on_build_complete)
        
        try:
            await client.connect()
        except KeyboardInterrupt:
            await client.close()

    asyncio.run(main())
