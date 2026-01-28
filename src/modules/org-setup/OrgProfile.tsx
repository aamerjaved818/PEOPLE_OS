import React, { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Building, Globe, Mail, MapPin, Phone, Save, Upload, Lock } from 'lucide-react';
import { useOrgStore } from '@/store/orgStore';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/components/ui/Toast';
import DateInput from '@/components/ui/DateInput';
import { OrganizationProfile } from '@/types';

import OrgSwitcher from './OrgSwitcher';
import { DataExportButton } from '@/components/common/DataExportButton';

const OrgProfile: React.FC = () => {
  const { profile, updateProfile, saveProfile, fetchProfile } = useOrgStore();
  const { success, error } = useToast();

  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { isDirty, isSubmitting, errors },
  } = useForm<OrganizationProfile>({
    defaultValues: profile,
  });

  // Update form when store changes (e.g. after fetch)
  useEffect(() => {
    Object.entries(profile).forEach(([key, value]) => {
      setValue(key as keyof OrganizationProfile, value);
    });
  }, [profile, setValue]);

  const handleOrgSwitch = (orgId: string) => {
    fetchProfile(orgId);
    success('Switched organization context');
  };

  const onSubmit = async (data: OrganizationProfile) => {
    try {
      updateProfile(data);
      await saveProfile();
      success('Organization profile saved successfully');
    } catch (err) {
      error('Failed to save profile');
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="card-vibrant overflow-hidden shadow-sm">
        <div className="px-8 py-6 border-b border-border bg-bg/50 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div>
              <h3 className="font-black text-sm text-vibrant uppercase tracking-wider flex items-center gap-3">
                <Building size={20} className="text-primary" />
                Company Profile
              </h3>
              <p className="text-[0.625rem] text-text-muted font-bold mt-1.5 uppercase tracking-widest">
                Basic company information and logo
              </p>
            </div>

            <div className="h-8 w-px bg-border" />

            <OrgSwitcher currentOrgId={profile.id} onSwitch={handleOrgSwitch} />
          </div>
          <div className="flex gap-2">
            <DataExportButton
              data={[profile]}
              columns={[
                { key: 'name', header: 'Company Name' },
                { key: 'code', header: 'Org Code' },
                { key: 'industry', header: 'Industry' },
                { key: 'email', header: 'Email' },
                { key: 'phone', header: 'Phone' },
                { key: 'country', header: 'Country' },
                { key: 'taxId', header: 'Tax ID' },
              ]}
              filename="Organization_Profile"
              title="Organization Profile"
            />
            <Button
              onClick={handleSubmit(onSubmit)}
              disabled={!isDirty || isSubmitting}
              className="h-9 px-6 bg-primary hover:bg-primary/90 text-primary-foreground text-[0.65rem] font-black uppercase tracking-[0.15em] gap-2 rounded-lg shadow-lg shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <span className="animate-spin">⌛</span>
              ) : (
                <Save size={14} strokeWidth={3} />
              )}
              Save Changes
            </Button>
          </div>
        </div>

        <div className="p-8">
          <form className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Branding Section */}
            <div className="lg:col-span-1 space-y-6">
              <div className="h-56 w-full rounded-2xl card-vibrant border-2 border-dashed border-border flex flex-col items-center justify-center group cursor-pointer hover:border-primary/50 hover:bg-muted/50 transition-all relative overflow-hidden">
                {profile.logo ? (
                  <img src={profile.logo} alt="Logo" className="w-full h-full object-contain p-4" />
                ) : (
                  <div className="text-center p-6">
                    <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                      <Upload
                        size={24}
                        className="text-muted-foreground group-hover:text-primary"
                      />
                    </div>
                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2">
                      Upload Logo
                    </p>
                    <p className="text-[0.6rem] text-muted-foreground">
                      PNG, JPG or SVG
                      <br />
                      Max 2MB
                    </p>
                  </div>
                )}
                <input
                  type="file"
                  className="absolute inset-0 opacity-0 cursor-pointer"
                  accept="image/*"
                  onChange={(e) => {
                    // Handle file upload (mock for now, or implement real upload logic)
                    const file = e.target.files?.[0];
                    if (file) {
                      const reader = new FileReader();
                      reader.onloadend = () => {
                        setValue('logo', reader.result as string, { shouldDirty: true });
                      };
                      reader.readAsDataURL(file);
                    }
                  }}
                />
              </div>

              <div className="card-vibrant rounded-xl p-5 border border-border">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-4 border-b border-border pb-2">
                  Regional Settings
                </h4>
                <div className="space-y-4">
                  <div>
                    <label className="block text-[0.6rem] font-black text-muted-foreground uppercase tracking-widest mb-1.5">
                      Currency
                    </label>
                    <select
                      {...register('currency')}
                      className="w-full bg-input border border-border rounded-lg p-2.5 text-sm font-bold text-foreground focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                    >
                      <option value="PKR" className="bg-surface text-foreground">
                        PKR (Pakistani Rupee)
                      </option>
                      <option value="USD" className="bg-surface text-foreground">
                        USD (US Dollar)
                      </option>
                      <option value="EUR" className="bg-surface text-foreground">
                        EUR (Euro)
                      </option>
                      <option value="GBP" className="bg-surface text-foreground">
                        GBP (British Pound)
                      </option>
                      <option value="AED" className="bg-surface text-foreground">
                        AED (UAE Dirham)
                      </option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[0.6rem] font-black text-muted-foreground uppercase tracking-widest mb-1.5">
                      Tax Year End
                    </label>
                    <select
                      {...register('taxYearEnd')}
                      className="w-full bg-input border border-border rounded-lg p-2.5 text-sm font-bold text-foreground focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                    >
                      <option value="June" className="bg-surface text-foreground">
                        June
                      </option>
                      <option value="December" className="bg-surface text-foreground">
                        December
                      </option>
                      <option value="March" className="bg-surface text-foreground">
                        March
                      </option>
                      <option value="September" className="bg-surface text-foreground">
                        September
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* General Info Section */}
            <div className="lg:col-span-2 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="col-span-full">
                  <label className="text-[0.65rem] font-black text-muted-foreground uppercase tracking-[0.1em] mb-2 flex justify-between">
                    Organization Code
                    <Lock size={12} className="text-muted-foreground/70" />
                  </label>
                  <div className="relative">
                    <Building
                      className="absolute left-3.5 top-3.5 text-muted-foreground"
                      size={18}
                    />
                    <input
                      {...register('code', { required: true })}
                      readOnly
                      className="w-full bg-muted/50 border border-border rounded-xl py-3 pl-10 pr-4 text-foreground font-bold focus:ring-0 outline-none transition-all uppercase tracking-widest cursor-not-allowed opacity-75"
                      placeholder="e.g. ORG01"
                      title="Organization Code is immutable"
                    />
                  </div>
                  <p className="text-[0.6rem] text-muted-foreground font-medium mt-1.5 ml-1">
                    Unique identifier for your organization.
                  </p>
                </div>

                <div className="col-span-full">
                  <label className="text-[0.65rem] font-black text-primary uppercase tracking-[0.1em] mb-2 flex justify-between">
                    Company Name
                    <Lock size={12} className="text-primary/70" />
                  </label>
                  <div className="relative">
                    <Building
                      className="absolute left-3.5 top-3.5 text-muted-foreground"
                      size={18}
                    />
                    <input
                      {...register('name', { required: true })}
                      readOnly
                      className="w-full bg-muted/50 border border-border rounded-xl py-3 pl-10 pr-4 text-foreground font-bold focus:ring-0 outline-none transition-all cursor-not-allowed opacity-75"
                      placeholder="e.g. Acme Corp"
                      title="Company Name is immutable. Contact support for changes."
                    />
                  </div>
                </div>

                <div className="col-span-full">
                  <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                    Industry / Sector
                  </label>
                  <div className="relative">
                    <Globe className="absolute left-3.5 top-3.5 text-text-muted" size={18} />
                    <input
                      {...register('industry')}
                      className="w-full bg-bg border border-border rounded-xl py-3 pl-10 pr-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                      placeholder="e.g. Manufacturing, Technology"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                    Official Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-3.5 text-text-muted" size={18} />
                    <input
                      {...register('email')}
                      className="w-full bg-bg border border-border rounded-xl py-3 pl-10 pr-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                      placeholder="contact@company.com"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3.5 top-3.5 text-text-muted" size={18} />
                    <input
                      {...register('phone')}
                      className="w-full bg-bg border border-border rounded-xl py-3 pl-10 pr-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                      placeholder="+1 (555) 000-0000"
                    />
                  </div>
                </div>

                <div className="col-span-full">
                  <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                    Headquarters Address
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3.5 top-3.5 text-text-muted" size={18} />
                    <textarea
                      {...register('addressLine1')}
                      rows={3}
                      className="w-full bg-bg border border-border rounded-xl py-3 pl-10 pr-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all resize-none"
                      placeholder="123 Corporate Blvd, Business District..."
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                    Country
                  </label>
                  <div className="relative">
                    <Globe className="absolute left-3.5 top-3.5 text-text-muted" size={18} />
                    <input
                      {...register('country')}
                      className="w-full bg-bg border border-border rounded-xl py-3 pl-10 pr-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                      placeholder="e.g. Pakistan"
                    />
                  </div>
                </div>

                <div>
                  <Controller
                    name="foundedDate"
                    control={control}
                    render={({ field }) => (
                      <DateInput
                        label="Establishment Date"
                        value={field.value || ''}
                        onChange={field.onChange}
                        error={errors.foundedDate?.message}
                        placeholder="DD-MMM-YYYY"
                      />
                    )}
                  />
                  <p className="text-[0.6rem] text-text-muted font-medium mt-1.5 ml-1">
                    Date when the organization was established
                  </p>
                </div>

                <div>
                  <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                    Tax Registration (NTN/EIN)
                  </label>
                  <input
                    {...register('taxId')}
                    className="w-full bg-bg border border-border rounded-xl py-3 px-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                    placeholder="e.g. 1234567-8"
                  />
                </div>
              </div>

              {/* Advanced System Settings Section */}
              <div className="col-span-full mt-8 pt-8 border-t border-border">
                <div className="card-vibrant rounded-xl p-6 border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
                  <h4 className="text-xs font-bold text-primary uppercase tracking-wider mb-4 pb-3 flex items-center gap-2">
                    <Lock size={16} className="text-primary" />
                    Advanced System Settings
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                        Enabled Modules
                      </label>
                      <input
                        {...register('enabledModules')}
                        className="w-full bg-bg border border-border rounded-xl py-3 px-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all font-mono text-sm"
                        placeholder='["hcm", "payroll", "attendance"]'
                      />
                      <p className="text-[0.6rem] text-text-muted font-medium mt-1.5 ml-1">
                        JSON array of enabled modules for this organization
                      </p>
                    </div>

                    <div>
                      <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                        System Authority
                      </label>
                      <input
                        {...register('systemAuthority')}
                        className="w-full bg-bg border border-border rounded-xl py-3 px-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                        placeholder="e.g. root, admin"
                      />
                      <p className="text-[0.6rem] text-text-muted font-medium mt-1.5 ml-1">
                        System-level permissions configuration
                      </p>
                    </div>

                    <div>
                      <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                        Approval Workflows
                      </label>
                      <input
                        {...register('approvalWorkflows')}
                        className="w-full bg-bg border border-border rounded-xl py-3 px-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all font-mono text-sm"
                        placeholder='{"leave": "manager", "expense": "finance"}'
                      />
                      <p className="text-[0.6rem] text-text-muted font-medium mt-1.5 ml-1">
                        Workflow configuration in JSON format
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default OrgProfile;
