import React, { useState, useEffect } from 'react';
import { Trophy, Heart, Star, ShoppingBag, TrendingUp } from 'lucide-react';
import api from '@/services/api';
import { RewardPoint } from '@/types';
import RecognitionFeed from './RecognitionFeed';
import RewardCatalog from './RewardCatalog';
import UserWallet from './UserWallet';

const RewardsModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'recognition' | 'rewards' | 'wallet'>('recognition');
  const [wallet, setWallet] = useState<RewardPoint | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      const user = JSON.parse(localStorage.getItem('user_data') || '{}');
      if (user.id) {
        const pointData = await api.getRewardPoints(user.id);
        setWallet(pointData);
      }
    } catch (error) {
      console.error('Failed to fetch rewards data', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header & Wallet Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-indigo-600 to-purple-600 p-8 rounded-3xl text-white shadow-xl overflow-hidden relative">
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <Trophy className="w-8 h-8 text-yellow-300" />
            Rewards & Recognition
          </h1>
          <p className="text-indigo-100 max-w-md">
            Celebrate wins, recognize your peers, and redeem points for exclusive rewards.
          </p>
        </div>

        <div className="relative z-10 bg-white/10 backdrop-blur-md p-6 rounded-2xl border border-white/20 flex items-center gap-6">
          <div className="h-16 w-16 bg-yellow-400 rounded-full flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform">
            <Star className="w-8 h-8 text-indigo-900 fill-current" />
          </div>
          <div>
            <p className="text-sm font-medium text-indigo-100 uppercase tracking-wider">
              Your Balance
            </p>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-black">{wallet?.balance ?? 0}</span>
              <span className="text-lg font-bold text-yellow-300">pts</span>
            </div>
          </div>
        </div>

        {/* Abstract background shapes */}
        <div className="absolute -top-12 -right-12 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-8 -left-8 w-48 h-48 bg-purple-400/20 rounded-full blur-2xl"></div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex p-1 bg-slate-100 rounded-2xl w-fit">
        <button
          onClick={() => setActiveTab('recognition')}
          className={`px-8 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === 'recognition'
              ? 'bg-white text-indigo-600 shadow-md'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          <Heart className="w-5 h-5" />
          Recognition Feed
        </button>
        <button
          onClick={() => setActiveTab('rewards')}
          className={`px-8 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === 'rewards'
              ? 'bg-white text-indigo-600 shadow-md'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          <ShoppingBag className="w-5 h-5" />
          Reward Catalog
        </button>
        <button
          onClick={() => setActiveTab('wallet')}
          className={`px-8 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
            activeTab === 'wallet'
              ? 'bg-white text-indigo-600 shadow-md'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          <TrendingUp className="w-5 h-5" />
          My Points
        </button>
      </div>

      {/* Content Area */}
      <div className="bg-white rounded-3xl shadow-sm border border-slate-100 min-h-[600px] overflow-hidden">
        {activeTab === 'recognition' && <RecognitionFeed onRecognitionSent={fetchUserData} />}
        {activeTab === 'rewards' && (
          <RewardCatalog points={wallet?.balance ?? 0} onRedeem={fetchUserData} />
        )}
        {activeTab === 'wallet' && <UserWallet wallet={wallet} />}
      </div>
    </div>
  );
};

export default RewardsModule;
