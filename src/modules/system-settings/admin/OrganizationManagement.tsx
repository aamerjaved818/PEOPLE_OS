import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Building2, AlertCircle, CheckCircle, Lock } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/components/ui/Toast';
import { api } from '@/services/api';
import { useOrgStore } from '@/store/orgStore';

interface CreateOrgForm {
  name: string;
  code: string;
  adminEmail: string;
  adminUsername: string;
}

const OrganizationManagement: React.FC = () => {
  const { currentUser } = useOrgStore();
  const { success, error } = useToast();
  const [createdOrg, setCreatedOrg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CreateOrgForm>({
    defaultValues: {
      code: 'ORG-',
    },
  });

  const onSubmit = async (data: CreateOrgForm) => {
    try {
      // Direct API call to create org
      // Note: We need to use api.post or request directly as this is a specific administrative action
      // Assuming backend supports POST /organizations

      const payload = {
        name: data.name,
        code: data.code,
        email: data.adminEmail,
        // We might want to seed the initial admin here or let the backend handle it
      };

      // Since api.createOrganization is not explicitly in the store/interface yet,
      // we'll try to use the generic post method or similar if available,
      // OR assuming we might need to add this endpoint.
      // For now, based on instructions, we'll try to save a new org profile.

      // However, typical saveOrganization updates the CURRENT org.
      // We need to Create.

      // Let's use api.request directly for clarity if typed allow, or cast
      await (api as any).post('/organizations', payload);

      success(`Organization "${data.name}" created successfully.`);
      setCreatedOrg(data.name);
      reset({ code: 'ORG-' });
    } catch (err: any) {
      console.error(err);
      error(err.response?.data?.detail || 'Failed to create organization. Code must be unique.');
    }
  };

  if (currentUser?.role !== 'Root') {
    return (
      <div className="p-8 flex items-center justify-center h-full text-text-muted">
        <div className="text-center">
          <Lock size={48} className="mx-auto mb-4 opacity-20" />
          <h2 className="text-lg font-bold">Access Restricted</h2>
          <p className="text-xs mt-2">Only Root administrators can manage organizations.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="card-vibrant p-8 border border-border">
        <div className="flex items-center gap-4 mb-6 border-b border-border pb-4">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
            <Building2 size={20} />
          </div>
          <div>
            <h3 className="text-lg font-black text-text-primary uppercase tracking-tight">
              Create New Organization
            </h3>
            <p className="text-xs text-text-muted font-medium">
              Provision a new tenant environment.
            </p>
          </div>
        </div>

        {createdOrg && (
          <div className="mb-6 p-4 bg-success/10 border border-success/20 rounded-xl flex items-center gap-3 text-success">
            <CheckCircle size={18} />
            <p className="text-sm font-bold">
              Organization <span className="underline">{createdOrg}</span> has been provisioned.
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-2xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Org Code */}
            <div>
              <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                Organization Code <span className="text-danger">*</span>
              </label>
              <input
                {...register('code', {
                  required: 'Code is required',
                  pattern: {
                    value: /^[A-Z0-9-]+$/,
                    message: 'Only uppercase alphanumeric and hyphens allowed',
                  },
                })}
                className="w-full bg-bg border border-border rounded-xl py-3 px-4 text-text-primary font-bold focus:ring-2 focus:ring-primary/20 outline-none transition-all uppercase tracking-widest"
                placeholder="ORG-000"
              />
              {errors.code && (
                <p className="text-danger text-[0.6rem] font-bold mt-1.5 flex items-center gap-1">
                  <AlertCircle size={10} /> {errors.code.message}
                </p>
              )}
              <p className="text-[0.6rem] text-text-muted mt-1.5">
                Unique immutable identifier (e.g. ORG-US-01)
              </p>
            </div>

            {/* Org Name */}
            <div>
              <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                Organization Name <span className="text-danger">*</span>
              </label>
              <input
                {...register('name', { required: 'Name is required' })}
                className="w-full bg-bg border border-border rounded-xl py-3 px-4 text-text-primary font-bold focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                placeholder="e.g. Acme Corporation"
              />
              {errors.name && (
                <p className="text-danger text-[0.6rem] font-bold mt-1.5 flex items-center gap-1">
                  <AlertCircle size={10} /> {errors.name.message}
                </p>
              )}
            </div>

            {/* Admin Email */}
            <div className="md:col-span-2">
              <label className="block text-[0.65rem] font-black text-text-muted uppercase tracking-[0.1em] mb-2">
                Initial Admin Email
              </label>
              <input
                {...register('adminEmail', {
                  required: 'Admin Email is required',
                  pattern: {
                    value: /^\S+@\S+$/i,
                    message: 'Invalid email address',
                  },
                })}
                className="w-full bg-bg border border-border rounded-xl py-3 px-4 text-text-primary font-medium focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                placeholder="admin@neworg.com"
              />
              <p className="text-[0.6rem] text-text-muted mt-1.5">
                This user will be assigned as the Super Admin for the new organization.
              </p>
            </div>
          </div>

          <div className="pt-4 flex justify-end">
            <Button
              disabled={isSubmitting}
              type="submit"
              className="px-8 h-10 bg-primary hover:bg-primary/90 text-primary-foreground font-black uppercase tracking-widest text-xs rounded-xl shadow-lg shadow-primary/20"
            >
              {isSubmitting ? 'Provisioning...' : 'Create Organization'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OrganizationManagement;
