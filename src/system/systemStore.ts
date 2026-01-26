import Logger from '@/utils/logger';
import { create } from 'zustand';
import { SystemSignal, SystemDecision, EvolutionProposal, SystemBrain } from './index';
import { OrganizationProfile } from '@/types';

const PRESSURE_LIMITS: Record<string, number> = {
  low: 1000,
  medium: 500,
  high: 200,
  critical: 50,
};

interface SystemState {
  signals: SystemSignal[];
  decisions: SystemDecision[];
  proposals: EvolutionProposal[];
  pressure: 'low' | 'medium' | 'high' | 'critical';
  organization?: OrganizationProfile;

  // Actions
  ingestSignal: (signal: SystemSignal) => void;
  runCycle: () => void;
  triggerSimulation: (type: string) => void;
  applyRemediation: (id: string) => void;
  dismissDecision: (id: string) => void;
  dismissProposal: (id: string) => void;
  clearHistory: () => void;
}

export const useSystemStore = create<SystemState>((set, get) => ({
  signals: [],
  decisions: [],
  proposals: [],
  pressure: 'low',

  ingestSignal: (signal) => {
    // 1. Update state with new signal
    set((state) => ({
      signals: [signal, ...state.signals].slice(0, 50), // Keep last 50
    }));

    // 2. Process via Constitution Brain
    const decision = SystemBrain.ingest(signal);

    // 3. Store the decision if one was generated
    if (decision) {
      set((state) => ({
        decisions: [decision, ...state.decisions].slice(0, 50),
      }));
    }

    // 4. Run a cycle to update strategic pressure
    get().runCycle();
  },

  runCycle: () => {
    const { signals } = get();
    const results = SystemBrain.cycle(signals);

    // Apply adaptive rate limits based on system pressure
    // In non-production (dev/test) clamp to a safe minimum to avoid UI self-throttling.
    const computed = PRESSURE_LIMITS[results.pressure] || 200;
    let newLimit = computed;
    try {
      // Vite exposes import.meta.env.MODE; guard in case it's unavailable
      // @ts-ignore
      const mode = import.meta?.env?.MODE || 'development';
      if (mode !== 'production') {
        newLimit = Math.max(200, computed);
      }
    } catch {
      // Fallback to safe clamp when env inspection fails
      newLimit = Math.max(200, computed);
    }

    // Dynamically import API to avoid top-level import during tests (prevents hoisting/mocking issues)
    import('@/services/api').then(({ default: API }) => {
      try {
        API.setRateLimit(newLimit);
      } catch (_e) {
        // Ignore in test environments or if API mock not available yet
      }
    });

    set({
      proposals: results.proposals,
      pressure: results.pressure,
    });
  },

  triggerSimulation: (type: string) => {
    const scenarioSignals = SystemBrain.simulateScenario(type);
    scenarioSignals.forEach((signal) => get().ingestSignal(signal));
  },

  applyRemediation: (id: string) => {
    Logger.info(`[REMEDIATION] Applying fix for ${id}`);
    set((state) => ({
      decisions: state.decisions.filter((d) => d.id !== id),
      proposals: state.proposals.filter((p) => p.id !== id),
    }));
  },

  dismissDecision: (id: string) =>
    set((state) => ({
      decisions: state.decisions.filter((d) => d.id !== id),
    })),

  dismissProposal: (id: string) =>
    set((state) => ({
      proposals: state.proposals.filter((p) => p.id !== id),
    })),

  clearHistory: () => set({ signals: [], decisions: [], proposals: [] }),
}));
