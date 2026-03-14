# Substrate Demo

A live visualization of persistent agent identity + swarm coordination.

Built for Nebius.Build Hackathon — March 15, 2026.

## Concept

An agent with weeks of accumulated persistent memory orchestrates a research swarm in real-time. Watch agents spawn, specialize, coordinate, and synthesize — all visualized as a live neural map.

## Architecture

- **Frontend:** HTML Canvas real-time node graph visualization + WebSocket
- **Backend:** Python WebSocket server bridging to OpenClaw (ready for integration)
- **Agents:** Simulated swarm coordination with real-time visualization
- **Compute:** Designed for Nebius + OpenClaw deployment

## Quick Start

### Option 1: Demo Mode (No Installation)

Just open the file - it works standalone:

```bash
# Open in your browser
open index.html
# or
start index.html
# or just double-click index.html
```

Then click "Launch Swarm" and watch the visualization run in full demo mode.

### Option 2: Live Mode (With WebSocket Backend)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the WebSocket server:**
   ```bash
   python server.py
   ```

3. **Open the visualization:**
   ```bash
   open index.html
   ```

4. **Launch a swarm:**
   - The visualization will automatically connect to `ws://localhost:8765`
   - Mode indicator will show "LIVE" (green) instead of "DEMO" (cyan)
   - Enter a research topic and click "Launch Swarm"

## Files

- **`index.html`** - Complete visualization (single file, no dependencies, pure HTML/CSS/JS)
- **`server.py`** - WebSocket server for agent coordination
- **`requirements.txt`** - Python dependencies (just websockets)
- **`DEMO.md`** - 5-minute presentation script for hackathon demo

## Features

### Persistent Identity: Magnus
- Central node representing a persistent AI agent
- Memory rings showing accumulated knowledge layers
- Grows and learns across sessions (not ephemeral)

### Agent Swarm Coordination
- Spawn 5 specialized agents on demand:
  - **Atlas** (Research) - cyan
  - **Nova** (Analysis) - magenta
  - **Cipher** (Synthesis) - gold
  - **Echo** (Validation) - green
  - **Sage** (Research) - cyan
- Real-time coordination and connection visualization
- Live activity feed showing agent discoveries

### Visual Design
- Dark theme (#0a0a0f background)
- Neon accents (cyan, magenta, gold, green)
- 60fps canvas animation
- Smooth spawning, pulsing, and connection effects
- Particle flows along connection lines
- Memory rings that grow over time

### WebSocket Protocol

Messages are JSON with a `type` field:

```json
// Agent spawns
{"type": "agent_spawn", "id": "agent-0", "name": "Atlas", "role": "research", "color": "#00f0ff"}

// Agent discovers something
{"type": "agent_update", "id": "agent-0", "status": "researching", "finding": "Identified pattern..."}

// Agents connect
{"type": "agent_connect", "from": "agent-0", "to": "agent-1", "reason": "Sharing insights"}

// Agent completes
{"type": "agent_complete", "id": "agent-0", "result": "Research complete"}

// Synthesis
{"type": "synthesis", "text": "Collective findings: ..."}

// Memory update
{"type": "memory_update", "layer": "collaborative_research", "content": "quantum computing"}
```

## OpenClaw Integration (Placeholder)

The backend includes a placeholder for OpenClaw integration:

```python
# In server.py, the coordinator can be extended to:
# 1. Initialize OpenClaw session manager
# 2. Spawn actual AI agents using sessions_spawn
# 3. Coordinate real agent communication
# 4. Stream live results back to visualization
```

## Demo Presentation

See `DEMO.md` for the complete 5-minute presentation script including:
- Timing checkpoints
- Key talking points
- Visual cues to highlight
- Q&A preparation
- Emergency recovery plans

## Technical Details

**Frontend:**
- Pure HTML/CSS/JavaScript (no frameworks, no build tools)
- Canvas-based rendering for smooth 60fps animation
- WebSocket client with automatic fallback to demo mode
- Responsive design

**Backend:**
- Python 3.8+ with asyncio
- WebSocket server using `websockets` library
- Simulated agent coordination with realistic delays
- Ready for OpenClaw/Claude API integration

## Quality Bar

This demo meets conference-quality standards:
- ✨ Smooth animations, no jank
- 🎨 Professional visual design
- 🔌 Works standalone OR with backend
- 📱 Responsive layout
- ⚡ 60fps performance
- 🎯 Purpose-driven visual elements

## Use Cases

- **Research:** Spawn specialists for different aspects of complex topics
- **Code Review:** Spawn agents for security, performance, style, tests
- **Creative Work:** Spawn agents for ideation, critique, synthesis, polish
- **Any domain where coordination beats centralization**

## The Thesis

Traditional AI resets every session. **Substrate** provides:
1. **Persistent Identity** - Magnus remembers across sessions
2. **Swarm Coordination** - Spawn specialists that work in parallel
3. **Visual Transparency** - See what's happening in real-time
4. **Memory Accumulation** - Knowledge builds over time, not resets

This is how we move beyond disposable AI.

## License

MIT
