import {
  getChatSession,
  sendChatMessage,
  type ChatMessage as ApiChatMessage,
  type ChatSessionWithMessages,
} from "@/api/aiApi";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import {
  AlertCircle,
  Bot,
  History,
  Loader2,
  Send,
  Settings,
  ThumbsDown,
  ThumbsUp,
  User,
} from "lucide-react";
import React, { useEffect, useRef, useState } from "react";
import AIAgentSettings from "./AIAgentSettings";
import ChatHistorySidebar from "./ChatHistorySidebar";

interface Message {
  id: string;
  content: string;
  sender: "user" | "ai";
  timestamp: Date;
  feedback?: "positive" | "negative";
  tools_used?: string[];
  timpark_executed?: boolean;
  processing_time?: number;
}

const AIAgent = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string>("");
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [isLoadingSession, setIsLoadingSession] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initialize with welcome message when no session is selected
    if (!currentSessionId) {
      setMessages([
        {
          id: "welcome",
          content: `Salut ${user?.name}! Sunt asistentul tău virtual pentru administrația publică din România. Cu ce te pot ajuta astăzi?\n\nPoți să mă întrebi despre:\n• Taxe și impozite locale\n• Proceduri administrative\n• Plata parcării TimPark în Timișoara\n• Informații de pe site-uri guvernamentale\n• Și multe altele!`,
          sender: "ai",
          timestamp: new Date(),
        },
      ]);
    }
  }, [user?.name, currentSessionId]);

  const loadSession = async (sessionId: number) => {
    try {
      setIsLoadingSession(true);
      setError("");

      const sessionData: ChatSessionWithMessages = await getChatSession(
        sessionId
      );

      // Convert API messages to component message format
      const convertedMessages: Message[] = sessionData.messages.map(
        (msg: ApiChatMessage) => ({
          id: msg.id.toString(),
          content: msg.content,
          sender: msg.role === "user" ? "user" : "ai",
          timestamp: new Date(msg.timestamp),
          tools_used: msg.tools_used || undefined,
          processing_time: msg.processing_time
            ? msg.processing_time / 1000
            : undefined, // Convert to seconds
        })
      );

      setMessages(convertedMessages);
      setCurrentSessionId(sessionId);
    } catch (error) {
      console.error("Error loading session:", error);
      setError("Nu am putut încărca conversația. Încearcă din nou.");
    } finally {
      setIsLoadingSession(false);
    }
  };

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
    setError("");
    // Welcome message will be set by useEffect
  };

  const handleSessionSelect = (sessionId: number) => {
    if (sessionId !== currentSessionId) {
      loadSession(sessionId);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentQuery = inputValue;
    setInputValue("");
    setIsTyping(true);
    setError("");

    try {
      // Send message via chat API (creates session if needed)
      const response = await sendChatMessage(
        currentQuery,
        currentSessionId || undefined,
        !currentSessionId // Create new session if none exists
      );

      if (response.success === false) {
        throw new Error(response.error || "Eroare în procesarea mesajului");
      }

      // Update current session ID if a new session was created
      if (!currentSessionId && response.session) {
        setCurrentSessionId(response.session.id);
      }

      // Extract AI response data
      const aiResponseMessage = response.message;
      const agentExecution = response.agent_execution;

      // Create AI response message
      const aiMessage: Message = {
        id: aiResponseMessage.id.toString(),
        content: aiResponseMessage.content,
        sender: "ai",
        timestamp: new Date(aiResponseMessage.timestamp),
        tools_used: aiResponseMessage.tools_used || undefined,
        processing_time: aiResponseMessage.processing_time
          ? aiResponseMessage.processing_time / 1000
          : undefined,
        timpark_executed: agentExecution?.timpark_result ? true : false,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err: any) {
      console.error("Error sending message to AI agent:", err);

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content:
          "Ne pare rău, nu am putut procesa întrebarea în acest moment. Vă rugăm să încercați din nou.",
        sender: "ai",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      setError(
        err.message ||
          "Eroare de conectare la serviciul AI. Verificați conexiunea la internet."
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleFeedback = (messageId: string, type: "positive" | "negative") => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, feedback: type } : msg
      )
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatToolsUsed = (tools: string[] = []) => {
    const toolNames: Record<string, string> = {
      query_reformulation: "Reformulare întrebare",
      timpark_payment: "Plată TimPark",
      web_search: "Căutare web",
      trusted_sites_search: "Site-uri oficiale",
      final_response_generation: "Sinteză finală",
    };

    return tools.map((tool) => toolNames[tool] || tool).join(", ");
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* History Sidebar */}
      {showHistory && (
        <div className="w-80 border-r border-gray-200 bg-white">
          <ChatHistorySidebar
            currentSessionId={currentSessionId || undefined}
            onSessionSelect={handleSessionSelect}
            onNewChat={handleNewChat}
          />
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Avatar className="h-10 w-10">
                <AvatarImage src="/bot-avatar.png" />
                <AvatarFallback className="bg-blue-600 text-white">
                  <Bot className="h-6 w-6" />
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-lg font-semibold text-blue-900">
                  Asistent Virtual România
                </h1>
                <p className="text-sm text-blue-600">
                  {currentSessionId
                    ? `Conversația #${currentSessionId}`
                    : "Administrație publică și servicii civice"}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                onClick={() => setShowHistory(!showHistory)}
                className="border-blue-300 text-blue-700 hover:bg-blue-50"
              >
                <History className="h-4 w-4 mr-2" />
                {showHistory ? "Ascunde" : "Istoric"}
              </Button>

              <Button
                variant="outline"
                onClick={() => setShowSettings(true)}
                className="border-blue-300 text-blue-700 hover:bg-blue-50"
              >
                <Settings className="h-4 w-4 mr-2" />
                Setări
              </Button>
            </div>
          </div>

          {error && (
            <div className="mt-3 bg-red-50 border border-red-200 rounded-lg p-3 flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
        </div>

        {/* Loading indicator for session */}
        {isLoadingSession && (
          <div className="flex-1 flex items-center justify-center">
            <div className="flex items-center space-x-2 text-blue-600">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span>Se încarcă conversația...</span>
            </div>
          </div>
        )}

        {/* Messages */}
        {!isLoadingSession && (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex max-w-3xl ${
                    message.sender === "user" ? "flex-row-reverse" : "flex-row"
                  } space-x-3`}
                >
                  <Avatar className="h-8 w-8 flex-shrink-0">
                    {message.sender === "user" ? (
                      <>
                        <AvatarImage src={user?.avatar} />
                        <AvatarFallback>
                          <User className="h-4 w-4" />
                        </AvatarFallback>
                      </>
                    ) : (
                      <>
                        <AvatarImage src="/bot-avatar.png" />
                        <AvatarFallback className="bg-blue-600 text-white">
                          <Bot className="h-4 w-4" />
                        </AvatarFallback>
                      </>
                    )}
                  </Avatar>

                  <div
                    className={`flex flex-col ${
                      message.sender === "user" ? "items-end" : "items-start"
                    }`}
                  >
                    <Card
                      className={`${
                        message.sender === "user"
                          ? "bg-blue-600 text-white"
                          : "bg-white border-blue-200"
                      } shadow-sm`}
                    >
                      <CardContent className="p-3">
                        <p className="text-sm whitespace-pre-wrap">
                          {message.content}
                        </p>
                      </CardContent>
                    </Card>

                    <div className="flex items-center mt-1 space-x-2">
                      <span className="text-xs text-gray-500">
                        {message.timestamp.toLocaleTimeString("ro-RO", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>

                      {/* Show AI info */}
                      {message.sender === "ai" &&
                        (message.tools_used || message.processing_time) && (
                          <div className="text-xs text-gray-400 flex items-center gap-1">
                            {message.processing_time && (
                              <span>
                                • {message.processing_time.toFixed(1)}s
                              </span>
                            )}
                            {message.timpark_executed && (
                              <span className="text-green-600">
                                • TimPark executat
                              </span>
                            )}
                            {message.tools_used &&
                              message.tools_used.length > 0 && (
                                <span
                                  title={formatToolsUsed(message.tools_used)}
                                >
                                  • {message.tools_used.length} instrumente
                                </span>
                              )}
                          </div>
                        )}

                      {/* Feedback buttons for AI messages */}
                      {message.sender === "ai" && (
                        <div className="flex space-x-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              handleFeedback(message.id, "positive")
                            }
                            className={`h-6 w-6 p-0 ${
                              message.feedback === "positive"
                                ? "text-green-600"
                                : "text-gray-400 hover:text-green-600"
                            }`}
                          >
                            <ThumbsUp className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              handleFeedback(message.id, "negative")
                            }
                            className={`h-6 w-6 p-0 ${
                              message.feedback === "negative"
                                ? "text-red-600"
                                : "text-gray-400 hover:text-red-600"
                            }`}
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

            {/* Typing indicator */}
            {isTyping && (
              <div className="flex justify-start">
                <div className="flex space-x-3">
                  <Avatar className="h-8 w-8 flex-shrink-0">
                    <AvatarImage src="/bot-avatar.png" />
                    <AvatarFallback className="bg-blue-600 text-white">
                      <Bot className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                  <Card className="bg-white border-blue-200 shadow-sm">
                    <CardContent className="p-3">
                      <div className="flex items-center space-x-1">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-75"></div>
                          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-150"></div>
                        </div>
                        <span className="text-xs text-blue-600 ml-2">
                          Procesez întrebarea...
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input area */}
        {!isLoadingSession && (
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="flex items-center space-x-2">
              <div className="flex-1 relative">
                <Input
                  ref={inputRef}
                  type="text"
                  placeholder="Scrie întrebarea ta aici..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isTyping}
                  className="pr-12 border-blue-300 focus:border-blue-500 focus:ring-blue-500"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className="absolute right-1 top-1 h-8 w-8 p-0 bg-blue-600 hover:bg-blue-700"
                >
                  {isTyping ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <p className="text-xs text-gray-500 mt-2 text-center">
              Apasă Enter pentru a trimite mesajul •
              {currentSessionId
                ? ` Conversația #${currentSessionId}`
                : " Conversație nouă"}
            </p>
          </div>
        )}
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <AIAgentSettings
          onClose={() => setShowSettings(false)}
          onSave={(configs) => {
            console.log("Agent configurations saved:", configs);
            setShowSettings(false);
          }}
        />
      )}
    </div>
  );
};

export default AIAgent;
