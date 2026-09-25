import { useState, useEffect } from "react";
import Header from "@/components/Header";
import ToolInterface from "@/components/ToolInterface";
import ResultsDisplay from "@/components/ResultsDisplay";
import { useToast } from "@/hooks/use-toast";
import { apiService } from "@/services/api";
import { supabase } from "@/integrations/supabase/client";
import type { User } from "@supabase/supabase-js";

const Index = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [results, setResults] = useState<{ summary: string; transcript: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [user, setUser] = useState<User | null>(null);
  const { toast } = useToast();

  // Check backend health and get user on component mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        await apiService.healthCheck();
        setBackendStatus('online');
      } catch (error) {
        setBackendStatus('offline');
        toast({
          title: "Backend Offline",
          description: "Please make sure the backend server is running on http://localhost:8000",
          variant: "destructive"
        });
      }
    };

    const getUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user || null);
    };

    checkBackendHealth();
    getUser();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setUser(session?.user || null);
    });

    return () => subscription.unsubscribe();
  }, [toast]);

  const handleGenerate = async (videoUrl: string, selectedModel: string) => {
    if (backendStatus !== 'online') {
      toast({
        title: "Backend Offline",
        description: "Please make sure the backend server is running",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);
    setLoadingStep("Initializing...");
    
    try {
      // Start video processing with user ID if available
      const processResponse = await apiService.processVideo(videoUrl, user?.id);
      
      toast({
        title: "Processing Started",
        description: `Estimated time: ${processResponse.estimated_time || 60} seconds`,
      });

      // Poll for job status and results
      const results = await apiService.pollJobStatus(
        processResponse.job_id,
        (status) => {
          // Update progress based on status
          setLoadingStep(status.current_step || "Processing...");
          
          // Map backend status to user-friendly messages
          const stepMessages: { [key: string]: string } = {
            'downloading': 'Step 1/3: Extracting audio from YouTube...',
            'transcribing': 'Step 2/3: Generating transcript with AI...',
            'summarizing': 'Step 3/3: Creating intelligent summary...',
          };
          
          if (status.status in stepMessages) {
            setLoadingStep(stepMessages[status.status]);
          }
        },
        2000 // Poll every 2 seconds
      );

      // Set the final results
      setResults({
        summary: results.summary,
        transcript: results.transcript
      });

      toast({
        title: "Success!",
        description: `Video "${results.video_title}" processed successfully in ${Math.round(results.processing_time || 0)}s`
      });
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error occurred";
      setError(`Failed to process video: ${errorMessage}`);
      
      toast({
        title: "Processing Failed",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
      setLoadingStep("");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/5 to-background">
      <Header />
      
      <main className="container py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-primary/80 to-primary/60 bg-clip-text text-transparent">
            Synapse
          </h1>
          <p className="text-xl text-muted-foreground leading-relaxed">
            Transform YouTube lectures into intelligent summaries using advanced AI models. 
            Extract key insights, generate transcripts, and make learning more efficient.
          </p>
          
          {/* Backend Status Indicator */}
          <div className="mt-6 flex items-center justify-center gap-2">
            <div className={`w-3 h-3 rounded-full ${
              backendStatus === 'online' ? 'bg-green-500' : 
              backendStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500'
            }`} />
            <span className="text-sm text-muted-foreground">
              Backend: {
                backendStatus === 'online' ? 'Online & Ready' : 
                backendStatus === 'offline' ? 'Offline' : 'Checking...'
              }
            </span>
          </div>
        </div>

        {/* Tool Interface */}
        <ToolInterface onGenerate={handleGenerate} isLoading={isLoading} />

        {/* Results Display */}
        <ResultsDisplay 
          isLoading={isLoading}
          loadingStep={loadingStep}
          results={results}
          error={error}
        />
      </main>
    </div>
  );
};

export default Index;
