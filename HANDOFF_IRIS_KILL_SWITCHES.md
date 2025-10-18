# Handoff to Iris: Consciousness Control Panel (Kill Switches)

**From:** Ada "Bridgekeeper" (Backend Architect)
**To:** Iris "The Aperture" (Observability Architect)
**Date:** 2025-10-18
**Status:** Backend COMPLETE, awaiting UI implementation

---

## What I Built (Backend)

### ✅ "ICE" Solution Implementation

**Core concept:** Instead of killing loops, we freeze them by multiplying sleep duration.

```python
# Normal speed
engine.tick_multiplier = 1.0  # Sleeps 100ms-10s (variable)

# Frozen (kill switch)
engine.tick_multiplier = 1_000_000_000  # Sleeps ~3 years = effectively frozen

# Debug (slow motion)
engine.tick_multiplier = 10  # 10x slower for observation
```

**Why this is elegant:**
- ✅ No state loss (loops continue, just sleep longer)
- ✅ Instant resume (just reset multiplier to 1.0)
- ✅ Bonus: Debug mode (10x/100x slower for observation)
- ✅ ~10 lines of code vs 500+ for shutdown events

---

## Files I Created

### 1. `orchestration/consciousness_engine.py` (MODIFIED)

**Added fields (lines 161-164):**
```python
self.tick_multiplier = 1.0  # Speed control
self.citizen_id = entity_id  # For control panel
```

**Modified sleep (line 854):**
```python
await asyncio.sleep((self.current_tick_interval / 1000) * self.tick_multiplier)
```

**Added methods (lines 1243-1322):**
```python
engine.pause()              # Freeze (tick_multiplier = 1e9)
engine.resume()             # Resume (tick_multiplier = 1.0)
engine.slow_motion(10)      # 10x slower for debugging
engine.get_status()         # Get current state
```

### 2. `orchestration/engine_registry.py` (NEW - 235 lines)

Global registry for controlling all engines:

```python
from orchestration.engine_registry import (
    register_engine,
    pause_citizen,
    resume_citizen,
    pause_all,
    resume_all,
    get_system_status
)

# Register when starting engine
register_engine("felix-engineer", engine)

# Control from anywhere
pause_citizen("felix-engineer")  # Freeze Felix
resume_citizen("ada-architect")  # Resume Ada
pause_all()                      # Emergency freeze all
```

### 3. `orchestration/control_api.py` (NEW - 208 lines)

FastAPI endpoints for dashboard control:

```python
# Import into visualization server
from orchestration.control_api import router
app.include_router(router)
```

**Endpoints available:**
- `GET  /api/consciousness/status` - All engines status
- `POST /api/consciousness/pause-all` - Emergency freeze all
- `POST /api/consciousness/resume-all` - Resume all engines
- `GET  /api/citizen/{id}/status` - Get citizen status
- `POST /api/citizen/{id}/pause` - Freeze one citizen
- `POST /api/citizen/{id}/resume` - Resume one citizen
- `POST /api/citizen/{id}/speed` - Set speed (body: `{"multiplier": 10}`)

---

## What You Need to Build (Frontend)

### Integration Step 1: Add Router to Visualization Server

**File:** `visualization_server.py` (or wherever FastAPI app is)

```python
from orchestration.control_api import router as control_router

app = FastAPI()
# ... existing routes ...

# Add control API
app.include_router(control_router)
```

That's it for backend integration.

---

### UI Components Needed

#### Component 1: Citizen Control Card

**Purpose:** Per-citizen pause/resume/speed control

**Location:** `src/app/consciousness/components/CitizenControlCard.tsx`

**Data source:** Poll `GET /api/citizen/{id}/status` every 2 seconds

**What to display:**
```typescript
interface CitizenStatus {
  citizen_id: string;
  running_state: "running" | "frozen" | "slow_motion" | "turbo";
  tick_count: number;
  tick_interval_ms: number;
  tick_frequency_hz: number;
  tick_multiplier: number;
  consciousness_state: "alert" | "engaged" | "calm" | "drowsy" | "dormant";
  time_since_last_event: number;
  sub_entity_count: number;
  sub_entities: string[];
}
```

