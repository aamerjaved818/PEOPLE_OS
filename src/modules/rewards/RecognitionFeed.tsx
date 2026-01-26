import React, { useState, useEffect } from 'react';
import {
  Send,
  Users,
  MessageSquare,
  Heart,
  Award,
  ShieldCheck,
  Zap,
  ArrowUpRight,
  Star,
} from 'lucide-react';
import api from '@/services/api';
import { Recognition, Employee } from '@/types';

interface RecognitionFeedProps {
  onRecognitionSent: () => void;
}

const RecognitionFeed: React.FC<RecognitionFeedProps> = ({ onRecognitionSent }) => {
  const [recognitions, setRecognitions] = useState<Recognition[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    receiverId: '',
    message: '',
    category: 'Teamwork',
    pointsAwarded: 50,
  });

  const categories = [
    { name: 'Teamwork', icon: Users, color: 'text-blue-500', bg: 'bg-blue-50' },
    { name: 'Innovation', icon: Zap, color: 'text-amber-500', bg: 'bg-amber-50' },
    { name: 'Excellence', icon: Award, color: 'text-purple-500', bg: 'bg-purple-50' },
    { name: 'Integrity', icon: ShieldCheck, color: 'text-emerald-500', bg: 'bg-emerald-50' },
    { name: 'Empathy', icon: Heart, color: 'text-rose-500', bg: 'bg-rose-50' },
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [recData, empData] = await Promise.all([api.getRecognitions(), api.getEmployees()]);
      setRecognitions(recData);
      setEmployees(empData);
    } catch (error) {
      console.error('Failed to fetch recognition data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const user = JSON.parse(localStorage.getItem('user_data') || '{}');
      await api.saveRecognition({
        ...formData,
        senderId: user.id,
      });
      setShowForm(false);
      setFormData({ receiverId: '', message: '', category: 'Teamwork', pointsAwarded: 50 });
      fetchData();
      onRecognitionSent();
    } catch (error) {
      console.error('Failed to send recognition', error);
    }
  };

  const getEmployeeName = (id: string) => {
    const emp = employees.find((e) => e.id === id);
    return emp ? emp.name : 'Unknown Employee';
  };

  const getCategoryIcon = (category: string) => {
    const cat = categories.find((c) => c.name === category);
    const IconComp = cat ? cat.icon : MessageSquare;
    return <IconComp className={`w-5 h-5 ${cat?.color ?? 'text-slate-400'}`} />;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
      {/* Feed Section */}
      <div className="lg:col-span-2 space-y-6">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            Recent Shout-outs
            <span className="bg-indigo-100 text-indigo-600 px-2 py-0.5 rounded-full text-xs">
              {recognitions.length}
            </span>
          </h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="md:hidden bg-indigo-600 text-white p-2 rounded-full shadow-lg"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-slate-50 animate-pulse h-40 rounded-3xl" />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {recognitions.map((rec) => (
              <div
                key={rec.id}
                className="bg-white border border-slate-100 p-6 rounded-3xl hover:shadow-md transition-shadow group relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                    <Star className="w-3 h-3 fill-current" />+{rec.pointsAwarded} pts
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-lg">
                    {getEmployeeName(rec.senderId).charAt(0)}
                  </div>
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center flex-wrap gap-2 text-sm">
                      <span className="font-bold text-slate-800">
                        {getEmployeeName(rec.senderId)}
                      </span>
                      <span className="text-slate-400">recognized</span>
                      <span className="font-bold text-indigo-600">
                        {getEmployeeName(rec.receiverId)}
                      </span>
                      <span className="text-slate-300 ml-auto">
                        {new Date(rec.createdAt).toLocaleDateString()}
                      </span>
                    </div>

                    <div className="bg-slate-50 p-4 rounded-2xl relative">
                      <p className="text-slate-600 leading-relaxed italic">"{rec.message}"</p>
                    </div>

                    <div className="flex items-center gap-3">
                      <div
                        className={`px-3 py-1 rounded-full flex items-center gap-2 text-xs font-medium border border-slate-100 bg-white`}
                      >
                        {getCategoryIcon(rec.category)}
                        {rec.category}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {recognitions.length === 0 && (
              <div className="text-center py-20 bg-slate-50 rounded-3xl border border-dashed border-slate-200">
                <Heart className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500 font-medium">
                  No recognitions yet. Be the first to shout out!
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Recognition Form */}
      <div className={`lg:block ${showForm ? 'block' : 'hidden'} lg:sticky lg:top-6`}>
        <div className="bg-slate-50 p-8 rounded-3xl border border-slate-200 space-y-6">
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-slate-800">Recognize Peer</h2>
            <p className="text-sm text-slate-500">Send a digital high-five and some points!</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Select Person
              </label>
              <select
                required
                className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-medium text-slate-700"
                value={formData.receiverId}
                onChange={(e) => setFormData({ ...formData, receiverId: e.target.value })}
              >
                <option value="">Choose a teammate...</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Category
              </label>
              <div className="grid grid-cols-1 gap-2">
                {categories.map((cat) => (
                  <button
                    key={cat.name}
                    type="button"
                    onClick={() => setFormData({ ...formData, category: cat.name })}
                    className={`flex items-center justify-between p-3 rounded-xl border transition-all ${
                      formData.category === cat.name
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-white bg-white hover:border-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <cat.icon className={`w-5 h-5 ${cat.color}`} />
                      <span className="text-sm font-bold text-slate-700">{cat.name}</span>
                    </div>
                    {formData.category === cat.name && (
                      <ArrowUpRight className="w-4 h-4 text-indigo-600" />
                    )}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Message
              </label>
              <textarea
                required
                rows={3}
                placeholder="What did they do that was awesome?"
                className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-medium text-slate-700"
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-indigo-100 flex items-center justify-center gap-2 transform active:scale-95 transition-all"
              >
                <Send className="w-5 h-5" />
                Send Shout-out
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RecognitionFeed;
