import {
  createChatSession,
  deleteChatSession,
  getChatSessions,
  updateChatSession,
  type ChatSessionListItem,
} from "@/api/aiApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { formatDistanceToNow } from "date-fns";
import { ro } from "date-fns/locale";
import {
  Calendar,
  Check,
  Clock,
  Edit2,
  MessageSquare,
  Plus,
  Search,
  Trash2,
  X,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import ChatStatsCard from "./ChatStatsCard";

interface ChatHistorySidebarProps {
  currentSessionId?: number;
  onSessionSelect: (sessionId: number) => void;
  onNewChat: () => void;
  className?: string;
}

const ChatHistorySidebar: React.FC<ChatHistorySidebarProps> = ({
  currentSessionId,
  onSessionSelect,
  onNewChat,
  className = "",
}) => {
  const [sessions, setSessions] = useState<ChatSessionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [editingSession, setEditingSession] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const sessionsData = await getChatSessions(false, 50);
      setSessions(sessionsData || []);
    } catch (error) {
      console.error("Error loading chat sessions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSession = await createChatSession();
      await loadSessions(); // Refresh list
      onNewChat();
      onSessionSelect(newSession.id);
    } catch (error) {
      console.error("Error creating new chat:", error);
    }
  };

  const handleDeleteSession = async (
    sessionId: number,
    event: React.MouseEvent
  ) => {
    event.stopPropagation();
    if (window.confirm("Ești sigur că vrei să ștergi această conversație?")) {
      try {
        await deleteChatSession(sessionId);
        await loadSessions(); // Refresh list

        // If deleting current session, start new chat
        if (sessionId === currentSessionId) {
          onNewChat();
        }
      } catch (error) {
        console.error("Error deleting session:", error);
      }
    }
  };

  const handleEditSession = (
    sessionId: number,
    currentTitle: string,
    event: React.MouseEvent
  ) => {
    event.stopPropagation();
    setEditingSession(sessionId);
    setEditTitle(currentTitle || "");
  };

  const handleSaveEdit = async (sessionId: number) => {
    try {
      await updateChatSession(sessionId, { title: editTitle });
      await loadSessions(); // Refresh list
      setEditingSession(null);
    } catch (error) {
      console.error("Error updating session title:", error);
    }
  };

  const handleCancelEdit = () => {
    setEditingSession(null);
    setEditTitle("");
  };

  const filteredSessions = sessions.filter((session) =>
    (session.title || "Conversație nouă")
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  const formatLastMessageTime = (timestamp?: string) => {
    if (!timestamp) return "";
    try {
      return formatDistanceToNow(new Date(timestamp), {
        addSuffix: true,
        locale: ro,
      });
    } catch {
      return "";
    }
  };

  return (
    <div className={`h-full flex flex-col ${className}`}>
      <Card className="flex-1 flex flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-blue-900">
            <MessageSquare className="h-5 w-5" />
            Conversații
          </CardTitle>

          {/* New Chat Button */}
          <Button
            onClick={handleNewChat}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Plus className="h-4 w-4 mr-2" />
            Conversație nouă
          </Button>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-500 h-4 w-4" />
            <Input
              placeholder="Caută conversații..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 border-blue-300 focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-0">
          {loading ? (
            <div className="p-4 text-center text-blue-600">
              Se încarcă conversațiile...
            </div>
          ) : filteredSessions.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              {searchTerm
                ? "Nicio conversație găsită"
                : "Încă nu ai conversații"}
            </div>
          ) : (
            <div className="space-y-1 p-2">
              {filteredSessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => onSessionSelect(session.id)}
                  className={`
                    group cursor-pointer rounded-lg p-3 hover:bg-blue-50 transition-colors
                    ${
                      currentSessionId === session.id
                        ? "bg-blue-100 border-l-4 border-blue-600"
                        : "hover:bg-blue-25"
                    }
                  `}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      {editingSession === session.id ? (
                        <div className="flex items-center gap-1">
                          <Input
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            className="text-sm h-7"
                            onKeyDown={(e) => {
                              if (e.key === "Enter") handleSaveEdit(session.id);
                              if (e.key === "Escape") handleCancelEdit();
                            }}
                            autoFocus
                          />
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleSaveEdit(session.id)}
                            className="h-7 w-7 p-0"
                          >
                            <Check className="h-3 w-3 text-green-600" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={handleCancelEdit}
                            className="h-7 w-7 p-0"
                          >
                            <X className="h-3 w-3 text-red-600" />
                          </Button>
                        </div>
                      ) : (
                        <>
                          <div className="font-medium text-blue-900 text-sm truncate">
                            {session.title || "Conversație nouă"}
                          </div>
                          <div className="flex items-center gap-3 mt-1">
                            <div className="flex items-center gap-1 text-xs text-blue-600">
                              <MessageSquare className="h-3 w-3" />
                              {session.message_count}
                            </div>
                            {session.last_message_at && (
                              <div className="flex items-center gap-1 text-xs text-blue-500">
                                <Clock className="h-3 w-3" />
                                {formatLastMessageTime(session.last_message_at)}
                              </div>
                            )}
                          </div>
                        </>
                      )}
                    </div>

                    {editingSession !== session.id && (
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) =>
                            handleEditSession(
                              session.id,
                              session.title || "",
                              e
                            )
                          }
                          className="h-7 w-7 p-0 hover:bg-blue-200"
                        >
                          <Edit2 className="h-3 w-3 text-blue-600" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => handleDeleteSession(session.id, e)}
                          className="h-7 w-7 p-0 hover:bg-red-100"
                        >
                          <Trash2 className="h-3 w-3 text-red-600" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Date badge */}
                  <div className="mt-2">
                    <Badge
                      variant="outline"
                      className="text-xs text-blue-700 border-blue-300"
                    >
                      <Calendar className="h-3 w-3 mr-1" />
                      {new Date(session.created_at).toLocaleDateString("ro-RO")}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Chat Statistics */}
      <div className="mt-3">
        <ChatStatsCard />
      </div>
    </div>
  );
};

export default ChatHistorySidebar;
