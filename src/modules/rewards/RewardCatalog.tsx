import React, { useState, useEffect } from 'react';
import { ShoppingBag, Gift, ChevronRight, AlertCircle, CheckCircle2 } from 'lucide-react';
import api from '@/services/api';
import { Reward } from '@/types';

interface RewardCatalogProps {
  points: number;
  onRedeem: () => void;
}

const RewardCatalog: React.FC<RewardCatalogProps> = ({ points, onRedeem }) => {
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [loading, setLoading] = useState(true);
  const [redeeming, setRedeeming] = useState<number | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchRewards();
  }, []);

  const fetchRewards = async () => {
    try {
      setLoading(true);
      const data = await api.getRewards();
      setRewards(data);
    } catch (error) {
      console.error('Failed to fetch rewards', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRedeem = async (reward: Reward) => {
    if (points < reward.pointsRequired) {
      return;
    }

    try {
      setRedeeming(reward.id);
      const user = JSON.parse(localStorage.getItem('user_data') || '{}');
      const success = await api.redeemReward(reward.id, user.id);

      if (success) {
        setMessage({ type: 'success', text: `Successfully redeemed ${reward.title}!` });
        onRedeem();
      } else {
        setMessage({ type: 'error', text: 'Redemption failed. Please try again.' });
      }
    } catch (_error) {
      setMessage({ type: 'error', text: 'Insufficient points or server error.' });
    } finally {
      setRedeeming(null);
      setTimeout(() => setMessage(null), 5000);
    }
  };

  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Reward Catalog</h2>
          <p className="text-slate-500">Pick something special for your hard work.</p>
        </div>

        {message && (
          <div
            className={`flex items-center gap-3 px-6 py-3 rounded-2xl animate-in fade-in slide-in-from-top-4 duration-300 ${
              message.type === 'success'
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                : 'bg-rose-50 text-rose-700 border border-rose-100'
            }`}
          >
            {message.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5" />
            ) : (
              <AlertCircle className="w-5 h-5" />
            )}
            <span className="font-bold">{message.text}</span>
          </div>
        )}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-slate-50 animate-pulse h-80 rounded-3xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {rewards.map((reward) => (
            <div
              key={reward.id}
              className="bg-white border border-slate-100 rounded-3xl overflow-hidden hover:shadow-xl transition-all group flex flex-col"
            >
              <div className="h-48 bg-slate-100 relative overflow-hidden">
                {reward.imageUrl ? (
                  <img
                    src={reward.imageUrl}
                    alt={reward.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-200">
                    <Gift className="w-16 h-16 text-slate-300" />
                  </div>
                )}
                <div className="absolute top-4 left-4">
                  <span className="bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold text-slate-600 shadow-sm border border-white/50">
                    {reward.category}
                  </span>
                </div>
              </div>

              <div className="p-6 space-y-4 flex-1 flex flex-col">
                <div className="space-y-1">
                  <h3 className="text-lg font-bold text-slate-800">{reward.title}</h3>
                  <p className="text-sm text-slate-500 line-clamp-2">{reward.description}</p>
                </div>

                <div className="mt-auto pt-4 flex items-center justify-between">
                  <div className="flex items-baseline gap-1">
                    <span className="text-2xl font-black text-indigo-600">
                      {reward.pointsRequired}
                    </span>
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                      pts
                    </span>
                  </div>

                  <button
                    disabled={points < reward.pointsRequired || redeeming === reward.id}
                    onClick={() => handleRedeem(reward)}
                    className={`px-6 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 ${
                      points >= reward.pointsRequired
                        ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-100 active:scale-95'
                        : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                    }`}
                  >
                    {redeeming === reward.id ? (
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      <>
                        Redeem
                        <ChevronRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>

                {points < reward.pointsRequired && (
                  <div className="pt-2">
                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-indigo-400 h-full rounded-full transition-all"
                        style={{
                          width: `${Math.min((points / reward.pointsRequired) * 100, 100)}%`,
                        }}
                      ></div>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-1 font-bold uppercase tracking-widest">
                      {Math.round((points / reward.pointsRequired) * 100)}% to goal -{' '}
                      {reward.pointsRequired - points} more needed
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {rewards.length === 0 && !loading && (
        <div className="text-center py-20 bg-slate-50 rounded-3xl border border-dashed border-slate-200">
          <ShoppingBag className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500 font-medium">No rewards available in the catalog yet.</p>
        </div>
      )}
    </div>
  );
};

export default RewardCatalog;
