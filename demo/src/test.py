# tests/test_build_dashboard.py
import pytest
import asyncio
import json
import websockets
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Assuming your server and client are in these files
from build_dashboard_server import BuildDashboardServer
from build_dashboard_client import BuildDashboardClient

@pytest.fixture
def config():
    return {
        'host': 'localhost',
        'port': 8765,
        'github_app_id': 'test_app_id',
        'github_private_key_path': 'test_private_key.pem',
        'installation_id': '12345'
    }

@pytest.fixture
def mock_private_key():
    return """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1c7+9z5Pad7OejecsQ0bu3aozN3tihPmljnnudb9G3HECdnH
lWu2/a1gB9JW5TBQ+AVpum9Okx7KfqkfBKL9mcHgSL0yWMdjMfNOqNtrQqKlN4kE
p6RD++7sGbzbfZ9arwrlD/HSDAWGdGGJTSOBM6pHehyLmSC3DJoR/CTu0vTGTWXQ
rO64Z8tyXQPtVPb/YXrcUhbBp8i72b9Xky0fD6PkEebOy0Ip58XVAn2UPNlNOSPS
ye+Qjtius0Md4Nie4+X8kwVI2Qjk3dSm0sw/720KJkdVDmrayeljtKBx6AtNQsSX
gzQbeMmiqFFkwrG1+zx6E7H7jqIQ9B6bvWKXGwIDAQABAoIBAD8kBBPL6PPhAqUB
K1r1/gycfDkUCQRP4DbZHt+458JlFHm8DYpBH+/5xsZqF9rLL+APq7X0NQ+Z7da+
8jAeuhEVZO+rZaghY2+4YxknRQJ8lrQXwZYEu3ZHqlvidZmTJgF6YvEIdw1WAcD6
qjZW7M5FD4XcYbXOL4rQP6UYVTzCvwpFWScwsZZTQKjOicd3ysBYYgg0RwJ6Yt6w
LPf+lDfcJJtX6vSP3NqN/+jZI3qecN/WCrVSSP8/uqFRsn2TPzK+EwUHJcq8rsjM
0updKCN1Wk7KYsFhN5ylvAk2GCLHnM+3FAHgWdrtSCjvFC9Bk2EqsIRk5zvQYkES
Vk2T/MECgYEA6KQXB/9IGQH9HqO9pwC5lsrT7r5CJY376OqxOzZVhx3WuWUXP7Ck
5wF5fzF9LjfyrnwZZxFHK6YqZuAjBkm8DSKzWLBl7NWhxwEFzDRVqCZ7slMEIF+i
Yvn/x1+q1h7nUy3ZNZee/UssqjhM1zV5fttILzyG7QEXvIvSuHkBzSMCgYEA6s+U
dC7tuE7/+Glm3SdsEfigYUAQr3g/Q6ytNhhzP6WRYssyqFBhjOtxSDP7JJw8S+xG
.....
-----END RSA PRIVATE KEY-----"""

@pytest.fixture
async def server(config, mock_private_key):
    with patch('builtins.open', mock_open(read_data=mock_private_key)):
        server = BuildDashboardServer(config)
        await server.start()
        yield server
        # Cleanup
        for conn in server.connections.values():
            await conn.close()

@pytest.mark.asyncio
async def test_server_client_connection(config, server):
    # Create a test client
    client = BuildDashboardClient({
        'server_url': f"ws://{config['host']}:{config['port']}",
        'github_app_id': config['github_app_id'],
        'github_private_key_path': config['github_private_key_path'],
        'installation_id': config['installation_id'],
        'repositories': ['iree-org/iree']
    })

    # Test connection establishment
    connected = False
    async def on_connect():
        nonlocal connected
        connected = True
    
    client.on('connect', on_connect)
    await client.connect()
    
    assert connected

@pytest.mark.asyncio
async def test_build_workflow(config, server):
    client = BuildDashboardClient(config)
    
    # Track received messages
    received_messages = []
    async def on_build_update(message):
        received_messages.append(message)
    
    client.on('build_update', on_build_update)
    await client.connect()
    
    # Subscribe to repository
    await client.subscribe_to_repository('iree-org/iree')
    
    # Start a build
    build_id = 'test-build-1'
    await client.send_build_start({
        'build_id': build_id,
        'repository': 'iree-org/iree',
        'branch': 'main',
        'commit': 'abc123'
    })
    
    # Update build
    await client.send_build_update({
        'build_id': build_id,
        'step': 'compile',
        'status': 'running'
    })
    
    # Complete build
    await client.send_build_complete({
        'build_id': build_id,
        'status': 'success',
        'summary': 'Build completed successfully'
    })
    
    # Wait for messages
    await asyncio.sleep(1)
    
    # Verify received messages
    assert len(received_messages) == 3
    assert received_messages[0]['type'] == 'build_started'
    assert received_messages[1]['type'] == 'build_update'
    assert received_messages[2]['type'] == 'build_complete'

# Example usage script
if __name__ == "__main__":
    async def main():
        # Server configuration
        server_config = {
            'host': 'localhost',
            'port': 8080,
            'github_app_id': 'your_app_id',
            'github_private_key_path': 'path/to/private-key.pem'
        }
        
        # Start server
        server = BuildDashboardServer(server_config)
        server_task = asyncio.create_task(server.start())
        
        # Client configuration
        client_config = {
            'server_url': 'ws://localhost:8080',
            'github_app_id': 'your_app_id',
            'github_private_key_path': 'path/to/private-key.pem',
            'installation_id': 'your_installation_id',
            'repositories': ['iree-org/iree', 'iree-org/iree-turbine']
        }
        
        # Create client
        client = BuildDashboardClient(client_config)
        
        # Set up event handlers
        def on_build_start(data):
            print(f"Build started: {data}")
        
        def on_build_update(data):
            print(f"Build update: {data}")
        
        def on_build_complete(data):
            print(f"Build complete: {data}")
        
        client.on('build_started', on_build_start)
        client.on('build_update', on_build_update)
        client.on('build_complete', on_build_complete)
        
        # Connect client
        await client.connect()
        
        # Example: Send a test build
        await client.send_build_start({
            'build_id': 'test-1',
            'repository': 'iree-org/iree',
            'branch': 'main',
            'commit': 'abc123'
        })
        
        # Keep the connection alive
        try:
            await asyncio.gather(server_task)
        except KeyboardInterrupt:
            print("Shutting down...")

    asyncio.run(main())
