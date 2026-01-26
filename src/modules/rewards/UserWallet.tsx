import React, { useState, useEffect } from 'react';
import { ArrowUpCircle, ArrowDownCircle, History, Target, Wallet } from 'lucide-react';
import { RewardPoint, RewardPointTransaction } from '@/types';
import api from '@/services/api';

interface UserWalletProps {
  wallet: RewardPoint | null;
}

const UserWallet: React.FC<UserWalletProps> = ({ wallet }) => {
  const [transactions, setTransactions] = useState<RewardPointTransaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const user = JSON.parse(localStorage.getItem('user_data') || '{}');
      if (user.id) {
        const data = await api.getRewardTransactions(user.id);
        setTransactions(data);
      }
    } catch (error) {
      console.error('Failed to fetch reward transactions', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      label: 'Total Earned',
      value: wallet?.totalEarned ?? 0,
      icon: ArrowUpCircle,
      color: 'text-emerald-500',
      bg: 'bg-emerald-50',
    },
    {
      label: 'Total Redeemed',
      value: wallet?.totalRedeemed ?? 0,
      icon: ArrowDownCircle,
      color: 'text-rose-500',
      bg: 'bg-rose-50',
    },
    {
      label: 'Current Balance',
      value: wallet?.balance ?? 0,
      icon: Wallet,
      color: 'text-indigo-500',
      bg: 'bg-indigo-50',
    },
  ];

  return (
    <div className="p-8 space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">My Point Wallet</h2>
        <p className="text-slate-500">Track your earnings and redemptions performance.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-white border border-slate-100 p-8 rounded-3xl flex items-center gap-6 hover:shadow-lg transition-all"
          >
            <div className={`h-16 w-16 ${stat.bg} rounded-2xl flex items-center justify-center`}>
              <stat.icon className={`w-8 h-8 ${stat.color}`} />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">
                {stat.label}
              </p>
              <p className="text-3xl font-black text-slate-800">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Progress & Targets */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-slate-50 p-8 rounded-3xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Target className="w-5 h-5 text-indigo-600" />
              Earning Insights
            </h3>

            <div className="space-y-6">
              <div>
                <div className="flex justify-between items-end mb-2">
                  <span className="text-sm font-bold text-slate-600">Quarterly Goal</span>
                  <span className="text-xs font-bold text-indigo-600">
                    {wallet?.totalEarned ?? 0} / 5000 pts
                  </span>
                </div>
                <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-600 h-full rounded-full transition-all duration-1000"
                    style={{
                      width: `${Math.min(100, ((wallet?.totalEarned ?? 0) / 5000) * 100)}%`,
                    }}
                  ></div>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-200 space-y-4">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Highlights
                </p>
                <div className="p-4 bg-white rounded-2xl border border-slate-100 shadow-sm">
                  <p className="text-sm font-bold text-slate-800">Points Master</p>
                  <p className="text-xs text-slate-500 mt-1">
                    You have earned more points than 85% of your team this month!
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-slate-100 rounded-3xl overflow-hidden shadow-sm">
            <div className="p-6 border-b border-slate-50 flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <History className="w-5 h-5 text-slate-400" />
                Points History
              </h3>
            </div>

            <div className="divide-y divide-slate-50 max-h-[500px] overflow-y-auto">
              {loading ? (
                <div className="p-12 text-center text-slate-400 font-bold">Loading history...</div>
              ) : transactions.length === 0 ? (
                <div className="p-12 text-center text-slate-400 font-bold">
                  No point transactions found.
                </div>
              ) : (
                transactions.map((item) => (
                  <div
                    key={item.id}
                    className="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className={`h-10 w-10 rounded-xl flex items-center justify-center ${
                          item.points > 0
                            ? 'bg-emerald-50 text-emerald-600'
                            : 'bg-rose-50 text-rose-600'
                        }`}
                      >
                        {item.points > 0 ? (
                          <ArrowUpCircle className="w-6 h-6" />
                        ) : (
                          <ArrowDownCircle className="w-6 h-6" />
                        )}
                      </div>
                      <div>
                        <p className="font-bold text-slate-800">{item.description}</p>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          {item.type}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p
                        className={`font-black ${item.points > 0 ? 'text-emerald-600' : 'text-rose-600'}`}
                      >
                        {item.points > 0 ? '+' : ''}
                        {item.points} pts
                      </p>
                      <p className="text-xs text-slate-400 font-medium whitespace-nowrap">
                        {new Date(item.createdAt).toLocaleDateString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserWallet;
