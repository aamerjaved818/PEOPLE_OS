/**
 * Team Directory
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { selfServiceApi } from '@/services/selfServiceApi';
import { Card } from '@/components/ui/Card';
import { SearchInput } from '@/components/ui/SearchInput';

export const TeamDirectory: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const { data: team, isLoading } = useQuery({
    queryKey: ['teamDirectory'],
    queryFn: () => selfServiceApi.getTeamDirectory(),
  });

  const filteredTeam = team?.filter(
    (member) =>
      member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.department?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Team Directory</h1>

      <div className="mb-6">
        <SearchInput
          placeholder="Search by name, email, or department..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="text-center py-12">Loading...</div>
      ) : filteredTeam && filteredTeam.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTeam.map((member) => (
            <Card key={member.id} className="hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start space-x-4">
                  {member.profilePhotoUrl ? (
                    <img
                      src={member.profilePhotoUrl}
                      alt={member.name}
                      className="w-16 h-16 rounded-full object-cover border-2 border-blue-500"
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-full bg-blue-500 flex items-center justify-center text-white text-xl font-bold flex-shrink-0">
                      {member.name.charAt(0)}
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-gray-900 truncate">{member.name}</h3>
                    <p className="text-sm text-gray-600 truncate">{member.designation}</p>
                    <p className="text-sm text-gray-500 truncate">{member.department}</p>
                  </div>
                </div>

                {member.bio && (
                  <p className="mt-4 text-sm text-gray-700 line-clamp-2">{member.bio}</p>
                )}

                <div className="mt-4 space-y-2">
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="mr-2">📧</span>
                    <a href={`mailto:${member.email}`} className="hover:underline truncate">
                      {member.email}
                    </a>
                  </div>
                  {member.phone && (
                    <div className="flex items-center text-sm text-gray-600">
                      <span className="mr-2">📞</span>
                      <span className="truncate">{member.phone}</span>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <div className="p-12 text-center text-gray-500">
            {searchTerm ? 'No team members found matching your search' : 'No team members found'}
          </div>
        </Card>
      )}
    </div>
  );
};
