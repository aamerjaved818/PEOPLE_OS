import { useState, useEffect } from 'react';

interface PredictionData {
  month: string;
  actual: number | null;
  predicted: number | null;
}

interface PredictionsState {
  predictions: PredictionData[];
  confidence: number;
  loading: boolean;
}

const MOCK_DATA: PredictionData[] = [
  { month: 'Jan', actual: 4000, predicted: 4100 },
  { month: 'Feb', actual: 3000, predicted: 3200 },
  { month: 'Mar', actual: 2000, predicted: 2400 },
  { month: 'Apr', actual: 2780, predicted: 2900 },
  { month: 'May', actual: 1890, predicted: 1950 },
  { month: 'Jun', actual: 2390, predicted: 2400 },
  { month: 'Jul', actual: 3490, predicted: 3500 },
  { month: 'Aug', actual: null, predicted: 3800 },
  { month: 'Sep', actual: null, predicted: 4100 },
  { month: 'Oct', actual: null, predicted: 4300 },
];

export function usePredictions() {
  const [data, setData] = useState<PredictionsState>({
    predictions: [],
    confidence: 0,
    loading: true,
  });

  useEffect(() => {
    // Simulate API delay
    const timer = setTimeout(() => {
      setData({
        predictions: MOCK_DATA,
        confidence: 0.895, // 89.5%
        loading: false,
      });
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  return data;
}
