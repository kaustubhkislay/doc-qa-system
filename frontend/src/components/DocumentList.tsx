import { useEffect, useState } from 'react';
import { FileText, Trash2, Check } from 'lucide-react';
import { documentsApi } from '../api/client';
import type { Document } from '../api/client';

interface Props {
  refreshTrigger: number;
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
}

export default function DocumentList({ 
  refreshTrigger, 
  selectedIds, 
  onSelectionChange 
}: Props) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDocuments();
  }, [refreshTrigger]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await documentsApi.list();
      setDocuments(data.documents);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this document?')) return;
    
    try {
      await documentsApi.delete(id);
      onSelectionChange(selectedIds.filter(sid => sid !== id));
      loadDocuments();
    } catch (err) {
      console.error(err);
      alert('Failed to delete document');
    }
  };

  const toggleSelection = (id: string) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter(sid => sid !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500">Loading documents...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold mb-4">Your Documents</h2>
      
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      
      {documents.length === 0 ? (
        <p className="text-gray-500 text-sm">
          No documents uploaded yet. Upload a PDF to get started.
        </p>
      ) : (
        <div className="space-y-2">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className={`flex items-center gap-3 p-3 rounded-lg border transition-colors cursor-pointer ${
                selectedIds.includes(doc.id)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => toggleSelection(doc.id)}
            >
              <div className={`flex-shrink-0 w-5 h-5 rounded border flex items-center justify-center ${
                selectedIds.includes(doc.id)
                  ? 'bg-blue-600 border-blue-600'
                  : 'border-gray-300'
              }`}>
                {selectedIds.includes(doc.id) && (
                  <Check size={14} className="text-white" />
                )}
              </div>
              
              <FileText size={20} className="text-blue-600 flex-shrink-0" />
              
              <div className="flex-grow min-w-0">
                <p className="font-medium truncate">{doc.title}</p>
                <p className="text-sm text-gray-500">
                  {doc.page_count} pages • {doc.filename}
                </p>
              </div>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(doc.id);
                }}
                className="p-2 text-gray-400 hover:text-red-600 transition-colors"
              >
                <Trash2 size={18} />
              </button>
            </div>
          ))}
        </div>
      )}
      
      {selectedIds.length > 0 && (
        <p className="mt-4 text-sm text-blue-600">
          {selectedIds.length} document(s) selected for search
        </p>
      )}
    </div>
  );
}