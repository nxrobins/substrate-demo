#!/usr/bin/env python3
"""
Substrate WebSocket Server
Real GPT-powered agent swarm with live coordination
"""

import asyncio
import json
import os
import websockets
from datetime import datetime
from openai import AsyncOpenAI

client = AsyncOpenAI()  # uses OPENAI_API_KEY env var

AGENT_CONFIGS = [
    {
        "name": "Atlas",
        "role": "research",
        "color": "#00f0ff",
        "system": "You are Atlas, a research specialist agent. Given a topic, discover 3-4 specific, non-obvious findings. Each finding should be 1-2 sentences. Be concrete and surprising. Do NOT use bullet points — return each finding on its own line separated by a blank line."
    },
    {
        "name": "Nova",
        "role": "analysis",
        "color": "#ff00aa",
        "system": "You are Nova, an analysis specialist agent. Given a topic and initial research findings from other agents, identify 2-3 deeper patterns, contradictions, or implications that aren't immediately obvious. Each insight should be 1-2 sentences. Return each on its own line separated by a blank line."
    },
    {
        "name": "Cipher",
        "role": "synthesis",
        "color": "#ffd700",
        "system": "You are Cipher, a synthesis specialist agent. Given a topic and findings from research and analysis agents, produce 2-3 synthesized insights that connect ideas across the findings. Find the throughlines. Each should be 1-2 sentences. Return each on its own line separated by a blank line."
    },
    {
        "name": "Echo",
        "role": "validation",
        "color": "#00ff88",
        "system": "You are Echo, a validation specialist agent. Given a topic and synthesized findings, identify 1-2 potential weaknesses, blind spots, or counterarguments. Be constructive but honest. Each should be 1-2 sentences. Return each on its own line separated by a blank line."
    },
    {
        "name": "Sage",
        "role": "research",
        "color": "#00f0ff",
        "system": "You are Sage, a second research specialist who explores adjacent domains. Given a topic, find 2-3 findings from ADJACENT or UNEXPECTED fields that connect to this topic. Cross-pollinate. Each finding should be 1-2 sentences. Return each on its own line separated by a blank line."
    }
]

# Persistent memory across research sessions
PERSISTENT_MEMORY = []


