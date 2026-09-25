import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Loader2, FileText, MessageSquare, AlertCircle, CheckCircle } from "lucide-react";

interface ResultsDisplayProps {
  isLoading: boolean;
  loadingStep?: string;
  results?: {
    summary: string;
    transcript: string;
  };
  error?: string;
}

const ResultsDisplay = ({ isLoading, loadingStep, results, error }: ResultsDisplayProps) => {
  // Initial state - show placeholder
  if (!isLoading && !results && !error) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="flex flex-col items-center justify-center py-16 text-center">
          <div className="rounded-full bg-accent/20 p-6 mb-4">
            <FileText className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Ready to Process</h3>
          <p className="text-muted-foreground max-w-md">
            Enter a YouTube video URL and select an AI model above to generate an intelligent summary and transcript
          </p>
        </CardContent>
      </Card>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="flex flex-col items-center justify-center py-16 text-center">
          <Loader2 className="h-12 w-12 text-primary animate-spin mb-4" />
          <h3 className="text-xl font-semibold mb-2">Processing Your Video</h3>
          <p className="text-muted-foreground mb-6">
            {loadingStep || "Analyzing video content..."}
          </p>
          <div className="w-full max-w-md space-y-2">
            <div className="flex items-center text-sm text-muted-foreground">
              <div className="w-4 h-4 rounded-full bg-primary mr-3" />
              Step 1: Extracting audio
            </div>
            <div className="flex items-center text-sm text-muted-foreground">
              <div className="w-4 h-4 rounded-full bg-muted mr-3" />
              Step 2: Generating transcript
            </div>
            <div className="flex items-center text-sm text-muted-foreground">
              <div className="w-4 h-4 rounded-full bg-muted mr-3" />
              Step 3: Creating summary
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Error state
  if (error) {
    return (
      <Card className="w-full max-w-4xl mx-auto border-destructive/20">
        <CardContent className="flex flex-col items-center justify-center py-16 text-center">
          <div className="rounded-full bg-destructive/10 p-6 mb-4">
            <AlertCircle className="h-12 w-12 text-destructive" />
          </div>
          <h3 className="text-xl font-semibold mb-2 text-destructive">Processing Failed</h3>
          <p className="text-muted-foreground max-w-md">
            {error || "Sorry, we couldn't process this video. Please check the URL and try again."}
          </p>
        </CardContent>
      </Card>
    );
  }

  // Success state with results
  if (results) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-2 text-green-600">
          <CheckCircle className="h-5 w-5" />
          <span className="font-medium">Processing completed successfully!</span>
        </div>

        {/* Summary Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Summary
            </CardTitle>
            <CardDescription>
              AI-generated key points and insights from the lecture
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-foreground leading-relaxed">
                {results.summary}
              </div>
            </div>
          </CardContent>
        </Card>

        <Separator />

        {/* Transcript Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Full Transcript
            </CardTitle>
            <CardDescription>
              Complete transcription of the video content
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-foreground leading-relaxed">
                {results.transcript}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return null;
};

export default ResultsDisplay;