import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';

const execAsync = promisify(exec);

interface ComponentStatus {
  name: string;
  status: 'running' | 'stopped' | 'error';
  details: string;
  pid?: number;
  uptime?: string;
}

async function checkFalkorDB(): Promise<ComponentStatus> {
  try {
    // Check FalkorDB via Docker container
    const { stdout } = await execAsync('docker exec mind_protocol_falkordb redis-cli ping');
    const isRunning = stdout.trim() === 'PONG';

    return {
      name: 'FalkorDB',
      status: isRunning ? 'running' : 'stopped',
      details: isRunning ? 'Healthy' : 'Not responding',
    };
  } catch (error) {
    return {
      name: 'FalkorDB',
      status: 'error',
      details: 'Docker container not found or not running',
    };
  }
}

async function checkConsciousnessMechanisms(): Promise<ComponentStatus[]> {
  try {
    // Check for heartbeat file written by websocket_server every 60s
    const heartbeatPath = 'C:\\Users\\reyno\\mind-protocol\\.heartbeats\\consciousness_engine.heartbeat';

    if (!existsSync(heartbeatPath)) {
      return [{
        name: 'Consciousness Mechanisms',
        status: 'stopped',
        details: 'No heartbeat file found',
      }];
    }

    const stats = await readFile(heartbeatPath, 'utf-8');
    const heartbeatData = JSON.parse(stats);
    const lastBeat = new Date(heartbeatData.timestamp);
    const now = new Date();
    const ageSeconds = (now.getTime() - lastBeat.getTime()) / 1000;

    // Check if heartbeat is stale
    if (ageSeconds > 120) {
      return [{
        name: 'Consciousness Mechanisms',
        status: 'stopped',
        details: `Stale heartbeat (${Math.floor(ageSeconds)}s old)`,
      }];
    }

    // Count running engines
    const engines = heartbeatData.engines || {};
    const runningCount = Object.values(engines).filter((e: any) => e.running).length;

    // Return individual mechanism statuses
    const mechanismStatus = runningCount > 0 ? 'running' : 'stopped';

    return [
      {
        name: 'Energy Diffusion',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
      {
        name: 'Energy Decay',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
      {
        name: 'Link Strengthening',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
      {
        name: 'Threshold Activation',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
      {
        name: 'Workspace Selection',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
    ];
  } catch (error) {
    return [{
      name: 'Consciousness Mechanisms',
      status: 'error',
      details: 'Could not read heartbeat file',
    }];
  }
}

async function checkConversationWatcher(): Promise<ComponentStatus> {
  try {
    // Check for heartbeat file written by conversation_watcher.py every 10s
    const heartbeatPath = 'C:\\Users\\reyno\\mind-protocol\\.heartbeats\\conversation_watcher.heartbeat';

    if (!existsSync(heartbeatPath)) {
      return {
        name: 'Conversation Watcher',
        status: 'stopped',
        details: 'No heartbeat file found',
      };
    }

    const stats = await readFile(heartbeatPath, 'utf-8');
    const heartbeatData = JSON.parse(stats);
    const lastBeat = new Date(heartbeatData.timestamp);
    const now = new Date();
    const ageSeconds = (now.getTime() - lastBeat.getTime()) / 1000;

    if (ageSeconds < 30) {
      return {
        name: 'Conversation Watcher',
        status: 'running',
        details: `Monitoring conversations (${Math.floor(ageSeconds)}s ago)`,
      };
    } else {
      return {
        name: 'Conversation Watcher',
        status: 'stopped',
        details: `Stale heartbeat (${Math.floor(ageSeconds)}s old)`,
      };
    }
  } catch (error) {
    return {
      name: 'Conversation Watcher',
      status: 'error',
      details: 'Could not read heartbeat file',
    };
  }
}

async function checkTRACECapture(): Promise<ComponentStatus> {
  try {
    // TRACE capture is part of conversation_watcher
    // If conversation_watcher is running, TRACE is active
    const watcherStatus = await checkConversationWatcher();

    if (watcherStatus.status === 'running') {
      return {
        name: 'TRACE Format Capture',
        status: 'running',
        details: 'Dual learning mode operational',
      };
    } else {
      return {
        name: 'TRACE Format Capture',
        status: watcherStatus.status,
        details: watcherStatus.status === 'stopped' ? 'Inactive' : 'Error',
      };
    }
  } catch (error) {
    return {
      name: 'TRACE Format Capture',
      status: 'error',
      details: 'Status check failed',
    };
  }
}

async function checkStimulusInjection(): Promise<ComponentStatus> {
  try {
    // Check for heartbeat file written by stimulus_injection_service.py
    const heartbeatPath = 'C:\\Users\\reyno\\mind-protocol\\orchestration\\services\\.heartbeats\\stimulus_injection.heartbeat';

    if (!existsSync(heartbeatPath)) {
      return {
        name: 'Stimulus Injection',
        status: 'stopped',
        details: 'No heartbeat file found',
      };
    }

    const stats = await readFile(heartbeatPath, 'utf-8');
    const heartbeatData = JSON.parse(stats);
    const lastBeat = new Date(heartbeatData.timestamp);
    const now = new Date();
    const ageSeconds = (now.getTime() - lastBeat.getTime()) / 1000;

    if (ageSeconds < 30) {
      return {
        name: 'Stimulus Injection',
        status: 'running',
        details: `Service active (${Math.floor(ageSeconds)}s ago)`,
      };
    } else {
      return {
        name: 'Stimulus Injection',
        status: 'stopped',
        details: `Stale heartbeat (${Math.floor(ageSeconds)}s old)`,
      };
    }
  } catch (error) {
    return {
      name: 'Stimulus Injection',
      status: 'error',
      details: 'Could not read heartbeat file',
    };
  }
}

async function checkAutonomyOrchestrator(): Promise<ComponentStatus> {
  try {
    // Check for heartbeat file written by autonomy_orchestrator.py
    const heartbeatPath = 'C:\\Users\\reyno\\mind-protocol\\orchestration\\services\\.heartbeats\\autonomy_orchestrator.heartbeat';

    if (!existsSync(heartbeatPath)) {
      return {
        name: 'Autonomy Orchestrator',
        status: 'stopped',
        details: 'No heartbeat file found',
      };
    }

    const stats = await readFile(heartbeatPath, 'utf-8');
    const heartbeatData = JSON.parse(stats);
    const lastBeat = new Date(heartbeatData.timestamp);
    const now = new Date();
    const ageSeconds = (now.getTime() - lastBeat.getTime()) / 1000;

    if (ageSeconds < 30) {
      return {
        name: 'Autonomy Orchestrator',
        status: 'running',
        details: `Service active (${Math.floor(ageSeconds)}s ago)`,
      };
    } else {
      return {
        name: 'Autonomy Orchestrator',
        status: 'stopped',
        details: `Stale heartbeat (${Math.floor(ageSeconds)}s old)`,
      };
    }
  } catch (error) {
    return {
      name: 'Autonomy Orchestrator',
      status: 'error',
      details: 'Could not read heartbeat file',
    };
  }
}

export async function GET() {
  try {
    const [falkorDB, mechanisms, watcher, trace, stimulus, autonomy] = await Promise.all([
      checkFalkorDB(),
      checkConsciousnessMechanisms(),
      checkConversationWatcher(),
      checkTRACECapture(),
      checkStimulusInjection(),
      checkAutonomyOrchestrator(),
    ]);

    // Flatten mechanisms array (it returns multiple ComponentStatus objects)
    const components = [falkorDB, ...mechanisms, watcher, trace, stimulus, autonomy];

    // Overall system health
    const allRunning = components.every(c => c.status === 'running');
    const anyError = components.some(c => c.status === 'error');

    return NextResponse.json({
      overall: allRunning ? 'healthy' : anyError ? 'degraded' : 'partial',
      components,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to check system status', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
