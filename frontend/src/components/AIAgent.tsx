
import React, { useState, useRef, useEffect } from 'react';
import { Send, ThumbsUp, ThumbsDown, Bot, User, Paperclip } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { useAuth } from '@/contexts/AuthContext';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  feedback?: 'positive' | 'negative';
}

const AIAgent = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: `Salut ${user?.name}! Sunt asistentul tău virtual pentru administrația publică. Cu ce te pot ajuta astăzi?`,
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputValue);
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: aiResponse,
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000);
  };

  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('certificat') || input.includes('urbanism')) {
      return 'Pentru a obține un certificat de urbanism, aveți nevoie de: 1) Cererea completată, 2) Planul cadastral, 3) Taxa aferentă. Documentele se pot depune online prin secțiunea "Documente Auto" sau la ghișeu. Termenul de solutionare este de 30 de zile lucrătoare.';
    }
    
    if (input.includes('taxe') || input.includes('impozit')) {
      return 'Informațiile despre taxele locale le găsiți în arhiva de documente. Plata se poate face online, la ghișeu sau prin virament bancar. Pentru întrebări specifice despre calculul taxelor, vă recomand să consultați secțiunea dedicată din profilul dumneavoastră.';
    }
    
    if (input.includes('acte') || input.includes('documente')) {
      return 'Pentru gestionarea documentelor personale, accesați secțiunea "Profil". Acolo puteți încărca și verifica documentele de identitate. Pentru documente oficiale, verificați "Arhiva Documente" unde găsiți toate formularele necesare.';
    }
    
    if (input.includes('programare') || input.includes('ghișeu')) {
      return 'Pentru programări la ghișeu, contactați numărul 021.XXX.XXXX sau folosiți sistemul online de programări. Orarul este Luni-Vineri 8:00-16:00. Multe servicii pot fi realizate complet online prin această platformă.';
    }
    
    return 'Înțeleg întrebarea dumneavoastră. Pentru informații detaliate, vă recomand să consultați arhiva de documente sau să contactați direct serviciul competent. Pot să vă ajut cu informații despre proceduri administrative, documente necesare sau să vă ghidez prin platformă.';
  };

  const handleFeedback = (messageId: string, type: 'positive' | 'negative') => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, feedback: type } : msg
    ));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Avatar className="h-10 w-10">
              <AvatarImage src="/bot-avatar.png" />
              <AvatarFallback className="bg-primary-500 text-white">
                <Bot className="h-6 w-6" />
              </AvatarFallback>
            </Avatar>
            <div className="absolute -bottom-1 -right-1 h-4 w-4 bg-green-500 rounded-full border-2 border-white animate-pulse-slow"></div>
          </div>
          <div>
            <h1 className="text-lg font-semibold">Asistent Virtual</h1>
            <p className="text-sm text-gray-600">Online • Răspunde în câteva secunde</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-3xl ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'} space-x-3`}>
              <Avatar className="h-8 w-8 flex-shrink-0">
                {message.sender === 'user' ? (
                  <>
                    <AvatarImage src={user?.avatar} />
                    <AvatarFallback>
                      <User className="h-4 w-4" />
                    </AvatarFallback>
                  </>
                ) : (
                  <>
                    <AvatarImage src="/bot-avatar.png" />
                    <AvatarFallback className="bg-primary-500 text-white">
                      <Bot className="h-4 w-4" />
                    </AvatarFallback>
                  </>
                )}
              </Avatar>
              
              <div className={`flex flex-col ${message.sender === 'user' ? 'items-end' : 'items-start'}`}>
                <Card className={`${message.sender === 'user' 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-white'
                } shadow-sm`}>
                  <CardContent className="p-3">
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </CardContent>
                </Card>
                
                <div className="flex items-center mt-1 space-x-2">
                  <span className="text-xs text-gray-500">
                    {message.timestamp.toLocaleTimeString('ro-RO', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </span>
                  
                  {message.sender === 'ai' && (
                    <div className="flex space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`h-6 w-6 p-0 ${
                          message.feedback === 'positive' 
                            ? 'text-green-600 bg-green-100' 
                            : 'text-gray-400 hover:text-green-600'
                        }`}
                        onClick={() => handleFeedback(message.id, 'positive')}
                      >
                        <ThumbsUp className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`h-6 w-6 p-0 ${
                          message.feedback === 'negative' 
                            ? 'text-red-600 bg-red-100' 
                            : 'text-gray-400 hover:text-red-600'
                        }`}
                        onClick={() => handleFeedback(message.id, 'negative')}
                      >
                        <ThumbsDown className="h-3 w-3" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="flex space-x-3 max-w-3xl">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-primary-500 text-white">
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <Card className="bg-white shadow-sm">
                <CardContent className="p-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <Button
            variant="ghost"
            size="sm"
            className="flex-shrink-0"
          >
            <Paperclip className="h-4 w-4" />
          </Button>
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Scrie întrebarea ta aici..."
            className="flex-1"
            disabled={isTyping}
          />
          <Button 
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            className="flex-shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Asistentul virtual poate face greșeli. Verifică informațiile importante.
        </p>
      </div>
    </div>
  );
};

export default AIAgent;
