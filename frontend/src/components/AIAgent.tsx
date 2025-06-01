import {
  AgentQueryRequest,
  AgentQueryResponse,
  sendAgentQuery,
} from "@/api/aiApi";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import {
  AlertCircle,
  Bot,
  Loader2,
  Send,
  ThumbsDown,
  ThumbsUp,
  User,
} from "lucide-react";
import React, { useEffect, useRef, useState } from "react";

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
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: `Salut ${user?.name}! Sunt asistentul tău virtual pentru administrația publică. Cu ce te pot ajuta astăzi?`,
      sender: "ai",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
      // Prepare agent query request
      const request: AgentQueryRequest = {
        query: currentQuery,
        config: {
          web_search: {
            city_hint: "timisoara",
            search_context_size: "high",
          },
          timpark_payment: {
            use_timpark_payment: true,
          },
        },
      };

      // Send query to real AI agent
      const response: AgentQueryResponse = await sendAgentQuery(request);

      // Create AI response message
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.success
          ? response.response
          : response.error || "Ne pare rău, a apărut o eroare.",
        sender: "ai",
        timestamp: new Date(),
        tools_used: response.tools_used,
        timpark_executed: response.timpark_executed,
        processing_time: response.processing_time,
      };

      setMessages((prev) => [...prev, aiMessage]);

      // Show error if agent failed
      if (!response.success) {
        setError(
          response.error || "A apărut o eroare în procesarea întrebării."
        );
      }
    } catch (err) {
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
            <p className="text-sm text-gray-600">
              Online • Răspunde în câteva secunde
            </p>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 p-3">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <p className="text-sm text-red-700">{error}</p>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setError("")}
              className="ml-auto h-6 w-6 p-0 text-red-600 hover:text-red-800"
            >
              ✕
            </Button>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
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
                    <AvatarFallback className="bg-primary-500 text-white">
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
                      ? "bg-primary-500 text-white"
                      : "bg-white"
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
                          <span>• {message.processing_time.toFixed(1)}s</span>
                        )}
                        {message.timpark_executed && (
                          <span className="text-green-600">
                            • TimPark executat
                          </span>
                        )}
                        {message.tools_used &&
                          message.tools_used.length > 0 && (
                            <span title={formatToolsUsed(message.tools_used)}>
                              • {message.tools_used.length} instrumente
                            </span>
                          )}
                      </div>
                    )}

                  {message.sender === "ai" && (
                    <div className="flex space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`h-6 w-6 p-0 ${
                          message.feedback === "positive"
                            ? "text-green-600 bg-green-100"
                            : "text-gray-400 hover:text-green-600"
                        }`}
                        onClick={() => handleFeedback(message.id, "positive")}
                      >
                        <ThumbsUp className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`h-6 w-6 p-0 ${
                          message.feedback === "negative"
                            ? "text-red-600 bg-red-100"
                            : "text-gray-400 hover:text-red-600"
                        }`}
                        onClick={() => handleFeedback(message.id, "negative")}
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
              <Avatar className="h-8 w-8 flex-shrink-0">
                <AvatarImage src="/bot-avatar.png" />
                <AvatarFallback className="bg-primary-500 text-white">
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>

              <Card className="bg-white shadow-sm">
                <CardContent className="p-3">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                    <span className="text-sm text-gray-600">
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

      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex space-x-2">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Întreabă-mă orice despre servicii publice..."
            className="flex-1"
            disabled={isTyping}
          />
          <Button
            onClick={handleSendMessage}
            disabled={isTyping || !inputValue.trim()}
            className="px-4"
          >
            {isTyping ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Quick suggestions */}
        <div className="mt-2 flex flex-wrap gap-2">
          {[
            "Taxe locuință Timișoara",
            "Plătesc parcarea 2 ore",
            "Înnoirea pașaportului",
            "Certificat de urbanism",
          ].map((suggestion) => (
            <Button
              key={suggestion}
              variant="outline"
              size="sm"
              onClick={() => setInputValue(suggestion)}
              disabled={isTyping}
              className="text-xs"
            >
              {suggestion}
            </Button>
          ))}
        </div>

        <p className="text-xs text-gray-500 mt-2 text-center">
          Asistentul virtual poate face greșeli. Verifică informațiile
          importante.
        </p>
      </div>
    </div>
  );
};

export default AIAgent;
