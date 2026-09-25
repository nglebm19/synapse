import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Youtube, Zap } from "lucide-react";

// Static model configuration
const AVAILABLE_MODELS = {
  asr: [
    { id: 'openai/whisper-large-v3', displayName: 'High-Quality Transcription (Whisper Large)' }
  ],
  llm: [
    { id: 'mistralai/Mistral-7B-Instruct-v0.2', displayName: 'Fast & Creative (Mistral 7B)' },
    { id: 'meta-llama/Llama-2-13b-chat-hf', displayName: 'Detailed & Thorough (Llama 13B)' }
  ]
};

interface ToolInterfaceProps {
  onGenerate: (videoUrl: string, selectedModel: string) => void;
  isLoading: boolean;
}

const ToolInterface = ({ onGenerate, isLoading }: ToolInterfaceProps) => {
  const [videoUrl, setVideoUrl] = useState("");
  const [selectedModel, setSelectedModel] = useState("");

  const isValidYouTubeUrl = (url: string) => {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/)|youtu\.be\/)[\w-]+/;
    return youtubeRegex.test(url);
  };

  const canGenerate = videoUrl && isValidYouTubeUrl(videoUrl) && selectedModel && !isLoading;

  const handleGenerate = () => {
    if (canGenerate) {
      onGenerate(videoUrl, selectedModel);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="text-center">
        <CardTitle className="flex items-center justify-center gap-2 text-2xl">
          <Youtube className="h-6 w-6 text-red-500" />
          Transform YouTube Lectures into Summaries
        </CardTitle>
        <CardDescription>
          Enter a YouTube video URL and select an AI model to generate an intelligent summary
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <label htmlFor="youtube-url" className="text-sm font-medium">
            YouTube Video URL
          </label>
          <Input
            id="youtube-url"
            type="text"
            placeholder="Paste a YouTube video link here... (e.g., https://youtube.com/watch?v=...)"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            className={`transition-colors ${
              videoUrl && !isValidYouTubeUrl(videoUrl) 
                ? "border-destructive focus-visible:ring-destructive" 
                : ""
            }`}
          />
          {videoUrl && !isValidYouTubeUrl(videoUrl) && (
            <p className="text-sm text-destructive">
              Please enter a valid YouTube URL
            </p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="model-select" className="text-sm font-medium">
            AI Model Selection
          </label>
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger>
              <SelectValue placeholder="Choose an AI model for processing" />
            </SelectTrigger>
            <SelectContent>
              {AVAILABLE_MODELS.llm.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  {model.displayName}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button
          onClick={handleGenerate}
          disabled={!canGenerate}
          className="w-full h-12 text-base font-medium bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Zap className="mr-2 h-5 w-5" />
          {isLoading ? "Generating..." : "Generate Summary"}
        </Button>
      </CardContent>
    </Card>
  );
};

export default ToolInterface;