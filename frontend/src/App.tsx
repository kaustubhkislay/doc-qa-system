import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const handleUploadComplete = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Document Q&A
          </h1>
          <p className="text-sm text-gray-600">
            Upload PDFs and ask questions about their content
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Upload & Documents */}
          <div className="space-y-6">
            <DocumentUpload onUploadComplete={handleUploadComplete} />
            <DocumentList
              refreshTrigger={refreshTrigger}
              selectedIds={selectedIds}
              onSelectionChange={setSelectedIds}
            />
          </div>

          {/* Right Column: Chat */}
          <div className="lg:col-span-2">
            <ChatInterface selectedDocumentIds={selectedIds} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;