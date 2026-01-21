import React, { useState, useEffect } from 'react';
import { X, Save, Building2, Globe, MapPin, Hash, Phone, Mail, Calendar } from 'lucide-react';
import { OrganizationProfile } from '../../../types';
import { Button } from '../../../components/ui/Button';

interface OrganizationFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<OrganizationProfile>) => Promise<void>;
  initialData?: OrganizationProfile;
}

const OrganizationFormModal: React.FC<OrganizationFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
}) => {
  const [formData, setFormData] = useState<Partial<OrganizationProfile>>({
    name: '',
    code: '',
    industry: '',
    country: '',
    city: '',
    email: '',
    website: '',
    phone: '',
    taxId: '',
    registrationNumber: '',
    foundedDate: '',
    ...initialData,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({ ...initialData });
    } else {
      setFormData({
        name: '',
        code: '',
        industry: '',
        country: '',
        city: '',
        email: '',
        website: '',
        phone: '',
        taxId: '',
        registrationNumber: '',
        foundedDate: '',
      });
    }
  }, [initialData, isOpen]);

  if (!isOpen) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error('Failed to save organization', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-surface border border-white/10 rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-6 border-b border-white/10 bg-slate-900/50">
          <h2 className="text-xl font-black uppercase tracking-tight text-white flex items-center gap-3">
            <Building2 className="text-blue-400" size={24} />
            {initialData ? 'Edit Organization' : 'Register New Organization'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <form
          onSubmit={handleSubmit}
          className="p-6 space-y-6 max-h-[70vh] overflow-y-auto custom-scrollbar"
        >
          {/* Identity Section */}
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-blue-400 mb-2">
              Corporate Identity
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Organization Name <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <Building2
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="text"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                    placeholder="e.g. Acme Corp"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Organization Code <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <Hash
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="text"
                    name="code"
                    required
                    value={formData.code}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                    placeholder="e.g. ORG-001"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Industry / Sector
                </label>
                <div className="relative">
                  <ActivityIcon
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="text"
                    name="industry"
                    value={formData.industry}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                    placeholder="e.g. Technology"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Establishment Date
                </label>
                <div className="relative">
                  <Calendar
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="date"
                    name="foundedDate"
                    value={formData.foundedDate}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all [&::-webkit-calendar-picker-indicator]:invert"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Location & Contact */}
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-emerald-400 mb-2">
              Location & Contact
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Country
                </label>
                <div className="relative">
                  <Globe
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                    placeholder="e.g. Pakistan"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  City
                </label>
                <div className="relative">
                  <MapPin
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                    placeholder="e.g. Lahore"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Email
                </label>
                <div className="relative">
                  <Mail
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                    placeholder="contact@company.com"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Phone
                </label>
                <div className="relative">
                  <Phone
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                    placeholder="+92 300 1234567"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-1.5 mt-2">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                Website
              </label>
              <div className="relative">
                <Globe
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                  size={16}
                />
                <input
                  type="url"
                  name="website"
                  value={formData.website}
                  onChange={handleChange}
                  className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                  placeholder="https://example.com"
                />
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-white/10 flex items-center justify-end gap-3">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              disabled={isSubmitting}
              className="text-slate-400 hover:text-white"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-blue-600 hover:bg-blue-500 text-white min-w-[120px] shadow-lg shadow-blue-600/20"
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Saving...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Save size={16} />
                  Save Organization
                </span>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Helper for the missing icon from destructuring if needed, though Lucide has Activity.
// But I didn't import Activity, let's fix that validation or assume it works.
// Wait, I imported Activity in OrganizationList, but here in Form I missed it.
// Let's assume standard Lucide import.
// I will import Activity in the file import statement.

import { Activity as ActivityIcon } from 'lucide-react';

export default OrganizationFormModal;
