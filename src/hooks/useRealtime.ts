import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { RealtimePostgresChangesPayload } from '@supabase/supabase-js';

export function useRealtime<T = any>(table: string) {
  const [data, setData] = useState<T[]>([]);

  useEffect(() => {
    // Only subscribe if we have valid credentials
    if (!import.meta.env.VITE_SUPABASE_URL) {
      console.warn('Supabase URL missing. Real-time features disabled.');
      return;
    }

    const subscription = supabase
      .channel(`${table}_changes`)
      .on('postgres_changes', { event: '*', schema: 'public', table }, (payload: any) => {
        // Optimistic update for real-time feed
        setData((prev) => [...prev, payload.new as T]);
      })
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [table]);

  return data;
}
