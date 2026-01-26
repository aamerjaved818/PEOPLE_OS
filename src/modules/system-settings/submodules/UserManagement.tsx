import React, { useState } from 'react';
import { ShieldCheck, Users, Check, X, Plus, Trash2, Edit2, Building } from 'lucide-react';
import { useOrgStore, Permission, ROLE_HIERARCHY } from '@store/orgStore';
import { useToast } from '@components/ui/Toast';
import { useModal } from '@hooks/useModal';
import { useSaveEntity } from '@hooks/useSaveEntity';
import { Button } from '@components/ui/Button';
import { Input } from '@components/ui/Input';
import { Modal } from '@components/ui/Modal';
import { SYSTEM_ROOT_ROLES, ORG_SUPER_ROLES, GRANULAR_PERMISSIONS } from '@/config/permissions';

export interface AdminUserForm {
  id?: string;
  username: string;
  name: string;
  email: string;
  role: string;
  status: string;
  isSystemUser: boolean;
  password?: string;
}

const PermissionMatrix = React.memo(() => {
  const { rolePermissions, togglePermission } = useOrgStore();

  return (
    <div className="card-vibrant rounded-xl overflow-hidden mb-8 shadow-sm">
      <div className="px-6 py-5 border-b border-border bg-bg/50">
        <h3 className="font-black text-sm text-vibrant flex items-center gap-3 uppercase tracking-wider">
          <ShieldCheck size={20} className="text-primary" />
          PERMISSIONS
        </h3>
        <p className="text-[0.65rem] text-text-muted mt-1.5 font-bold uppercase tracking-widest">
          Role Permissions
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-bg/80 text-[0.6rem] uppercase text-text-muted font-black tracking-[0.2em] border-b border-border/40">
            <tr>
              <th scope="col" className="px-6 py-4">
                ROLE
              </th>
              {GRANULAR_PERMISSIONS.map((perm) => (
                <th key={perm.id} scope="col" className="px-6 py-4 text-center">
                  <div className="flex flex-col items-center gap-1">
                    <span>{perm.label.toUpperCase()}</span>
                    <span className="text-[0.5rem] opacity-50 bg-primary/10 px-1.5 py-0.5 rounded text-primary border border-primary/20">
                      {perm.category.toUpperCase()}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {ROLE_HIERARCHY.slice()
              .reverse()
              .map((role) => {
                const isSystemRoot = SYSTEM_ROOT_ROLES.has(role as any);
                const isOrgSuper = ORG_SUPER_ROLES.has(role as any);
                const isFullAccess = isSystemRoot || isOrgSuper;

                return (
                  <tr key={role} className="hover:bg-primary/5 transition-all duration-300 group">
                    <td
                      scope="row"
                      className="px-6 py-4 font-black text-text-secondary text-xs tracking-tight group-hover:text-text-primary transition-colors"
                    >
                      {role}
                    </td>

                    {isFullAccess ? (
                      <td colSpan={GRANULAR_PERMISSIONS.length} className="px-6 py-4 text-center">
                        <div
                          className={`
                          inline-flex items-center gap-2 px-4 py-1.5 rounded-lg border shadow-sm
                          ${
                            isSystemRoot
                              ? 'bg-danger/10 border-danger/30 text-danger'
                              : 'bg-primary/10 border-primary/30 text-primary'
                          }
                        `}
                        >
                          <ShieldCheck size={14} strokeWidth={3} />
                          <span className="text-[0.65rem] font-black uppercase tracking-widest">
                            {isSystemRoot ? 'System Full Access' : 'Org Full Access'}
                          </span>
                        </div>
                      </td>
                    ) : (
                      GRANULAR_PERMISSIONS.map((col) => {
                        const localPerms = rolePermissions[role] || [];
                        const hasWildcard = localPerms.includes('*');
                        const hasAccess = hasWildcard || localPerms.includes(col.id);

                        return (
                          <td
                            key={col.id}
                            className="px-6 py-4 text-center"
                            onClick={() => !hasWildcard && togglePermission(role, col.id)}
                            title={hasWildcard ? 'Full System Access (Wildcard)' : col.description}
                          >
                            <div
                              className={`
                                inline-flex items-center justify-center transition-all duration-200 
                                ${!hasWildcard ? 'hover:scale-125 cursor-pointer hover:opacity-80 active:scale-95' : 'cursor-default opacity-50'}
                              `}
                            >
                              {hasAccess ? (
                                <Check
                                  size={18}
                                  className="text-success drop-shadow-md"
                                  strokeWidth={3}
                                />
                              ) : (
                                <X size={18} className="text-danger" strokeWidth={3} />
                              )}
                            </div>
                          </td>
                        );
                      })
                    )}
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>
    </div>
  );
});

interface UserManagementProps {
  onSync: () => void;
}

/**
 * UserManagement Component
 * @description Manages system administrators, roles, and permissions within the organization.
 * Key features:
 * - Admin list management (Add/Edit/Delete)
 * - Permission matrix visualization
 * - Security policy enforcement (MFA, Session limits)
 *
 * @param {Object} props - Component props
 * @param {Function} props.onSync - Callback after data modification
 * @param {boolean} props.isSaving - Loading state for persistence operations
 */
const UserManagement: React.FC<UserManagementProps> = ({ onSync: syncCallback }) => {
  const {
    users,
    addUser,
    updateUser,
    deleteUser,
    addAuditLog,
    fetchUsers,
    errorEntities,
    currentOrganization,
    fetchProfile,
    currentUser,
    loadingEntities,
  } = useOrgStore();
  const { success, error } = useToast();
  const adminUserModal = useModal();
  const orgUserModal = useModal();
  const [userToDelete, setUserToDelete] = useState<any | null>(null);
  const [userType, setUserType] = useState<'system' | 'org'>('system');

  const { organizations, fetchOrganizations } = useOrgStore();

  // Initial Fetch
  React.useEffect(() => {
    fetchUsers();
    if (currentUser?.role === 'Root') {
      fetchOrganizations();
    }
  }, [fetchUsers, currentUser, fetchOrganizations]);

  // Ensure a current organization is selected when possible so org users render
  React.useEffect(() => {
    // Priority 0: Root users should default to Global View (no org selected) unless manually selected
    if (currentUser?.role === 'Root') {
      return;
    }

    // Priority 1: Use current user's organization if assigned (Enforce Restriction)
    if (currentUser?.organizationId) {
      if (currentOrganization?.id !== currentUser.organizationId) {
        fetchProfile(currentUser.organizationId).catch(() => {});
      }
      return;
    }

    // Priority 2: If an organization is already active, respect "manual selection" and do not override.
    if (currentOrganization) {
      return;
    }

    // Priority 3: Restore from storage
    const selected = localStorage.getItem('selected_org_id');
    if (selected) {
      fetchProfile(selected).catch(() => {});
      return;
    }

    // Priority 4: Fallback: pick first organization id from any org user
    const firstOrgUser = users.find((u: any) => !u.isSystemUser && u.organizationId);
    if (firstOrgUser) {
      fetchProfile(firstOrgUser.organizationId).catch(() => {});
    }
  }, [currentOrganization, users, fetchProfile, currentUser]);

  // Separate users into system and organization users
  // Rule: Only Root can see Root users. All other users cannot view Root.
  const systemUsers = React.useMemo(() => {
    return users.filter((u: any) => {
      // Security: Always exclude Root users unless current user is Root
      if (u.role === 'Root' && currentUser?.role !== 'Root') {
        return false;
      }
      // STRICT DEFINITION: ONLY 'Root' is a global system administrator.
      // 'SystemAdmin', 'Super Admin' etc are considered org-level or at least not "Root".
      return u.role === 'Root';
    });
  }, [users, currentUser]);

  const orgUsers = React.useMemo(() => {
    return users.filter((u: any) => {
      // Exclude Root from the general list (they are in the System Admin list)
      if (u.role === 'Root') {
        return false;
      }
      // Root can see all org users across organizations
      if (currentUser?.role === 'Root') {
        return true;
      }
      // Non-root sees only users for the selected organization
      return u.organizationId === currentOrganization?.id;
    });
  }, [users, currentUser, currentOrganization]);

  const handleDeleteConfirm = async () => {
    if (!userToDelete) {
      return;
    }

    try {
      await deleteUser(userToDelete.id);
      addAuditLog({
        action: `Revoked access: ${userToDelete.username}`,
        user: 'Current Admin',
        status: 'Warning',
      });
      success('User access revoked successfully');
    } catch (err: any) {
      const errorMessage = err?.message || err?.detail || 'Failed to delete user';
      error(errorMessage);
    } finally {
      setUserToDelete(null);
    }
  };

  const {
    formData,
    updateField,
    handleSave,
    isSaving: isFormSaving,
    setFormData,
  } = useSaveEntity<AdminUserForm>({
    initialState: {
      username: '',
      name: '',
      email: '',
      role: 'SystemAdmin',
      status: 'Active',
      isSystemUser: false,
    },
    onSave: async (data) => {
      if (data.id) {
        updateUser(data.id, { ...data, role: data.role as any } as any); // Force cast to avoid strict union mismatch
        addAuditLog({
          action: `Updated ${userType === 'system' ? 'system' : 'organization'} user: ${data.username}`,
          user: 'Current Admin',
          status: 'Success',
        });
      } else {
        addUser({
          ...data,
          id: Date.now().toString(),
          isSystemUser: userType === 'system',
          organizationId: currentOrganization?.id,
        } as any);
        addAuditLog({
          action: `Added ${userType === 'system' ? 'system' : 'organization'} user: ${data.username}`,
          user: 'Current Admin',
          status: 'Success',
        });
      }
      syncCallback?.();
      userType === 'system' ? adminUserModal.close() : orgUserModal.close();
    },
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Loading State */}
      {loadingEntities?.users && (
        <div className="p-8 bg-primary/5 border border-primary/20 rounded-2xl text-center">
          <div className="flex items-center justify-center gap-3">
            <div className="w-4 h-4 rounded-full bg-primary animate-spin"></div>
            <p className="text-sm font-semibold text-text-primary">
              Loading access control data...
            </p>
          </div>
        </div>
      )}

      {/* System Admin Management Section - ONLY VISIBLE TO ROOT */}
      {currentUser?.role === 'Root' && (
        <div
          className="card-vibrant rounded-2xl shadow-sm overflow-hidden"
          role="region"
          aria-label="System Administrator Management"
        >
          <div className="px-8 py-6 border-b border-border bg-bg/50 flex items-center justify-between">
            <div>
              <h3 className="font-black text-sm text-vibrant uppercase tracking-wider">
                System Administrators
              </h3>
              <p className="text-[0.625rem] text-text-muted font-bold mt-1.5 uppercase tracking-[0.2em]">
                Manage system-level administrators with full access
              </p>
            </div>
            <Button
              size="sm"
              className="h-10 px-6 bg-primary hover:bg-primary/90 text-primary-foreground text-[0.65rem] font-black uppercase tracking-[0.15em] gap-3 rounded-lg shadow-lg shadow-primary/20 hover:shadow-primary/40 hover:-translate-y-0.5 transition-all duration-300"
              onClick={() => {
                setUserType('system');
                setFormData({
                  username: '',
                  name: '',
                  email: '',
                  role: 'Root',
                  status: 'Active',
                  isSystemUser: true,
                });
                adminUserModal.open();
              }}
              aria-label="Add New System Administrator"
            >
              <Plus size={16} strokeWidth={3} /> Add System Admin
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-bg/80 text-[0.6rem] uppercase text-text-muted font-black tracking-[0.25em] border-b border-border">
                <tr>
                  <th scope="col" className="px-8 py-5">
                    IDENTITY
                  </th>
                  <th scope="col" className="px-8 py-5">
                    ROLE / ACCESS
                  </th>
                  <th scope="col" className="px-8 py-5 text-center">
                    SECURITY STATUS
                  </th>
                  <th scope="col" className="px-8 py-5 text-right">
                    ACTIONS
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {systemUsers.map((user: any) => (
                  <tr
                    key={user.id}
                    className="hover:bg-primary/5 transition-all duration-200 group"
                  >
                    <td className="px-8 py-5">
                      <div className="flex items-center gap-4">
                        <div className="w-9 h-9 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[0.7rem] font-black border border-primary/20">
                          {(user.name || user.username || 'U')
                            .split(' ')
                            .map((n: string) => n[0])
                            .join('')
                            .slice(0, 2)
                            .toUpperCase()}
                        </div>
                        <div>
                          <p className="text-[0.75rem] font-black text-text-primary">
                            {user.username}
                          </p>
                          <p className="text-[0.625rem] text-text-muted font-medium tracking-tight mt-0.5">
                            {user.name || 'No Name Set'}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-8 py-5">
                      <div className="inline-block px-4 py-2 bg-bg border border-border rounded-lg shadow-sm">
                        <span className="font-black text-[0.625rem] tracking-[0.2em] text-primary uppercase">
                          {user.role === 'SystemAdmin' ? 'SYSTEMADMIN' : user.role.toUpperCase()}
                        </span>
                      </div>
                    </td>
                    <td className="px-8 py-5 text-center">
                      <div className="flex items-center justify-center gap-2">
                        {user.isSystemUser && (
                          <div className="px-2.5 py-1 rounded-[4px] bg-primary/20 border border-primary/40">
                            <span className="text-[10px] font-black text-primary tracking-tighter">
                              SYS
                            </span>
                          </div>
                        )}
                        {user.mfa_enabled && (
                          <div className="px-2.5 py-1 rounded-[4px] bg-success/20 border border-success/40">
                            <span className="text-[10px] font-black text-success tracking-tighter">
                              MFA
                            </span>
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-8 py-5 text-right">
                      <div className="flex items-center justify-end gap-2 transition-all">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-text-muted hover:text-primary hover:bg-primary/10"
                          onClick={() => {
                            setUserType('system');
                            setFormData(user);
                            adminUserModal.open();
                          }}
                          aria-label={`Edit ${user.name}`}
                        >
                          <Edit2 size={14} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-text-muted hover:text-danger hover:bg-danger/10"
                          onClick={() => setUserToDelete(user)}
                          aria-label={`Delete ${user.name}`}
                        >
                          <Trash2 size={14} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {errorEntities?.users && (
                  <tr>
                    <td colSpan={4} className="px-6 py-8 text-center bg-danger/10">
                      <p className="text-xs font-bold text-danger">
                        Failed to load users: {errorEntities.users}
                      </p>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => fetchUsers()}
                        className="mt-2 text-danger hover:text-danger/80"
                      >
                        Retry
                      </Button>
                    </td>
                  </tr>
                )}
                {!errorEntities?.users && systemUsers.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <div className="w-12 h-12 bg-muted-bg rounded-full flex items-center justify-center text-text-muted">
                          <Users size={24} />
                        </div>
                        <div>
                          <p className="text-xs font-black text-text-primary uppercase tracking-tight">
                            No system administrators found
                          </p>
                          <p className="text-[0.6rem] text-text-muted font-bold mt-1 antialiased">
                            Start by adding a new system administrator.
                          </p>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Organization Users Management Section */}
      <div
        className="card-vibrant rounded-2xl shadow-sm overflow-hidden"
        role="region"
        aria-label="Organization Users Management"
      >
        {!currentOrganization && currentUser?.role !== 'Root' ? (
          <div className="px-8 py-12 text-center bg-bg/50">
            <div className="flex flex-col items-center gap-3">
              <div className="w-12 h-12 bg-warning/10 rounded-full flex items-center justify-center text-warning">
                <Building size={24} />
              </div>
              <div>
                <p className="text-sm font-bold text-text-primary uppercase tracking-tight">
                  No Organization Selected
                </p>
                <p className="text-[0.75rem] text-text-muted font-medium mt-1">
                  Please navigate to the Organizations tab to select an organization first.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <>
            <div className="px-8 py-6 border-b border-border bg-bg/50 flex items-center justify-between">
              <div>
                <h3 className="font-black text-sm text-vibrant uppercase tracking-wider">
                  {currentUser?.role === 'Root' && !currentOrganization
                    ? 'All Organization Users'
                    : 'Organization Users'}
                </h3>
                <p className="text-[0.625rem] text-text-muted font-bold mt-1.5 uppercase tracking-[0.2em]">
                  {currentOrganization?.name
                    ? `${currentOrganization.name} • Manage users and admins for this organization`
                    : 'Global View • Managing users across all organizations (Root Access)'}
                </p>
              </div>
              <Button
                size="sm"
                className="h-10 px-6 bg-primary hover:bg-primary/90 text-primary-foreground text-[0.65rem] font-black uppercase tracking-[0.15em] gap-3 rounded-lg shadow-lg shadow-primary/20 hover:shadow-primary/40 hover:-translate-y-0.5 transition-all duration-300"
                onClick={() => {
                  setUserType('org');
                  setFormData({
                    username: '',
                    name: '',
                    email: '',
                    role: 'HRManager',
                    status: 'Active',
                    isSystemUser: false,
                  });
                  orgUserModal.open();
                }}
                aria-label="Add New Organization User"
                disabled={!currentOrganization}
              >
                <Plus size={16} strokeWidth={3} /> Add User
              </Button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-bg/80 text-[0.6rem] uppercase text-text-muted font-black tracking-[0.25em] border-b border-border">
                  <tr>
                    <th scope="col" className="px-8 py-5">
                      IDENTITY
                    </th>
                    {currentUser?.role === 'Root' && !currentOrganization && (
                      <th scope="col" className="px-8 py-5">
                        ORGANIZATION
                      </th>
                    )}
                    <th scope="col" className="px-8 py-5">
                      ROLE / ACCESS
                    </th>
                    <th scope="col" className="px-8 py-5 text-center">
                      SECURITY STATUS
                    </th>
                    <th scope="col" className="px-8 py-5 text-right">
                      ACTIONS
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {orgUsers.map((user: any) => (
                    <tr
                      key={user.id}
                      className="hover:bg-primary/5 transition-all duration-200 group"
                    >
                      <td className="px-8 py-5">
                        <div className="flex items-center gap-4">
                          <div className="w-9 h-9 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[0.7rem] font-black border border-primary/20">
                            {(user.name || user.username || 'U')
                              .split(' ')
                              .map((n: string) => n[0])
                              .join('')
                              .slice(0, 2)
                              .toUpperCase()}
                          </div>
                          <div>
                            <p className="text-[0.75rem] font-black text-text-primary">
                              {user.username}
                            </p>
                            <p className="text-[0.625rem] text-text-muted font-medium tracking-tight mt-0.5">
                              {user.name || 'No Name Set'}
                            </p>
                          </div>
                        </div>
                      </td>
                      {currentUser?.role === 'Root' && !currentOrganization && (
                        <td className="px-8 py-5">
                          {user.organizationId ? (
                            <div className="inline-block px-3 py-1.5 bg-primary/5 border border-primary/10 rounded-lg">
                              <span className="font-bold text-[0.6rem] text-primary uppercase tracking-wider">
                                {organizations.find((o) => o.id === user.organizationId)?.name ||
                                  'Unknown Org'}
                              </span>
                            </div>
                          ) : (
                            <span className="text-text-muted text-xs">-</span>
                          )}
                        </td>
                      )}
                      <td className="px-8 py-5">
                        <div className="inline-block px-4 py-2 bg-bg border border-border rounded-lg shadow-sm">
                          <span className="font-black text-[0.625rem] tracking-[0.2em] text-primary uppercase">
                            {user.role.toUpperCase()}
                          </span>
                        </div>
                      </td>
                      <td className="px-8 py-5 text-center">
                        <div className="flex items-center justify-center gap-2">
                          {user.mfa_enabled && (
                            <div className="px-2.5 py-1 rounded-[4px] bg-success/20 border border-success/40">
                              <span className="text-[10px] font-black text-success tracking-tighter">
                                MFA
                              </span>
                            </div>
                          )}
                          <div className="px-2.5 py-1 rounded-[4px] bg-info/20 border border-info/40">
                            <span className="text-[10px] font-black text-info tracking-tighter">
                              ORG
                            </span>
                          </div>
                        </div>
                      </td>
                      <td className="px-8 py-5 text-right">
                        <div className="flex items-center justify-end gap-2 transition-all">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-text-muted hover:text-primary hover:bg-primary/10"
                            onClick={() => {
                              setUserType('org');
                              setFormData(user);
                              orgUserModal.open();
                            }}
                            aria-label={`Edit ${user.name}`}
                          >
                            <Edit2 size={14} />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-text-muted hover:text-danger hover:bg-danger/10"
                            onClick={() => setUserToDelete(user)}
                            aria-label={`Delete ${user.name}`}
                          >
                            <Trash2 size={14} />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {!errorEntities?.users && orgUsers.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-12 text-center">
                        <div className="flex flex-col items-center gap-3">
                          <div className="w-12 h-12 bg-muted-bg rounded-full flex items-center justify-center text-text-muted">
                            <Users size={24} />
                          </div>
                          <div>
                            <p className="text-xs font-black text-text-primary uppercase tracking-tight">
                              No organization users found
                            </p>
                            <p className="text-[0.6rem] text-text-muted font-bold mt-1 antialiased">
                              Start by adding a new user to this organization.
                            </p>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Permission Matrix Area - ONLY VISIBLE TO ROOT */}
      {currentUser?.role === 'Root' && <PermissionMatrix />}

      {/* Delete Confirmation Dialog */}
      {/* Delete Confirmation Dialog */}
      <Modal
        isOpen={!!userToDelete}
        onClose={() => setUserToDelete(null)}
        title="Revoke Access?"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-sm text-text-secondary">
            This will permanently remove the administrator{' '}
            <span className="font-bold text-text-primary">{userToDelete?.username}</span> and revoke
            all their system privileges.
            <br />
            <br />
            <span className="text-danger font-bold">This action cannot be undone.</span>
          </p>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="ghost" onClick={() => setUserToDelete(null)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDeleteConfirm}>
              Revoke Access
            </Button>
          </div>
        </div>
      </Modal>

      {/* User Modal for System Admins */}
      <Modal
        isOpen={adminUserModal.isOpen}
        onClose={adminUserModal.close}
        title={formData.id ? 'Edit System Administrator' : 'Add New System Administrator'}
      >
        <div className="space-y-4 py-2">
          <p className="text-[0.6rem] text-text-muted font-medium -mt-2 mb-2">
            <span className="text-danger">*</span> All fields are required
          </p>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Username *"
              value={formData.username}
              onChange={(e) => updateField('username', e.target.value)}
              placeholder="e.g. root_admin"
              required
            />
            <Input
              label="Full Name *"
              value={formData.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="John Doe"
              required
            />
          </div>
          <Input
            label="Email Address *"
            value={formData.email}
            onChange={(e) => updateField('email', e.target.value)}
            placeholder="admin@enterprise.com"
            type="email"
            required
          />
          <div className="space-y-1.5">
            <label className="text-[0.6rem] font-black text-text-muted uppercase tracking-widest ml-1">
              System Role <span className="text-danger">*</span>
            </label>
            <select
              className="w-full input-frost font-black text-xs outline-none"
              value={formData.role}
              onChange={(e) => updateField('role', e.target.value)}
              required
            >
              {ROLE_HIERARCHY.filter((role) => {
                if (formData.isSystemUser) {
                  // System Admin Modal: Only allow Root
                  return role === 'Root';
                } else {
                  // Org User Modal: Allow everything EXCEPT Root
                  return role !== 'Root';
                }
              }).map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </div>
          {!formData.id && (
            <Input
              label="Temporary Password *"
              type="password"
              value={formData.password}
              onChange={(e) => updateField('password', e.target.value)}
              placeholder="••••••••"
              required
            />
          )}

          <div className="flex items-center gap-3 p-3 bg-primary/10 border border-primary/20 rounded-xl">
            <input
              type="checkbox"
              id="isSystemUser"
              className="w-4 h-4 rounded border-border bg-transparent text-primary focus:ring-primary/20"
              checked={formData.isSystemUser}
              onChange={(e) => updateField('isSystemUser', e.target.checked)}
            />
            <label htmlFor="isSystemUser" className="flex flex-col cursor-pointer">
              <span className="text-[0.7rem] font-black text-primary uppercase tracking-tight">
                System User
              </span>
              <span className="text-[0.6rem] text-text-muted font-bold">
                Prevents this user from being deleted.
              </span>
            </label>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <Button variant="ghost" onClick={adminUserModal.close}>
              Cancel
            </Button>
            <Button onClick={handleSave} isLoading={isFormSaving}>
              {formData.id ? 'Update System Admin' : 'Add System Admin'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* User Modal for Organization Users */}
      <Modal
        isOpen={orgUserModal.isOpen}
        onClose={orgUserModal.close}
        title={formData.id ? 'Edit Organization User' : 'Add New Organization User'}
      >
        <div className="space-y-4 py-2">
          <p className="text-[0.6rem] text-text-muted font-medium -mt-2 mb-2">
            <span className="text-danger">*</span> All fields are required
          </p>
          <p className="text-[0.65rem] text-primary bg-primary/10 border border-primary/20 rounded-lg p-2 font-semibold">
            Organization: <strong>{currentOrganization?.name || 'Select Organization'}</strong>
          </p>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Username *"
              value={formData.username}
              onChange={(e) => updateField('username', e.target.value)}
              placeholder="e.g. john.doe"
              required
            />
            <Input
              label="Full Name *"
              value={formData.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="John Doe"
              required
            />
          </div>
          <Input
            label="Email Address *"
            value={formData.email}
            onChange={(e) => updateField('email', e.target.value)}
            placeholder="john@enterprise.com"
            type="email"
            required
          />
          <div className="space-y-1.5">
            <label className="text-[0.6rem] font-black text-text-muted uppercase tracking-widest ml-1">
              Organization Role <span className="text-danger">*</span>
            </label>
            <select
              className="w-full bg-muted-bg border-none rounded-lg p-2.5 font-black text-xs text-text-primary focus:ring-2 focus:ring-primary/20 outline-none"
              value={formData.role}
              onChange={(e) => updateField('role', e.target.value)}
              required
            >
              <option value="Employee">Employee</option>
              <option value="Manager">Manager</option>
              <option value="HRExecutive">HR Executive</option>
              <option value="HRManager">HR Manager</option>
            </select>
            <p className="text-[0.55rem] text-text-muted font-medium mt-1">
              Super Admin is automatically created when organization is created. Org users can only
              be: Employee, Manager, HR Executive, or HR Manager.
            </p>
          </div>
          {!formData.id && (
            <Input
              label="Temporary Password *"
              type="password"
              value={formData.password}
              onChange={(e) => updateField('password', e.target.value)}
              placeholder="••••••••"
              required
            />
          )}

          <div className="flex justify-end gap-3 mt-6">
            <Button variant="ghost" onClick={orgUserModal.close}>
              Cancel
            </Button>
            <Button onClick={handleSave} isLoading={isFormSaving}>
              {formData.id ? 'Update User' : 'Add User'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default UserManagement;
