import asyncio
import jwt
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
from dataclasses import dataclass, asdict
from aiohttp import web
import aiohttp
from cryptography.hazmat.primitives import serialization
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BuildState:
    id: str
    repository: str
    branch: str
    commit: str
    status: str
    start_time: float
    steps: list
    logs: list
    end_time: Optional[float] = None
    summary: Optional[str] = None

class BuildDashboardServer:
    def __init__(self, config: dict):
        self.config = config
        self.connections = {}  # connection_id -> WebSocket
        self.installation_tokens = {}  # installation_id -> {token, expires_at}
        self.build_states = {}  # build_id -> BuildState
        self.subscriptions = {}  # connection_id -> Set[repository]
        
        # Load GitHub App private key
        with open(config['github_private_key_path'], 'rb') as key_file:
            self.private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )

    async def verify_installation_token(self, token: str) -> Optional[int]:
        try:
            decoded = jwt.decode(
                token,
                self.private_key.public_key(),
                algorithms=['RS256'],
                audience=self.config['github_app_id']
            )
            return decoded.get('installation_id')
        except jwt.InvalidTokenError:
            return None

    async def refresh_installation_token(self, installation_id: int) -> Optional[str]:
        try:
            # Create a JWT for GitHub App authentication
            now = datetime.utcnow()
            payload = {
                'iat': now,
                'exp': now + timedelta(minutes=10),
                'iss': self.config['github_app_id']
            }
            jwt_token = jwt.encode(payload, self.private_key, algorithm='RS256')

            # Get installation token
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'https://api.github.com/app/installations/{installation_id}/access_tokens',
                    headers={
                        'Authorization': f'Bearer {jwt_token}',
                        'Accept': 'application/vnd.github.v3+json'
                    }
                ) as response:
                    if response.status == 201:
                        data = await response.json()
                        token = data['token']
                        expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
                        
                        self.installation_tokens[installation_id] = {
                            'token': token,
                            'expires_at': expires_at
                        }
                        return token
        except Exception as e:
            logger.error(f"Failed to refresh installation token: {e}")
            return None

    async def get_installation_token(self, installation_id: int) -> Optional[str]:
        if installation_id in self.installation_tokens:
            token_data = self.installation_tokens[installation_id]
            if datetime.utcnow() < token_data['expires_at'] - timedelta(minutes=5):
                return token_data['token']
        
        return await self.refresh_installation_token(installation_id)

    async def handle_websocket(self, websocket, path):
        connection_id = None
        try:
            # Verify connection
            auth_header = websocket.request_headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                await websocket.close(1008, 'Unauthorized')
                return

            installation_id = await self.verify_installation_token(auth_header[7:])
            if not installation_id:
                await websocket.close(1008, 'Invalid token')
                return

            # Set up connection
            connection_id = str(len(self.connections))
            self.connections[connection_id] = websocket
            self.subscriptions[connection_id] = set()

            logger.info(f"New connection established: {connection_id}")

            # Handle messages
            async for message in websocket:
                await self.handle_message(connection_id, installation_id, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed: {connection_id}")
        finally:
            if connection_id:
                self.connections.pop(connection_id, None)
                self.subscriptions.pop(connection_id, None)

    async def handle_message(self, connection_id: str, installation_id: int, message: str):
        try:
            data = json.loads(message)
            msg_type = data.get('type')

            handlers = {
                'build_start': self.handle_build_start,
                'build_update': self.handle_build_update,
                'build_complete': self.handle_build_complete,
                'build_query': self.handle_build_query,
                'subscription': self.handle_subscription
            }

            if msg_type in handlers:
                await handlers[msg_type](connection_id, installation_id, data)
            else:
                await self.send_error(connection_id, 'Unknown message type')

        except json.JSONDecodeError:
            await self.send_error(connection_id, 'Invalid JSON')
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error(connection_id, 'Internal error')

    async def handle_build_start(self, connection_id: str, installation_id: int, data: dict):
        build_id = data.get('build_id')
        repository = data.get('repository')
        branch = data.get('branch')
        commit = data.get('commit')

        if not all([build_id, repository, branch, commit]):
            await self.send_error(connection_id, 'Missing required fields')
            return

        build_state = BuildState(
            id=build_id,
            repository=repository,
            branch=branch,
            commit=commit,
            status='started',
            start_time=datetime.utcnow().timestamp(),
            steps=[],
            logs=[]
        )

        self.build_states[build_id] = build_state
        await self.broadcast_build_update(repository, {
            'type': 'build_started',
            'build': asdict(build_state)
        })
        
        await self.create_github_check_run(installation_id, build_state)

    async def handle_build_update(self, connection_id: str, installation_id: int, data: dict):
        build_id = data.get('build_id')
        build_state = self.build_states.get(build_id)
        
        if not build_state:
            await self.send_error(connection_id, 'Build not found')
            return

        if 'step' in data:
            build_state.steps.append({
                'step': data['step'],
                'status': data.get('status'),
                'timestamp': datetime.utcnow().timestamp()
            })

        if 'log' in data:
            build_state.logs.append(data['log'])

        await self.broadcast_build_update(build_state.repository, {
            'type': 'build_update',
            'build': asdict(build_state)
        })

        await self.update_github_check_run(installation_id, build_state)

    async def handle_build_complete(self, connection_id: str, installation_id: int, data: dict):
        build_id = data.get('build_id')
        build_state = self.build_states.get(build_id)
        
        if not build_state:
            await self.send_error(connection_id, 'Build not found')
            return

        build_state.status = data.get('status', 'completed')
        build_state.end_time = datetime.utcnow().timestamp()
        build_state.summary = data.get('summary')

        await self.broadcast_build_update(build_state.repository, {
            'type': 'build_complete',
            'build': asdict(build_state)
        })

        await self.complete_github_check_run(installation_id, build_state)

    async def handle_build_query(self, connection_id: str, installation_id: int, data: dict):
        build_id = data.get('build_id')
        repository = data.get('repository')

        if build_id:
            build_state = self.build_states.get(build_id)
            response = {
                'type': 'build_query_response',
                'build': asdict(build_state) if build_state else None
            }
        elif repository:
            builds = [
                asdict(build) for build in self.build_states.values()
                if build.repository == repository
            ]
            builds.sort(key=lambda x: x['start_time'], reverse=True)
            response = {
                'type': 'build_query_response',
                'builds': builds[:10]  # Latest 10 builds
            }
        else:
            await self.send_error(connection_id, 'Missing build_id or repository')
            return

        await self.connections[connection_id].send(json.dumps(response))

    async def handle_subscription(self, connection_id: str, installation_id: int, data: dict):
        repository = data.get('repository')
        action = data.get('action')

        if not repository or action not in ['subscribe', 'unsubscribe']:
            await self.send_error(connection_id, 'Invalid subscription request')
            return

        if action == 'subscribe':
            self.subscriptions[connection_id].add(repository)
        else:
            self.subscriptions[connection_id].discard(repository)

    async def broadcast_build_update(self, repository: str, message: dict):
        for conn_id, subscribed_repos in self.subscriptions.items():
            if repository in subscribed_repos:
                try:
                    await self.connections[conn_id].send(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send to {conn_id}: {e}")

    async def send_error(self, connection_id: str, message: str):
        try:
            await self.connections[connection_id].send(json.dumps({
                'type': 'error',
                'message': message
            }))
        except Exception as e:
            logger.error(f"Failed to send error to {connection_id}: {e}")

    async def create_github_check_run(self, installation_id: int, build_state: BuildState):
        token = await self.get_installation_token(installation_id)
        if not token:
            return

        owner, repo = build_state.repository.split('/')
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'https://api.github.com/repos/{owner}/{repo}/check-runs',
                headers={
                    'Authorization': f'token {token}',
                    'Accept': 'application/vnd.github.v3+json'
                },
                json={
                    'name': 'Build Dashboard',
                    'head_sha': build_state.commit,
                    'status': 'in_progress',
                    'started_at': datetime.fromtimestamp(build_state.start_time).isoformat()
                }
            ) as response:
                if response.status != 201:
                    logger.error(f"Failed to create check run: {await response.text()}")

    async def start(self):
        server = await websockets.serve(
            self.handle_websocket,
            self.config['host'],
            self.config['port']
        )
        
        logger.info(f"Server started on ws://{self.config['host']}:{self.config['port']}")
        await server.wait_closed()

if __name__ == "__main__":
    config = {
        'host': 'localhost',
        'port': 8080,
        'github_app_id': '<enter app id>',
        'github_private_key_path': '<enter path/to/private-key.pem>'
    }
    
    server = BuildDashboardServer(config)
    asyncio.run(server.start())
