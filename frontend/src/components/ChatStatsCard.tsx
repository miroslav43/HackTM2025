import { getChatStats, type ChatStats } from "@/api/aiApi";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Clock, MessageSquare, TrendingUp, Zap } from "lucide-react";
import React, { useEffect, useState } from "react";

interface ChatStatsCardProps {
  className?: string;
}

const ChatStatsCard: React.FC<ChatStatsCardProps> = ({ className = "" }) => {
  const [stats, setStats] = useState<ChatStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError("");
      const statsData = await getChatStats();
      setStats(statsData);
    } catch (err: any) {
      console.error("Error loading stats:", err);
      setError("Nu am putut încărca statisticile");
    } finally {
      setLoading(false);
    }
  };

  const toolNames: Record<string, string> = {
    query_reformulation: "Reformulare întrebări",
    timpark_payment: "Plată TimPark",
    web_search: "Căutare web",
    trusted_sites_search: "Site-uri oficiale",
    final_response_generation: "Sinteză finală",
  };

  if (loading) {
    return (
      <Card className={`${className}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="text-blue-600">Se încarcă statisticile...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats) {
    return (
      <Card className={`${className}`}>
        <CardContent className="p-6">
          <div className="text-center text-gray-500">
            {error || "Nu sunt disponibile statistici"}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-blue-900">
          <TrendingUp className="h-5 w-5" />
          Statistici conversații
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Main Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-blue-600" />
              <span className="text-sm text-blue-700 font-medium">
                Conversații
              </span>
            </div>
            <div className="text-2xl font-bold text-blue-900 mt-1">
              {stats.total_sessions}
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-600" />
              <span className="text-sm text-blue-700 font-medium">Mesaje</span>
            </div>
            <div className="text-2xl font-bold text-blue-900 mt-1">
              {stats.total_messages}
            </div>
          </div>
        </div>

        {/* Average messages per session */}
        {stats.total_sessions > 0 && (
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-blue-600" />
              <span className="text-sm text-blue-700 font-medium">
                Media mesaje/conversație
              </span>
            </div>
            <div className="text-lg font-bold text-blue-900 mt-1">
              {(stats.total_messages / stats.total_sessions).toFixed(1)}
            </div>
          </div>
        )}

        {/* Most used tools */}
        {stats.most_used_tools && stats.most_used_tools.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Zap className="h-4 w-4 text-blue-600" />
              <span className="text-sm text-blue-700 font-medium">
                Instrumente populare
              </span>
            </div>
            <div className="flex flex-wrap gap-1">
              {stats.most_used_tools.slice(0, 3).map((tool, index) => (
                <Badge
                  key={tool}
                  variant="outline"
                  className="text-xs bg-blue-100 text-blue-800 border-blue-300"
                >
                  {toolNames[tool] || tool}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Agent executions */}
        {stats.total_agent_executions > 0 && (
          <div className="bg-green-50 rounded-lg p-3 border border-green-200">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-700 font-medium">
                Execuții AI
              </span>
            </div>
            <div className="text-lg font-bold text-green-900 mt-1">
              {stats.total_agent_executions}
            </div>
          </div>
        )}

        {/* Success rate */}
        {stats.total_messages > 0 && stats.total_agent_executions > 0 && (
          <div className="text-center mt-4 pt-3 border-t border-blue-200">
            <div className="text-xs text-blue-600">
              Rata de succes:{" "}
              {(
                (stats.total_agent_executions / (stats.total_messages / 2)) *
                100
              ).toFixed(0)}
              %
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ChatStatsCard;
