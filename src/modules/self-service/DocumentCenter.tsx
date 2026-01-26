/**
 * Document Center - Document Requests & Library
 */
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { selfServiceApi } from '@/services/selfServiceApi';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { toast } from '@/components/ui/Toast';
import { Tabs } from '@/components/ui/Tabs';

export const DocumentCenter: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState('my-documents');

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Document Center</h1>

      <Tabs
        tabs={[
          { id: 'my-documents', label: 'My Documents', content: <DocumentLibrary /> },
          { id: 'request-document', label: 'Request Document', content: <DocumentRequests /> },
        ]}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
    </div>
  );
};

const DocumentLibrary: React.FC = () => {
  const { data: documents, isLoading } = useQuery({
    queryKey: ['myDocuments'],
    queryFn: selfServiceApi.getMyDocuments,
  });

  if (isLoading) {
    return <div className="py-8 text-center">Loading...</div>;
  }

  return (
    <div className="space-y-4">
      <p className="text-gray-600">View and download your uploaded documents</p>

      {documents && documents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map((doc) => (
            <Card key={doc.id} className="hover:shadow-lg transition-shadow">
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <span className="text-3xl mb-2 block">📄</span>
                    <h3 className="font-semibold text-gray-900 truncate">{doc.documentName}</h3>
                    <p className="text-sm text-gray-500">{doc.documentType}</p>
                  </div>
                </div>

                <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                  <span>{new Date(doc.uploadDate).toLocaleDateString()}</span>
                  {doc.fileSize && <span>{(doc.fileSize / 1024).toFixed(0)} KB</span>}
                </div>

                <Button
                  className="mt-3 w-full"
                  variant="outline"
                  size="sm"
                  onClick={() => window.open(doc.documentUrl, '_blank')}
                >
                  View Document
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <div className="p-12 text-center">
            <p className="text-gray-500 text-lg mb-4">No documents uploaded yet</p>
            <p className="text-sm text-gray-400">Documents uploaded by HR will appear here</p>
          </div>
        </Card>
      )}
    </div>
  );
};

const DocumentRequests: React.FC = () => {
  const queryClient = useQueryClient();
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [formData, setFormData] = useState({
    documentType: '',
    purpose: '',
    additionalNotes: '',
  });

  const { data: requests, isLoading } = useQuery({
    queryKey: ['myDocumentRequests'],
    queryFn: selfServiceApi.getMyDocumentRequests,
  });

  const requestMutation = useMutation({
    mutationFn: selfServiceApi.requestDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myDocumentRequests'] });
      toast.success('Document request submitted');
      setShowRequestForm(false);
      setFormData({ documentType: '', purpose: '', additionalNotes: '' });
    },
  });

  const documentTypes = [
    'Experience Letter',
    'Salary Certificate',
    'Employment Verification',
    'Tax Certificate',
    'No Objection Certificate',
  ];

  if (isLoading) {
    return <div className="py-8 text-center">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <p className="text-gray-600">Request official documents from HR</p>
        <Button onClick={() => setShowRequestForm(!showRequestForm)}>
          {showRequestForm ? 'Cancel' : '+ New Request'}
        </Button>
      </div>

      {showRequestForm && (
        <Card>
          <div className="p-6 space-y-4">
            <h3 className="text-lg font-semibold">Request Document</h3>

            <div>
              <label className="block text-sm font-medium mb-2">Document Type</label>
              <select
                className="w-full border rounded-md p-2"
                value={formData.documentType}
                onChange={(e) => setFormData((prev) => ({ ...prev, documentType: e.target.value }))}
              >
                <option value="">Select document type</option>
                {documentTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            <Input
              label="Purpose"
              placeholder="Why do you need this document?"
              value={formData.purpose}
              onChange={(e) => setFormData((prev) => ({ ...prev, purpose: e.target.value }))}
            />

            <div>
              <label className="block text-sm font-medium mb-2">Additional Notes (Optional)</label>
              <textarea
                className="w-full border rounded-md p-2 min-h-[80px]"
                placeholder="Any additional information..."
                value={formData.additionalNotes}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, additionalNotes: e.target.value }))
                }
              />
            </div>

            <Button
              onClick={() => requestMutation.mutate(formData)}
              disabled={!formData.documentType || requestMutation.isPending}
              className="w-full"
            >
              Submit Request
            </Button>
          </div>
        </Card>
      )}

      {/* Request History */}
      <div>
        <h3 className="text-lg font-semibold mb-4">My Requests</h3>
        {requests && requests.length > 0 ? (
          <div className="space-y-3">
            {requests.map((request) => (
              <Card key={request.id}>
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900">{request.documentType}</h4>
                      <p className="text-sm text-gray-600 mt-1">{request.purpose}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        Requested: {new Date(request.requestedDate).toLocaleDateString()}
                      </p>
                    </div>
                    <StatusBadge status={request.status} />
                  </div>

                  {request.documentUrl && (
                    <Button
                      className="mt-3"
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(request.documentUrl, '_blank')}
                    >
                      Download Document
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <div className="p-8 text-center text-gray-500">No document requests yet</div>
          </Card>
        )}
      </div>
    </div>
  );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const colors = {
    Pending: 'bg-yellow-100 text-yellow-800',
    Approved: 'bg-green-100 text-green-800',
    Ready: 'bg-blue-100 text-blue-800',
    Rejected: 'bg-red-100 text-red-800',
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-medium ${colors[status as keyof typeof colors] || colors.Pending}`}
    >
      {status}
    </span>
  );
};