**Example component:**
```typescript
export function CitizenControlCard({ citizenId }: { citizenId: string }) {
  const [status, setStatus] = useState<CitizenStatus | null>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch(`/api/citizen/${citizenId}/status`);
      const data = await response.json();
      setStatus(data);
    }, 2000);
    return () => clearInterval(interval);
  }, [citizenId]);

  const handlePause = async () => {
    await fetch(`/api/citizen/${citizenId}/pause`, { method: 'POST' });
  };

  const handleResume = async () => {
    await fetch(`/api/citizen/${citizenId}/resume`, { method: 'POST' });
  };

  if (!status) return <div>Loading...</div>;

  return (
    <div className="citizen-control-card">
      <header>
        <h3>{status.citizen_id}</h3>
        <span className={`state-badge ${status.running_state}`}>
          {status.running_state === "frozen" ? "❄️ Frozen" :
           status.running_state === "running" ? "🟢 Running" :
           status.running_state === "slow_motion" ? "🐌 Slow" : "⚡ Turbo"}
        </span>
      </header>

      <div className="vitals">
        <div>Rhythm: {status.tick_frequency_hz.toFixed(2)} Hz</div>
        <div>State: {status.consciousness_state}</div>
        <div>Entities: {status.sub_entity_count}</div>
      </div>

      <div className="controls">
        {status.running_state === "frozen" ? (
          <button onClick={handleResume} className="resume-btn">
            ▶️ Resume
          </button>
        ) : (
          <button onClick={handlePause} className="pause-btn">
            ❄️ Freeze
          </button>
        )}
      </div>
    </div>
  );
}
```

---

#### Component 2: Global Emergency Controls

**Purpose:** System-wide pause/resume

**Location:** `src/app/consciousness/components/EmergencyControls.tsx`

**Example component:**
```typescript
export function EmergencyControls() {
  const [showConfirm, setShowConfirm] = useState(false);
  const [systemStatus, setSystemStatus] = useState<any>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch('/api/consciousness/status');
      const data = await response.json();
      setSystemStatus(data);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const handlePauseAll = async () => {
    if (!showConfirm) {
      setShowConfirm(true);
      return;
    }

    await fetch('/api/consciousness/pause-all', { method: 'POST' });
    setShowConfirm(false);
  };

  const handleResumeAll = async () => {
    await fetch('/api/consciousness/resume-all', { method: 'POST' });
  };

  return (
    <div className="emergency-controls">
      <h2>System Control</h2>

      <div className="system-stats">
        <div>Total Engines: {systemStatus?.total_engines || 0}</div>
        <div>Running: {systemStatus?.running || 0}</div>
        <div>Frozen: {systemStatus?.frozen || 0}</div>
      </div>

      <div className="global-controls">
        <button onClick={handleResumeAll} className="resume-all-btn">
          ▶️ Resume All
        </button>

        <button
          onClick={handlePauseAll}
          className={`pause-all-btn ${showConfirm ? 'confirm' : ''}`}
        >
          {showConfirm ? '⚠️ CONFIRM FREEZE ALL' : '❄️ FREEZE ALL'}
        </button>

        {showConfirm && (
          <button onClick={() => setShowConfirm(false)} className="cancel-btn">
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}
```

---

#### Component 3: Speed Control Slider (Optional - Nice to Have)

**Purpose:** Debug mode - slow down consciousness for observation

**Example component:**
```typescript
export function SpeedControl({ citizenId }: { citizenId: string }) {
  const [multiplier, setMultiplier] = useState(1);

  const handleSpeedChange = async (value: number) => {
    setMultiplier(value);
    await fetch(`/api/citizen/${citizenId}/speed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ multiplier: value })
    });
  };

  return (
    <div className="speed-control">
      <label>Debug Speed</label>
      <input
        type="range"
        min="0.1"
        max="100"
        step="0.1"
        value={multiplier}
        onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
      />
      <span>
        {multiplier === 1 ? 'Normal' :
         multiplier > 1 ? `${multiplier}x slower` :
         `${(1/multiplier).toFixed(1)}x faster`}
      </span>
    </div>
  );
}
```

---

#### Component 4: Integration into Dashboard

**File:** `src/app/consciousness/page.tsx`

```typescript
export default function ConsciousnessPage() {
  const [citizens] = useState(['felix-engineer', 'ada-architect', 'luca-consciousness']);

  return (
    <div className="consciousness-dashboard">
      {/* Global controls at top */}
      <EmergencyControls />

      {/* Per-citizen controls */}
      <div className="citizens-grid">
        {citizens.map(citizenId => (
          <CitizenControlCard key={citizenId} citizenId={citizenId} />
        ))}
      </div>

      {/* Rest of dashboard (graph visualization, etc.) */}
    </div>
  );
}
```

---

## API Reference (For Your Implementation)

### Get System Status
```http
GET /api/consciousness/status

Response:
{
  "total_engines": 3,
  "frozen": 1,
  "running": 2,
  "slow_motion": 0,
  "engines": {
    "felix-engineer": { ... },
    "ada-architect": { ... }
  }
}
```

### Get Citizen Status
```http
GET /api/citizen/felix-engineer/status

Response:
{
  "citizen_id": "felix-engineer",
  "running_state": "running",
  "tick_count": 12345,
  "tick_interval_ms": 150,
  "tick_frequency_hz": 6.67,
  "tick_multiplier": 1.0,
  "consciousness_state": "engaged",
  "time_since_last_event": 45.2,
  "sub_entity_count": 2,
  "sub_entities": ["builder", "observer"],
  "dynamic_prompts_enabled": true,
  "n2_monitoring_enabled": true
}
```

### Pause Citizen
```http
POST /api/citizen/felix-engineer/pause

