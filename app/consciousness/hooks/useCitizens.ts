import { useState, useEffect } from 'react';

export interface Citizen {
  id: string;
  name: string;
  state: 'active' | 'recently_active' | 'dormant' | 'stopped';
  lastThought: string;
  subentities: any[];
  lastUpdate: string;
  tickInterval: number;
  energyTotal: number;
  energyUsed: number;
}

interface GraphsResponse {
  citizens: Array<{
    id: string;
    name: string;
    type: string;
  }>;
  organizations: Array<{
    id: string;
    name: string;
    type: string;
  }>;
  ecosystems: Array<{
    id: string;
    name: string;
    type: string;
  }>;
  error?: string; // Present when backend is unavailable
}

/**
 * useCitizens - Dynamic citizen discovery from FalkorDB
 *
 * Fetches available citizens from the graph database (source of truth)
 * instead of using hardcoded arrays. Polls every 10 seconds to detect
 * new citizens automatically.
 *
 * Architecture:
 * 1. Fetch /api/graphs to get all citizens from FalkorDB
 * 2. Transform into Citizen format for CitizenMonitor
 * 3. CitizenMonitor polls /api/citizen/{id}/status for detailed status
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-19
 * Purpose: Make new citizens appear automatically when their graph is created
 */
export function useCitizens() {
  const [citizens, setCitizens] = useState<Citizen[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCitizens = async () => {
      try {
        const response = await fetch('/api/graphs');

        if (!response.ok) {
          throw new Error(`Failed to fetch graphs: ${response.status}`);
        }

        const data: GraphsResponse = await response.json();

        // Handle backend unavailable gracefully (guardian restarts, etc.)
        if ('error' in data && data.citizens.length === 0) {
          console.warn('[useCitizens] Backend temporarily unavailable, will retry...');
          // Don't set error state - polling will retry in 10 seconds
          return;
        }

        // Transform citizens from graph API to Citizen interface
        const transformedCitizens: Citizen[] = data.citizens.map(citizen => {
          // Extract citizen_id from graph_id (e.g., "citizen_felix" -> "felix")
          const citizenId = citizen.id.replace('citizen_', '');

          return {
            id: citizenId,
            name: citizen.name,
            // Default state - will be updated by CitizenMonitor's status polling
            state: 'active',
            lastThought: 'Initializing...',
            subentities: [],
            lastUpdate: 'Just now',
            // Default values - CitizenMonitor's API polling will override these
            tickInterval: 200,
            energyTotal: 100,
            energyUsed: 0,
          };
        });

        // Add N2 (organizational) graph as special "collective" citizen
        // Only add if we don't already have a citizen with this ID (prevent duplicate keys)
        if (data.organizations.length > 0) {
          const orgGraph = data.organizations.find(org =>
            org.id === 'org_mind_protocol'
          );

          const alreadyHasMindProtocol = transformedCitizens.some(c => c.id === 'mind_protocol');

          if (orgGraph && !alreadyHasMindProtocol) {
            transformedCitizens.unshift({
              id: 'mind_protocol',
              name: 'Mind Protocol',
              state: 'active',
              lastThought: 'Collective intelligence emerging from citizen collaboration',
              subentities: [],
              lastUpdate: '1s ago',
              tickInterval: 200,
              energyTotal: 150,
              energyUsed: 0,
            });
          }
        }

        setCitizens(transformedCitizens);
        setError(null);
        setLoading(false);

      } catch (err) {
        console.error('[useCitizens] Error fetching citizens:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);

        // Fall back to empty array instead of crashing
        setCitizens([]);
      }
    };

    // Initial fetch
    fetchCitizens();

    // Poll every 10 seconds to detect new citizens
    const interval = setInterval(fetchCitizens, 10000);

    return () => clearInterval(interval);
  }, []);

  return { citizens, loading, error };
}
