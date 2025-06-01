import { AlertCircle, Bot, Loader2, MessageCircle, Send } from 'lucide-react';
import React, { useState } from 'react';

const AISidebar = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const sendQuery = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');
    setResponse('');

    try {
      const res = await fetch('/api/ai/agent/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          // Optional: customize config for specific needs
          config: {
            web_search: { city_hint: 'timisoara' },
            // timpark_payment: { use_timpark_payment: false } // Disable if needed
          }
        }),
      });

      const data = await res.json();

      if (data.success) {
        setResponse(data.response);
      } else {
        setError(data.error || 'Failed to get response');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('AI query error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendQuery();
    }
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-all duration-200 z-50"
      >
        <Bot size={24} />
      </button>

      {/* Sidebar */}
      <div className={`fixed top-0 right-0 h-full w-96 bg-white shadow-xl transform transition-transform duration-300 z-40 ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
        
        {/* Header */}
        <div className="bg-blue-600 text-white p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot size={20} />
            <h2 className="font-semibold">AI Assistant</h2>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="text-white hover:text-gray-200"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-col h-full">
          
          {/* Welcome Message */}
          <div className="p-4 bg-gray-50 border-b">
            <div className="flex items-start gap-2">
              <MessageCircle size={16} className="text-blue-600 mt-1" />
              <div>
                <p className="text-sm text-gray-700">
                  Salut! Sunt asistentul AI pentru informații civice în România. 
                  Pot să te ajut cu:
                </p>
                <ul className="text-xs text-gray-600 mt-2 ml-2">
                  <li>• Taxe și impozite</li>
                  <li>• Proceduri administrative</li>
                  <li>• Plata parcării în Timișoara</li>
                  <li>• Informații despre instituții publice</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Response Area */}
          <div className="flex-1 p-4 overflow-y-auto">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <div className="flex items-start gap-2">
                  <AlertCircle size={16} className="text-red-600 mt-0.5" />
                  <div>
                    <p className="text-sm text-red-800 font-medium">Eroare</p>
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {response && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                <div className="flex items-start gap-2">
                  <Bot size={16} className="text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-sm text-blue-800 font-medium">Răspuns</p>
                    <div className="text-sm text-blue-700 mt-1 whitespace-pre-wrap">
                      {response}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {isLoading && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4">
                <div className="flex items-center gap-2">
                  <Loader2 size={16} className="text-gray-600 animate-spin" />
                  <p className="text-sm text-gray-600">Procesez întrebarea...</p>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-4 border-t bg-gray-50">
            <div className="flex gap-2">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Întreabă-mă orice despre servicii publice în România..."
                className="flex-1 p-2 border border-gray-300 rounded-lg text-sm resize-none"
                rows="2"
                disabled={isLoading}
              />
              <button
                onClick={sendQuery}
                disabled={isLoading || !query.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              >
                {isLoading ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Send size={16} />
                )}
              </button>
            </div>
            
            {/* Quick Examples */}
            <div className="mt-2">
              <p className="text-xs text-gray-500 mb-1">Exemple rapide:</p>
              <div className="flex flex-wrap gap-1">
                {[
                  "Taxe locuință Timișoara",
                  "Plătesc parcarea 2 ore",
                  "Înnoirea pașaportului"
                ].map((example) => (
                  <button
                    key={example}
                    onClick={() => setQuery(example)}
                    className="text-xs bg-white border border-gray-200 rounded px-2 py-1 hover:bg-gray-50 transition-colors"
                    disabled={isLoading}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

 