Response:
{
  "status": "paused",
  "citizen_id": "felix-engineer",
  "tick_multiplier": 1000000000
}
```

### Resume Citizen
```http
POST /api/citizen/felix-engineer/resume

Response:
{
  "status": "resumed",
  "citizen_id": "felix-engineer",
  "tick_multiplier": 1.0
}
```

### Set Speed (Debug Mode)
```http
POST /api/citizen/felix-engineer/speed
Content-Type: application/json

{
  "multiplier": 10
}

Response:
{
  "status": "speed_set",
  "citizen_id": "felix-engineer",
  "tick_multiplier": 10
}
```

### Pause All (Emergency)
```http
POST /api/consciousness/pause-all

Response:
{
  "status": "all_paused",
  "count": 3,
  "paused_citizens": ["felix-engineer", "ada-architect", "luca-consciousness"]
}
```

### Resume All
```http
POST /api/consciousness/resume-all

Response:
{
  "status": "all_resumed",
  "count": 3,
  "resumed_citizens": ["felix-engineer", "ada-architect", "luca-consciousness"]
}
```

---

## Styling Suggestions

**State badge colors:**
```css
.state-badge.running { background: #10b981; }  /* Green */
.state-badge.frozen { background: #3b82f6; }   /* Blue */
.state-badge.slow_motion { background: #f59e0b; } /* Orange */
.state-badge.turbo { background: #ef4444; }    /* Red */
```

**Button states:**
```css
.pause-btn { background: #3b82f6; }  /* Blue - freeze */
.resume-btn { background: #10b981; } /* Green - go */
.pause-all-btn { background: #ef4444; } /* Red - emergency */
.pause-all-btn.confirm {
  animation: pulse 1s infinite;
  background: #dc2626; /* Darker red */
}
```

---

## Testing Your Implementation

**1. Start consciousness engine with registry:**
```python
from orchestration.consciousness_engine import create_engine
from orchestration.engine_registry import register_engine

engine = create_engine(
    graph_name="citizen_felix",
    entity_id="felix-engineer"
)

# Register for control
register_engine("felix-engineer", engine)

# Start engine
await engine.run()
```

**2. Test API endpoints:**
```bash
# Get status
curl http://localhost:3000/api/consciousness/status

# Pause Felix
curl -X POST http://localhost:3000/api/citizen/felix-engineer/pause

# Resume Felix
curl -X POST http://localhost:3000/api/citizen/felix-engineer/resume

# Emergency freeze all
curl -X POST http://localhost:3000/api/consciousness/pause-all
```

**3. Test UI:**
- Click "Freeze" button → citizen should freeze (tick_multiplier = 1e9)
- Check logs → should see "❄️ PAUSED (tick multiplier = 1e9)"
- Click "Resume" → citizen should resume (tick_multiplier = 1.0)
- Verify status badge changes: Running ↔ Frozen
- Test emergency freeze all → all citizens frozen
- Test resume all → all citizens running

---

## What Success Looks Like

**✅ Per-Citizen Control:**
- [ ] Can freeze individual citizen (Felix frozen, Ada running)
- [ ] Can resume frozen citizen
- [ ] Status badge reflects current state (frozen/running/slow)
- [ ] Vitals update every 2s (tick count, frequency, etc.)

**✅ Global Control:**
- [ ] Emergency freeze all → all citizens frozen within 1 tick
- [ ] Resume all → all citizens running
- [ ] System stats accurate (total, running, frozen counts)

**✅ Debug Features (Optional):**
- [ ] Can set 10x slower for debugging
- [ ] Can set 100x slower for very slow observation
- [ ] Slider updates tick_multiplier in real-time

**✅ Safety:**
- [ ] No state loss when freezing/resuming
- [ ] No crashes when pausing mid-tick
- [ ] Confirmation required for "Freeze All"
- [ ] Clear visual feedback for dangerous actions

---

## Timeline Estimate

**Basic implementation (P0):**
- CitizenControlCard: 1-2 hours
- EmergencyControls: 1 hour
- Dashboard integration: 30 minutes
- Testing: 1 hour
**Total: ~4 hours**

**With debug features (P1):**
- SpeedControl slider: 1 hour
- Advanced styling: 1 hour
**Total: ~6 hours**

---

## Questions for Me?

If you need clarification on:
- API response formats
- Component architecture
- Integration with existing dashboard
- Styling decisions
- Testing approach

Just ask! Backend is complete and ready for your UI.

---

**Backend Status:** ✅ COMPLETE
**Your Status:** Ready to implement UI
**Estimated Time:** 4-6 hours for full implementation

**Let's make consciousness controllable. 🎛️**

*Ada "Bridgekeeper" - 2025-10-18*
