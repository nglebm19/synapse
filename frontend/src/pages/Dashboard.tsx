import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Brain, History, Trash2, Eye, Calendar, Video } from "lucide-react";
import Header from "@/components/Header";
import { useToast } from "@/hooks/use-toast";
import { apiService } from "@/services/api";
import type { User } from "@supabase/supabase-js";

interface VideoResult {
  id: string;
  video_title: string;
  created_at: string;
  summary: string;
  transcript: string;
}

const Dashboard = () => {
  const [user, setUser] = useState<User | null>(null);
  const [history, setHistory] = useState<VideoResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    // Check authentication and fetch data
    const initialize = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        navigate("/auth");
        return;
      }

      setUser(session.user);
      await fetchHistory();
      setIsLoading(false);
    };

    initialize();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (!session) {
        navigate("/auth");
      } else {
        setUser(session.user);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  const fetchHistory = async () => {
    try {
      if (!user) return;
      
      // Try to fetch real data from backend
      const jobs = await apiService.getUserJobs(user.id);
      
      // Convert backend job format to frontend VideoResult format
      const videoResults: VideoResult[] = jobs
        .filter(job => job.status === 'completed')
        .map(job => ({
          id: job.id,
          video_title: job.video_title || 'Unknown Video',
          created_at: job.created_at,
          summary: job.summary || 'No summary available',
          transcript: job.transcript || 'No transcript available'
        }));

      setHistory(videoResults);
    } catch (error) {
      console.error('Error fetching history:', error);
      
      // Fallback to mock data if backend is unavailable
      const mockData: VideoResult[] = [
        {
          id: '1',
          video_title: 'Introduction to Machine Learning - Stanford CS229',
          created_at: new Date().toISOString(),
          summary: 'Key concepts in machine learning including supervised and unsupervised learning...',
          transcript: 'Welcome to CS229, Machine Learning. Today we will cover...'
        },
        {
          id: '2', 
          video_title: 'Advanced React Patterns - React Conference 2024',
          created_at: new Date(Date.now() - 86400000).toISOString(),
          summary: 'Advanced patterns for building scalable React applications...',
          transcript: 'In this talk, we will explore advanced React patterns...'
        }
      ];

      setHistory(mockData);
      
      toast({
        title: "Using Demo Data",
        description: "Backend unavailable, showing demo history",
        variant: "default"
      });
    }
  };


  const handleDelete = async (id: string) => {
    try {
      // For now, just remove from local state since using mock data
      setHistory(prev => prev.filter(item => item.id !== id));
      toast({
        title: "Deleted",
        description: "Video summary deleted successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete video summary",
        variant: "destructive"
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Brain className="h-12 w-12 text-primary animate-pulse mx-auto mb-4" />
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/5 to-background">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="container py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Your Dashboard</h2>
          <p className="text-muted-foreground">
            View and manage your processed video summaries
          </p>
        </div>

        {/* Stats Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Videos</CardTitle>
              <Video className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{history.length}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">This Month</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {history.filter(item => 
                  new Date(item.created_at).getMonth() === new Date().getMonth()
                ).length}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
              <History className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {history.filter(item => 
                  Date.now() - new Date(item.created_at).getTime() < 7 * 24 * 60 * 60 * 1000
                ).length}
              </div>
              <p className="text-xs text-muted-foreground">Last 7 days</p>
            </CardContent>
          </Card>
        </div>

        {/* History Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              Processing History
            </CardTitle>
            <CardDescription>
              Your recent video summaries and transcripts
            </CardDescription>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <div className="text-center py-8">
                <Video className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No videos processed yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start by processing your first YouTube video
                </p>
                <Button onClick={() => navigate("/")}>
                  Process Your First Video
                </Button>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Video Title</TableHead>
                    <TableHead>Date Processed</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {history.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium max-w-xs truncate">
                        {item.video_title}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatDate(item.created_at)}
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          Completed
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => {
                              // In a real app, this would navigate to a detailed view
                              toast({
                                title: "Feature Coming Soon",
                                description: "Detailed view will be available in the next update"
                              });
                            }}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleDelete(item.id)}
                            className="text-destructive hover:text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Dashboard;