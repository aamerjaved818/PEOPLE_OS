import React, { useState, useEffect } from 'react';
import { ChevronDown, Check, Building } from 'lucide-react';
import { OrganizationProfile } from '@/types';
import { useOrgStore } from '@/store/orgStore';

interface OrgSwitcherProps {
  currentOrgId?: string;
  onSwitch: (orgId: string) => void;
}

const OrgSwitcher: React.FC<OrgSwitcherProps> = ({ currentOrgId, onSwitch }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [organizations, setOrganizations] = useState<OrganizationProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const {
    profile,
    fetchOrganizations: storeFetchOrganizations,
    organizations: storeOrganizations,
  } = useOrgStore();

  useEffect(() => {
    const fetchOrgs = async () => {
      setLoading(true);
      try {
        const data = await storeFetchOrganizations?.();
        setOrganizations(data || storeOrganizations || []);
      } catch (error) {
        console.error('Failed to fetch organizations', error);
      } finally {
        setLoading(false);
      }
    };

    if (isOpen && organizations.length === 0) {
      fetchOrgs();
    }
  }, [isOpen, storeFetchOrganizations, storeOrganizations, profile, organizations.length]);

  const activeOrg = organizations.find((o) => o.id === currentOrgId) || profile;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 pl-3 pr-2 py-1.5 rounded-lg bg-surface border border-border hover:bg-accent/50 transition-all group"
      >
        <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
          {activeOrg?.logo ? (
            <img src={activeOrg.logo} alt="" className="w-full h-full object-cover rounded-full" />
          ) : (
            <Building size={12} className="text-primary" />
          )}
        </div>

        <div className="text-left hidden md:block">
          <p className="text-xs font-bold text-foreground leading-none max-w-[150px] truncate">
            {activeOrg?.name || 'Select Organization'}
          </p>
          <p className="text-[10px] text-muted-foreground font-medium leading-none mt-0.5">
            {activeOrg?.code || 'Switch Context'}
          </p>
        </div>

        <ChevronDown
          size={14}
          className={`text-muted-foreground transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
            role="button"
            tabIndex={-1}
            aria-label="Close menu"
            onKeyDown={(e) => e.key === 'Escape' && setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-2 w-64 bg-surface border border-border rounded-xl shadow-xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100 flex flex-col">
            <div className="p-2 border-b border-border bg-muted/30">
              <p className="text-[10px] font-black uppercase tracking-wider text-muted-foreground px-2 py-1">
                Switch Organization
              </p>
            </div>

            <div className="max-h-[300px] overflow-y-auto p-1 custom-scrollbar">
              {loading ? (
                <div className="p-4 text-center text-xs text-muted-foreground">Loading...</div>
              ) : (
                organizations.map((org) => (
                  <button
                    key={org.id}
                    onClick={() => {
                      onSwitch(org.id);
                      setIsOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 p-2 rounded-lg text-left transition-all ${
                      currentOrgId === org.id
                        ? 'bg-primary/10 text-primary'
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                    }`}
                  >
                    <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center shrink-0 border border-border">
                      {org.logo ? (
                        <img
                          src={org.logo}
                          alt=""
                          className="w-full h-full object-cover rounded-lg"
                        />
                      ) : (
                        <Building size={16} />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-bold truncate">{org.name}</p>
                      <p className="text-[10px] opacity-70 truncate">{org.code}</p>
                    </div>

                    {currentOrgId === org.id && (
                      <Check size={14} className="text-primary shrink-0" />
                    )}
                  </button>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default OrgSwitcher;