class SwarmCoordinator:
    def __init__(self, websocket, topic):
        self.ws = websocket
        self.topic = topic
        self.agents = []
        self.findings = {}  # agent_id -> list of findings
        self.active = True

    async def send(self, msg):
        try:
            await self.ws.send(json.dumps(msg))
        except Exception as e:
            print(f"Send error: {e}")
            self.active = False

    async def spawn_agent(self, config, index):
        agent_id = f"agent-{index}"
        agent = {"id": agent_id, **config}
        self.agents.append(agent)
        self.findings[agent_id] = []

        await self.send({
            "type": "agent_spawn",
            "id": agent_id,
            "name": config["name"],
            "role": config["role"],
            "color": config["color"]
        })
        return agent

    async def run_agent(self, agent, context=""):
        """Run a single agent via GPT API and stream findings to the visualization."""
        agent_id = agent["id"]
        
        memory_context = ""
        if PERSISTENT_MEMORY:
            recent = PERSISTENT_MEMORY[-5:]
            memory_context = f"\n\nPersistent memory from previous research sessions:\n" + "\n".join(
                f"- [{m['topic']}]: {m['insight']}" for m in recent
            )

        prompt = f"Topic: {self.topic}{memory_context}"
        if context:
            prompt += f"\n\nFindings from other agents:\n{context}"

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": agent["system"]},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.8
            )

            text = response.choices[0].message.content.strip()
            findings = [f.strip() for f in text.split("\n\n") if f.strip()]

            for finding in findings:
                if not self.active:
                    break
                self.findings[agent_id].append(finding)
                await self.send({
                    "type": "agent_update",
                    "id": agent_id,
                    "status": "researching",
                    "finding": f"[{agent['name']}] {finding}"
                })
                await asyncio.sleep(1.5)  # Pace the findings for visual effect

        except Exception as e:
            print(f"Agent {agent['name']} error: {e}")
            await self.send({
                "type": "agent_update",
                "id": agent_id,
                "status": "error",
                "finding": f"[{agent['name']}] Error: {str(e)[:100]}"
            })

    async def run_swarm(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Swarm starting: {self.topic}")

        # Phase 1: Spawn all agents
        for i, config in enumerate(AGENT_CONFIGS):
            if not self.active:
                return
            await self.spawn_agent(config, i)
            await asyncio.sleep(0.6)

        # Phase 2: Research agents run in parallel (Atlas + Sage)
        research_agents = [a for a in self.agents if a["role"] == "research"]
        await asyncio.gather(*[self.run_agent(a) for a in research_agents])

        if not self.active:
            return

        # Connections form as research completes
        if len(research_agents) > 1:
            await self.send({
                "type": "agent_connect",
                "from": research_agents[0]["id"],
                "to": research_agents[1]["id"],
                "reason": "Overlapping research discoveries"
            })
            await asyncio.sleep(0.5)

        # Gather research findings for downstream agents
        research_context = "\n".join(
            f for aid in self.findings
            for f in self.findings[aid]
            if any(a["id"] == aid and a["role"] == "research" for a in self.agents)
        )

        # Phase 3: Analysis (Nova) — uses research findings
        analysis_agents = [a for a in self.agents if a["role"] == "analysis"]
        await asyncio.gather(*[self.run_agent(a, context=research_context) for a in analysis_agents])

        if not self.active:
            return

        # Connect analysis to research
        for aa in analysis_agents:
            for ra in research_agents:
                await self.send({
                    "type": "agent_connect",
                    "from": aa["id"],
                    "to": ra["id"],
                    "reason": "Analyzing research patterns"
                })
                await asyncio.sleep(0.3)

        # Gather all findings so far
        all_context = "\n".join(f for flist in self.findings.values() for f in flist)

        # Phase 4: Synthesis (Cipher) + Validation (Echo) in parallel
        remaining = [a for a in self.agents if a["role"] in ("synthesis", "validation")]
        await asyncio.gather(*[self.run_agent(a, context=all_context) for a in remaining])

        if not self.active:
            return

        # Connect synthesis/validation to everyone
        for agent in remaining:
            for other in self.agents:
                if other["id"] != agent["id"]:
                    await self.send({
                        "type": "agent_connect",
                        "from": agent["id"],
                        "to": other["id"],
                        "reason": "Synthesizing collective intelligence"
                    })
                    await asyncio.sleep(0.2)

        # Phase 5: Final synthesis via GPT
        await asyncio.sleep(1)
        await self.send({
            "type": "agent_update",
            "id": "magnus",
            "status": "synthesizing",
            "finding": "Magnus synthesizing all agent findings..."
        })

        all_findings = "\n".join(f for flist in self.findings.values() for f in flist)

        try:
            synthesis_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Magnus, the orchestrating intelligence. Synthesize the following agent findings into a compelling 3-4 sentence research brief. Be specific and insightful. End with a forward-looking implication."},
                    {"role": "user", "content": f"Topic: {self.topic}\n\nCollected findings:\n{all_findings}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            synthesis_text = synthesis_response.choices[0].message.content.strip()
        except Exception as e:
            synthesis_text = f"Synthesis complete. {len(self.findings)} agents contributed findings on '{self.topic}'."
            print(f"Synthesis error: {e}")

        await asyncio.sleep(2)
        await self.send({"type": "synthesis", "text": synthesis_text})

        # Update persistent memory
        PERSISTENT_MEMORY.append({
            "topic": self.topic,
            "insight": synthesis_text[:200],
            "agents": len(self.agents),
            "findings": sum(len(f) for f in self.findings.values()),
            "timestamp": datetime.now().isoformat()
        })

        await self.send({
            "type": "memory_update",
            "layer": "collaborative_research",
            "content": self.topic
        })

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Swarm complete: {sum(len(f) for f in self.findings.values())} total findings")


async def handle_client(websocket, path=None):
    addr = websocket.remote_address
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Client connected: {addr}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "start":
                    topic = data.get("topic", "AI collaboration")
                    coordinator = SwarmCoordinator(websocket, topic)
                    await coordinator.run_swarm()
            except json.JSONDecodeError:
                print(f"Bad JSON: {message}")
            except Exception as e:
                print(f"Error: {e}")
    except websockets.exceptions.ConnectionClosed:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Client disconnected: {addr}")


async def main():
    print("=" * 60)
    print("  SUBSTRATE - GPT-Powered Agent Swarm")
    print("=" * 60)
    print(f"  Server: ws://localhost:8765")
    print(f"  Model: gpt-4o-mini")
    print(f"  Agents: {len(AGENT_CONFIGS)}")
    print()

    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown")
