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

async function checkConsciousnessEngine(): Promise<ComponentStatus> {
  try {
    // Check for heartbeat file written by consciousness_engine.py every 10s
    const heartbeatPath = 'C:\\Users\\reyno\\mind-protocol\\.heartbeats\\consciousness_engine.heartbeat';

    if (!existsSync(heartbeatPath)) {
      return {
        name: 'Consciousness Engine',
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
        name: 'Consciousness Engine',
        status: 'running',
        details: `Last heartbeat ${Math.floor(ageSeconds)}s ago`,
      };
    } else {
      return {
        name: 'Consciousness Engine',
        status: 'stopped',
        details: `Stale heartbeat (${Math.floor(ageSeconds)}s old)`,
      };
    }
  } catch (error) {
    return {
      name: 'Consciousness Engine',
      status: 'error',
      details: 'Could not read heartbeat file',
    };
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

export async function GET() {
  try {
    const [falkorDB, engine, watcher, trace] = await Promise.all([
      checkFalkorDB(),
      checkConsciousnessEngine(),
      checkConversationWatcher(),
      checkTRACECapture(),
    ]);

    const components = [falkorDB, engine, watcher, trace];

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
