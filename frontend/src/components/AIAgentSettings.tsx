import {
  getAgentConfigSchema,
  getCurrentAgentConfig,
  updateAgentConfig,
  type CurrentToolConfigs,
  type ToolConfig,
  type ToolConfigSchema,
  type TrustedSitesToolConfig,
} from "@/api/aiApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Info, Loader2, RotateCcw, Save } from "lucide-react";
import React, { useEffect, useState } from "react";

interface AgentSettingsProps {
  onClose: () => void;
  onSave?: (configs: CurrentToolConfigs) => void;
}

const AIAgentSettings: React.FC<AgentSettingsProps> = ({ onClose, onSave }) => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [currentConfigs, setCurrentConfigs] =
    useState<CurrentToolConfigs | null>(null);
  const [schema, setSchema] = useState<Record<string, ToolConfigSchema> | null>(
    null
  );
  const [localConfigs, setLocalConfigs] = useState<CurrentToolConfigs | null>(
    null
  );
  const [error, setError] = useState<string>("");
  const [successMessage, setSuccessMessage] = useState<string>("");

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      setError("");

      const [configResponse, schemaResponse] = await Promise.all([
        getCurrentAgentConfig(),
        getAgentConfigSchema(),
      ]);

      if (!configResponse.success || !schemaResponse.success) {
        throw new Error("API returned unsuccessful response");
      }

      setCurrentConfigs(configResponse.current_configs);
      setLocalConfigs(
        JSON.parse(JSON.stringify(configResponse.current_configs))
      ); // Deep copy
      setSchema(schemaResponse.schema);
      setError("");
    } catch (err) {
      console.error("Error loading configs:", err);
      setError(
        `Failed to load configuration: ${
          err instanceof Error ? err.message : "Unknown error"
        }`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!localConfigs) return;

    try {
      setSaving(true);
      setError("");

      // Prepare tool configs for API
      const toolConfigs: Record<string, unknown> = {};

      // Simple tools
      toolConfigs.query_reformulation = localConfigs.query_reformulation;
      toolConfigs.timpark_payment = localConfigs.timpark_payment;
      toolConfigs.web_search = localConfigs.web_search;
      toolConfigs.final_response_generation =
        localConfigs.final_response_generation;

      // Mixed tool (trusted_sites_search)
      toolConfigs.trusted_sites_search = {
        gemini: localConfigs.trusted_sites_search.gemini,
        perplexity: localConfigs.trusted_sites_search.perplexity,
      };

      const response = await updateAgentConfig(toolConfigs);

      if (response.success) {
        setCurrentConfigs(localConfigs);
        setSuccessMessage(
          `Successfully updated ${response.updated_tools?.length || 0} tools`
        );

        // Save to localStorage for persistence
        localStorage.setItem("ai_agent_configs", JSON.stringify(localConfigs));

        // Call callback if provided
        if (onSave) {
          onSave(localConfigs);
        }

        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(""), 3000);
      } else {
        setError(response.error || "Failed to update configuration");
      }
    } catch (err) {
      console.error("Error saving configs:", err);
      setError("Failed to save configuration. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (currentConfigs) {
      setLocalConfigs(JSON.parse(JSON.stringify(currentConfigs)));
      setError("");
      setSuccessMessage("Configuration reset to last saved values");
      setTimeout(() => setSuccessMessage(""), 3000);
    }
  };

  const updateToolConfig = (
    toolName: keyof CurrentToolConfigs,
    field: keyof ToolConfig,
    value: string | number
  ) => {
    if (!localConfigs) return;

    const newConfigs = JSON.parse(JSON.stringify(localConfigs)); // Deep clone

    if (toolName === "trusted_sites_search") {
      // This shouldn't happen with the current UI design
      return;
    } else {
      const toolConfig = newConfigs[toolName] as ToolConfig;
      toolConfig[field] = value as never; // Use proper typing instead of any
    }

    setLocalConfigs(newConfigs);
  };

  const updateTrustedSitesConfig = (
    modelType: "gemini" | "perplexity",
    field: keyof ToolConfig,
    value: string | number
  ) => {
    if (!localConfigs) return;

    const newConfigs = JSON.parse(JSON.stringify(localConfigs)); // Deep clone
    const trustedSitesConfig =
      newConfigs.trusted_sites_search as TrustedSitesToolConfig;
    trustedSitesConfig[modelType][field] = value as never; // Use proper typing instead of any

    setLocalConfigs(newConfigs);
  };

  const renderToolConfig = (
    toolName: keyof CurrentToolConfigs,
    toolSchema: ToolConfigSchema
  ) => {
    if (!localConfigs || !schema) return null;

    const toolConfig = localConfigs[toolName];

    if (toolName === "trusted_sites_search") {
      const mixedConfig = toolConfig as TrustedSitesToolConfig;

      return (
        <div className="space-y-6">
          {/* Gemini Configuration */}
          <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
            <h4 className="font-semibold mb-3 flex items-center gap-2 text-blue-900">
              <Badge
                variant="outline"
                className="bg-blue-100 text-blue-800 border-blue-300"
              >
                Gemini
              </Badge>
              Domain Selection
            </h4>
            {toolSchema.gemini_config &&
              renderSingleToolConfig(
                mixedConfig.gemini,
                toolSchema.gemini_config,
                (field, value) =>
                  updateTrustedSitesConfig("gemini", field, value)
              )}
          </div>

          {/* Perplexity Configuration */}
          <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
            <h4 className="font-semibold mb-3 flex items-center gap-2 text-blue-900">
              <Badge
                variant="outline"
                className="bg-blue-100 text-blue-800 border-blue-300"
              >
                Perplexity
              </Badge>
              Filtered Search
            </h4>
            {toolSchema.perplexity_config &&
              renderSingleToolConfig(
                mixedConfig.perplexity,
                toolSchema.perplexity_config,
                (field, value) =>
                  updateTrustedSitesConfig("perplexity", field, value)
              )}
          </div>
        </div>
      );
    } else {
      const singleConfig = toolConfig as ToolConfig;
      return renderSingleToolConfig(singleConfig, toolSchema, (field, value) =>
        updateToolConfig(toolName, field, value)
      );
    }
  };

  const renderSingleToolConfig = (
    config: ToolConfig,
    configSchema:
      | ToolConfigSchema
      | ToolConfigSchema["gemini_config"]
      | ToolConfigSchema["perplexity_config"],
    onUpdate: (field: keyof ToolConfig, value: string | number) => void
  ) => {
    if (!configSchema) return null;

    return (
      <div className="space-y-4">
        {/* Model Selection */}
        <div className="space-y-2">
          <Label htmlFor="model" className="text-blue-900 font-medium">
            Model
          </Label>
          <Select
            value={config.model}
            onValueChange={(value) => onUpdate("model", value)}
          >
            <SelectTrigger className="border-blue-300 focus:border-blue-500 focus:ring-blue-500">
              <SelectValue
                placeholder="Select a model..."
                className="text-blue-900 font-medium"
              >
                <span className="text-blue-900 font-medium">
                  {config.model || "Select a model..."}
                </span>
              </SelectValue>
            </SelectTrigger>
            <SelectContent className="bg-white border-blue-200">
              {configSchema.available_models?.map((model) => (
                <SelectItem
                  key={model}
                  value={model}
                  className="text-blue-900 hover:bg-blue-50 focus:bg-blue-100"
                >
                  {model}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {!configSchema.available_models?.length && (
            <p className="text-sm text-red-600">No models available</p>
          )}
        </div>

        {/* Temperature */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="temperature" className="text-blue-900 font-medium">
              Temperature
            </Label>
            <span className="text-sm text-blue-700 font-mono bg-blue-100 px-2 py-1 rounded">
              {config.temperature}
            </span>
          </div>
          <Slider
            value={[config.temperature]}
            onValueChange={(value) => onUpdate("temperature", value[0])}
            min={configSchema.temperature_range?.[0] || 0}
            max={configSchema.temperature_range?.[1] || 1}
            step={0.1}
            className="w-full [&>span:first-child]:bg-blue-200 [&>span:first-child>span]:bg-blue-600"
          />
          <div className="text-xs text-blue-600">
            Lower = more focused, Higher = more creative
          </div>
        </div>

        {/* Max Tokens */}
        <div className="space-y-2">
          <Label htmlFor="max_tokens" className="text-blue-900 font-medium">
            Max Tokens
          </Label>
          <Input
            type="number"
            value={config.max_tokens}
            onChange={(e) => {
              const newValue = parseInt(e.target.value) || 0;
              onUpdate("max_tokens", newValue);
            }}
            min={configSchema.max_tokens_range?.[0] || 100}
            max={configSchema.max_tokens_range?.[1] || 30000}
            className="border-blue-300 focus:border-blue-500 focus:ring-blue-500 text-blue-900"
          />
          <div className="text-xs text-blue-600">
            Range: {configSchema.max_tokens_range?.[0]} -{" "}
            {configSchema.max_tokens_range?.[1]}
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-96">
          <CardContent className="flex items-center justify-center p-6">
            <Loader2 className="h-6 w-6 animate-spin mr-2" />
            Loading configuration...
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!localConfigs || !schema) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-96">
          <CardContent className="p-6">
            <div className="text-center">
              <p className="text-red-600 mb-4">Failed to load configuration</p>
              <div className="flex gap-2 justify-center">
                <Button onClick={loadConfigs}>Retry</Button>
                <Button variant="outline" onClick={onClose}>
                  Close
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5" />
                AI Agent Settings
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Configure models, temperature, and token limits for each tool
              </p>
            </div>
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-0 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Error/Success Messages */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mx-6 mt-4">
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          )}

          {successMessage && (
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mx-6 mt-4">
              <p className="text-blue-800 font-medium">{successMessage}</p>
            </div>
          )}

          <div className="p-6">
            <Tabs defaultValue="query_reformulation" className="w-full">
              <TabsList className="grid w-full grid-cols-5 bg-blue-100 border border-blue-200">
                {Object.entries(schema).map(([toolName, toolSchema]) => (
                  <TabsTrigger
                    key={toolName}
                    value={toolName}
                    className="text-xs data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=inactive]:text-blue-800 data-[state=inactive]:hover:text-blue-900 data-[state=inactive]:hover:bg-blue-200 font-medium"
                  >
                    {toolSchema.display_name}
                  </TabsTrigger>
                ))}
              </TabsList>

              {Object.entries(schema).map(([toolName, toolSchema]) => (
                <TabsContent key={toolName} value={toolName} className="mt-6">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold text-blue-900">
                        {toolSchema.display_name}
                      </h3>
                      <p className="text-sm text-blue-700">
                        {toolSchema.description}
                      </p>
                    </div>

                    {renderToolConfig(
                      toolName as keyof CurrentToolConfigs,
                      toolSchema
                    )}
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </div>
        </CardContent>

        {/* Footer with action buttons */}
        <div className="border-t border-blue-200 p-4 flex justify-between items-center bg-blue-50">
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleReset}
              disabled={saving}
              className="flex items-center gap-2 border-blue-300 text-blue-800 hover:bg-blue-100 hover:text-blue-900"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </Button>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={saving}
              className="border-blue-300 text-blue-800 hover:bg-blue-100"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
            >
              {saving ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              Save Changes
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default AIAgentSettings;
