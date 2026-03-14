# Substrate Demo

A live visualization of persistent agent identity + swarm coordination.

Built for Nebius.Build Hackathon — March 15, 2026.

## Concept

An agent with weeks of accumulated persistent memory orchestrates a research swarm in real-time. Watch agents spawn, specialize, coordinate, and synthesize — all visualized as a live neural map.

## Architecture

- **Frontend:** HTML Canvas real-time node graph visualization + WebSocket
- **Backend:** Python FastAPI WebSocket server bridging to OpenClaw
- **Agents:** OpenClaw agent spawning with persistent memory
- **Compute:** Nebius serverless GPU (hackathon)
