#!/usr/bin/env python3
"""
Substrate WebSocket Server
Bridges the visualization with AI agent swarm coordination
"""

import asyncio
import json
import websockets
import random
from datetime import datetime

# Agent configurations
AGENT_CONFIGS = [
    {"name": "Atlas", "role": "research", "color": "#00f0ff"},
    {"name": "Nova", "role": "analysis", "color": "#ff00aa"},
    {"name": "Cipher", "role": "synthesis", "color": "#ffd700"},
    {"name": "Echo", "role": "validation", "color": "#00ff88"},
    {"name": "Sage", "role": "research", "color": "#00f0ff"}
]

# Sample findings templates
FINDING_TEMPLATES = [
    "Identified cross-domain pattern in {topic}",
    "Discovered novel approach to {topic}",
    "Found correlation between {topic} and distributed systems",
    "Mapped evolutionary pathway in {topic}",
    "Synthesized new framework for {topic}",
    "Validated hypothesis about {topic}",
    "Uncovered hidden relationship in {topic}",
    "Extracted key insights from {topic} research",
    "Detected emergent properties in {topic}",
    "Formulated new theory regarding {topic}"
]

CONNECTION_REASONS = [
    "Sharing overlapping discoveries",
    "Coordinating research directions",
    "Cross-validating findings",
    "Synthesizing complementary insights",
    "Identifying pattern convergence"
]

class SwarmCoordinator:
    """Coordinates the AI agent swarm"""

    def __init__(self, websocket, topic):
        self.ws = websocket
        self.topic = topic
        self.agents = []
        self.active = True

    async def send_message(self, msg):
        """Send JSON message to client"""
        try:
            await self.ws.send(json.dumps(msg))
        except Exception as e:
            print(f"Error sending message: {e}")
            self.active = False

    async def spawn_agent(self, config, index):
        """Spawn a single agent"""
        agent_id = f"agent-{index}"
        agent = {
            "id": agent_id,
            "name": config["name"],
            "role": config["role"],
            "color": config["color"],
            "findings": []
        }
        self.agents.append(agent)

        await self.send_message({
            "type": "agent_spawn",
            "id": agent_id,
            "name": config["name"],
            "role": config["role"],
            "color": config["color"]
        })

        return agent

    async def agent_research(self, agent):
        """Simulate agent research activity"""
        # Number of findings this agent will discover
        num_findings = random.randint(3, 6)

        for i in range(num_findings):
            if not self.active:
                break

            # Wait before next finding
            await asyncio.sleep(random.uniform(3, 8))

            # Generate finding
            template = random.choice(FINDING_TEMPLATES)
            finding = template.format(topic=self.topic)
            agent["findings"].append(finding)

            await self.send_message({
                "type": "agent_update",
                "id": agent["id"],
                "status": "researching",
                "finding": finding
            })

            # Random chance to connect with another agent
            if len(self.agents) > 1 and random.random() > 0.5:
                other_agent = random.choice([a for a in self.agents if a["id"] != agent["id"]])
                await self.send_message({
                    "type": "agent_connect",
                    "from": agent["id"],
                    "to": other_agent["id"],
                    "reason": random.choice(CONNECTION_REASONS)
                })
                await asyncio.sleep(0.5)

    async def synthesize_results(self):
        """Synthesize all agent findings"""
        total_findings = sum(len(agent["findings"]) for agent in self.agents)

        synthesis = (
            f"Research complete. Discovered {total_findings} unique insights about \"{self.topic}\". "
            f"Key finding: Emergent properties arise when {len(self.agents)} specialized agents "
            f"coordinate through persistent memory substrate. This validates the core thesis of "
            f"identity-preserving AI collaboration."
        )

        await self.send_message({
            "type": "synthesis",
            "text": synthesis
        })

        # Add to memory
        await self.send_message({
            "type": "memory_update",
            "layer": "collaborative_research",
            "content": self.topic
        })

    async def run_swarm(self):
        """Execute the full swarm coordination"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting swarm for topic: {self.topic}")

        # Spawn agents with delays
        for i, config in enumerate(AGENT_CONFIGS):
            if not self.active:
                break
            agent = await self.spawn_agent(config, i)
            await asyncio.sleep(0.6)

        # Run agent research in parallel
        research_tasks = [self.agent_research(agent) for agent in self.agents]
        await asyncio.gather(*research_tasks)

        if not self.active:
            return

        # Synthesis phase
        await asyncio.sleep(2)
        await self.send_message({
            "type": "agent_update",
            "id": "magnus",
            "status": "synthesizing",
            "finding": "Synthesizing collective findings..."
        })

        await asyncio.sleep(3)
        await self.synthesize_results()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Swarm complete")


async def handle_client(websocket, path):
    """Handle WebSocket client connection"""
    client_addr = websocket.remote_address
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Client connected: {client_addr}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)

                if data.get("type") == "start":
                    topic = data.get("topic", "AI collaboration")

                    # Create and run swarm coordinator
                    coordinator = SwarmCoordinator(websocket, topic)
                    await coordinator.run_swarm()

                    # Note: In a real implementation, this is where you would:
                    # 1. Initialize OpenClaw session manager
                    # 2. Spawn actual AI agents using sessions_spawn
                    # 3. Coordinate real agent communication
                    # 4. Stream live results back to visualization
                    #
                    # Example (pseudocode):
                    # session = await openclaw.sessions_spawn(
                    #     agents=AGENT_CONFIGS,
                    #     task={"type": "research", "topic": topic}
                    # )
                    # async for event in session.stream():
                    #     await websocket.send(json.dumps(event))

            except json.JSONDecodeError:
                print(f"Invalid JSON received: {message}")
            except Exception as e:
                print(f"Error handling message: {e}")

    except websockets.exceptions.ConnectionClosed:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Client disconnected: {client_addr}")
    except Exception as e:
        print(f"Connection error: {e}")


async def main():
    """Start the WebSocket server"""
    host = "localhost"
    port = 8765

    print("=" * 60)
    print("SUBSTRATE WebSocket Server")
    print("=" * 60)
    print(f"Starting server on ws://{host}:{port}")
    print(f"Waiting for connections...")
    print()

    async with websockets.serve(handle_client, host, port):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer shutdown")
