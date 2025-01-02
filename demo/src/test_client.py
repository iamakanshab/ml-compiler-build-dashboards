import asyncio
import json
import logging
from datetime import datetime
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
            self.config['github_private_
