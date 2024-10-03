  'use client'

  import dynamic from 'next/dynamic';
  import React, { useState, useEffect, useCallback } from 'react';
  import { motion, AnimatePresence } from 'framer-motion';
  import { FixedSizeList as List, ListChildComponentProps } from 'react-window';
  import AutoSizer from 'react-virtualized-auto-sizer';
  import { Button } from '@/components/ui/button';
  import { Input } from '@/components/ui/input';
  import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
  import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
  import { SearchIcon, StarIcon, UsersIcon, BookOpenIcon, ChevronRightIcon } from 'lucide-react';
  import { useTheme } from 'next-themes';
  import axios from 'axios';
  import { ForceGraph2D } from 'react-force-graph';
  import { Bar, Doughnut, Line, Radar, Scatter, Bubble } from 'react-chartjs-2';
  import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement, RadialLinearScale } from 'chart.js';
  // Comment out this line
  // import { Switch } from '@/components/ui/switch';

  type Article = {
    id: string;
    title: string;
    authors: string[];
    abstract: string;
    publicationDate: string;
    relevance: number;
  };

  type GraphData = {
    nodes: { id: string; group: number }[];
    links: { source: string; target: string }[];
  };

  const API_BASE_URL = 'http://localhost:5000';

  const DynamicForceGraph2D = dynamic(() => import('react-force-graph').then(mod => mod.ForceGraph2D), {
    ssr: false,
    loading: () => <p>Loading visualization...</p>
  });

  const RecommendationsTab = () => {
    const [recommendations, setRecommendations] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
      const fetchRecommendations = async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/api/recommendations`);
          setRecommendations(response.data);
          setIsLoading(false);
        } catch (error) {
          console.error("Error fetching recommendations:", error);
          setError("Failed to fetch recommendations. Please try again later.");
          setIsLoading(false);
        }
      };

      fetchRecommendations();
    }, []);

    if (isLoading) {
      return <div>Loading recommendations...</div>;
    }

    if (error) {
      return <div className="text-red-500">{error}</div>;
    }

    return (
      <div className="space-y-8">
        {recommendations.map((item) => (
          <Card key={item.article.id} className="p-4">
            <CardHeader>
              <CardTitle>{item.article.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <h3 className="text-lg font-semibold mb-2">Recommended Articles:</h3>
              <div className="space-y-4">
                {item.recommendations.map((rec: any) => (
                  <Card key={rec.id} className="p-2">
                    <CardHeader>
                      <CardTitle className="text-md">{rec.title}</CardTitle>
                      <CardDescription>{rec.authors.join(', ')}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm">{rec.abstract}</p>
                      <p className="text-xs mt-2">Published: {rec.publicationDate}</p>
                      <p className="text-xs">Similarity: {(rec.similarity * 100).toFixed(2)}%</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  export function EnhancedMlMiningResearchApp() {
    const [articles, setArticles] = useState<Article[]>([]);
    const [filteredArticles, setFilteredArticles] = useState<Article[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
    const [recommendations, setRecommendations] = useState<Article[]>([]);
    const [collaborativeCollection, setCollaborativeCollection] = useState<Article[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('articles');
    const { theme, setTheme } = useTheme();
    const [error, setError] = useState<string | null>(null);
    const [databaseStatus, setDatabaseStatus] = useState<string>('');
    // Comment out this line
    // const [useMockData, setUseMockData] = useState(false);

    const fetchArticles = useCallback(async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await axios.post(`${API_BASE_URL}/search`, { query: '' });
        console.log("Fetched articles:", response.data);
        setArticles(response.data);
        setFilteredArticles(response.data);
      } catch (error) {
        console.error('Error fetching articles:', error);
        setError('Failed to fetch articles. Please check if the backend server is running and try again.');
      } finally {
        setIsLoading(false);
      }
    }, []);

    const fetchGraphData = useCallback(async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/article/graph`);
        console.log("Received graph data:", response.data);
        console.log("Number of nodes:", response.data.nodes.length);
        console.log("Number of links:", response.data.links.length);
        console.log("Sample nodes:", response.data.nodes.slice(0, 5));
        console.log("Sample links:", response.data.links.slice(0, 5));
        setGraphData(response.data);
      } catch (error) {
        console.error('Error fetching graph data:', error);
        setError('Failed to fetch graph data. Please try again later.');
      }
    }, []);

    const fetchRecommendations = useCallback(async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/article/recommendations`);
        setRecommendations(response.data);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
        setError('Failed to fetch recommendations. Please try again later.');
      }
    }, []);

    useEffect(() => {
      fetchArticles();
      fetchGraphData();
      fetchRecommendations();
      checkDatabaseStatus();
    }, [fetchArticles, fetchGraphData, fetchRecommendations]);

    const handleSearch = useCallback(async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setIsLoading(true);
      setError(null);
      try {
        const response = await axios.post(`${API_BASE_URL}/search`, { query: searchQuery });
        setFilteredArticles(response.data);
      } catch (error) {
        console.error('Error searching articles:', error);
        setError('Failed to search articles. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    }, [searchQuery]);

    const addToCollection = useCallback(async (article: Article) => {
      try {
        await axios.post(`${API_BASE_URL}/article/favorite`, { article_id: article.id });
        setCollaborativeCollection(prev => [...prev, article]);
      } catch (error) {
        console.error('Error adding to collection:', error);
        setError('Failed to add article to collection. Please try again later.');
      }
    }, []);

    const removeFromCollection = useCallback(async (articleId: string) => {
      try {
        await axios.delete(`${API_BASE_URL}/article/favorite`, {
          data: { article_id: articleId }
        });
        setCollaborativeCollection(prev => prev.filter(article => article.id !== articleId));
      } catch (error) {
        console.error('Error removing from collection:', error);
        setError('Failed to remove article from collection. Please try again later.');
      }
    }, []);

    const triggerArxivFetch = async () => {
      try {
        setIsLoading(true);
        const response = await axios.post(`${API_BASE_URL}/trigger_arxiv_fetch`);
        alert(response.data.message);
        fetchArticles();
      } catch (error) {
        console.error('Error triggering Arxiv fetch:', error);
        alert("Error: Failed to start Arxiv fetch process. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };

    const checkDatabaseStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/database_status`);
        setDatabaseStatus(response.data.message);
        if (response.data.article_count > 0) {
          fetchGraphData();
          fetchArticles();
        }
      } catch (error) {
        console.error('Error checking database status:', error);
        setDatabaseStatus('Error checking database status');
      }
    };

    const populateSampleData = async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/populate_sample_data`);
        alert(response.data.message);
        if (response.data.article_count > 0) {
          fetchGraphData();
          fetchArticles();
        }
        checkDatabaseStatus();
      } catch (error) {
        console.error('Error populating sample data:', error);
        setError('Failed to populate sample data. Please try again later.');
      }
    };

    const ArticleCard = ({ article }: { article: Article }) => (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="mb-4 hover:shadow-lg transition-shadow duration-300">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-primary">{article.title}</CardTitle>
            <CardDescription className="text-sm text-muted-foreground">
              {article.authors.join(', ')} • {article.publicationDate}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="mt-2 text-secondary-foreground">{article.abstract}</p>
            <div className="mt-4 flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Relevance: {article.relevance.toFixed(2)}</span>
              <Button onClick={() => addToCollection(article)} size="sm" variant="outline">
                <StarIcon className="mr-2 h-4 w-4" /> Save
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );

    const renderRow = ({ index, style }: ListChildComponentProps) => {
      console.log("Rendering article:", filteredArticles[index]);
      return (
        <div style={style}>
          <ArticleCard article={filteredArticles[index]} />
        </div>
      );
    };

    const VisualizationTab = () => {
      const { theme } = useTheme();
      const [aiInsights, setAiInsights] = useState<string[]>([]);
      const [chartData, setChartData] = useState<any>(null);

      useEffect(() => {
        const fetchData = async () => {
          try {
            const [visualizationResponse, insightsResponse] = await Promise.all([
              axios.get(`${API_BASE_URL}/api/visualization-data`),
              axios.get(`${API_BASE_URL}/api/ai-insights`)
            ]);

            setChartData(visualizationResponse.data);
            setAiInsights(insightsResponse.data);
          } catch (error) {
            console.error("Error fetching data:", error);
          }
        };

        fetchData();
      }, []);

      if (!chartData) {
        return <div>Loading...</div>;
      }

      const barChartData = {
        labels: Object.keys(chartData.publicationsPerMonth),
        datasets: [{
          label: 'Publications per Month',
          data: Object.values(chartData.publicationsPerMonth),
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
        }],
      };

      const doughnutChartData = {
        labels: chartData.researchTopics.labels,
        datasets: [{
          data: chartData.researchTopics.data,
          backgroundColor: [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
          ],
        }],
      };

      const lineChartData = {
        labels: Object.keys(chartData.citationsOverTime),
        datasets: [{
          label: 'Citations Over Time',
          data: Object.values(chartData.citationsOverTime),
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1,
        }],
      };

      const scatterChartData = {
        datasets: [{
          label: 'Citations vs. Publication Year',
          data: chartData.citationsVsYear,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
        }],
      };

      const bubbleChartData = {
        datasets: [{
          label: 'Research Impact',
          data: chartData.researchImpact,
          backgroundColor: 'rgba(255, 99, 132, 0.6)',
        }],
      };

      // Register ChartJS components
      ChartJS.register(
        CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend,
        ArcElement, PointElement, LineElement, RadialLinearScale
      );

      // Sample data for charts
      const radarChartData = {
        labels: ['Theory', 'Application', 'Methodology', 'Experiments', 'Results'],
        datasets: [{
          label: 'Paper Focus Areas',
          data: [65, 59, 90, 81, 56],
          fill: true,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgb(255, 99, 132)',
          pointBackgroundColor: 'rgb(255, 99, 132)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgb(255, 99, 132)',
        }],
      };

      const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top' as const,
            display: true,
          },
          title: {
            display: true,
            text: 'Chart Title',
          },
        },
      };

      return (
        <Card className="p-4">
          <CardHeader>
            <CardTitle>Research Visualization Dashboard</CardTitle>
            <CardDescription>Explore various insights from the research data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card className="col-span-1 h-[300px]">
                <CardHeader>
                  <CardTitle>Research Topics Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <Doughnut data={doughnutChartData} options={chartOptions} />
                </CardContent>
              </Card>
              
              <Card className="col-span-1 h-[300px]">
                <CardHeader>
                  <CardTitle>Paper Focus Areas</CardTitle>
                </CardHeader>
                <CardContent>
                  <Radar data={radarChartData} options={chartOptions} />
                </CardContent>
              </Card>
              
              <Card className="col-span-1 h-[300px]">
                <CardHeader>
                  <CardTitle>Publications per Month</CardTitle>
                </CardHeader>
                <CardContent>
                  <Bar data={barChartData} options={chartOptions} />
                </CardContent>
              </Card>
              
              <Card className="col-span-1 md:col-span-2 lg:col-span-3 h-[300px]">
                <CardHeader>
                  <CardTitle>Citations Over Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <Line data={lineChartData} options={chartOptions} />
                </CardContent>
              </Card>

              <Card className="col-span-1 md:col-span-2 h-[300px]">
                <CardHeader>
                  <CardTitle>Citations vs. Publication Year</CardTitle>
                </CardHeader>
                <CardContent>
                  <Scatter data={scatterChartData} options={chartOptions} />
                </CardContent>
              </Card>

              <Card className="col-span-1 h-[300px]">
                <CardHeader>
                  <CardTitle>Research Impact</CardTitle>
                </CardHeader>
                <CardContent>
                  <Bubble data={bubbleChartData} options={chartOptions} />
                </CardContent>
              </Card>
            </div>

            <Card className="mt-8">
              <CardHeader>
                <CardTitle>AI-Driven Insights and Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 space-y-2">
                  {aiInsights.map((insight, index) => (
                    <li key={index} className="text-sm">{insight}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </CardContent>
        </Card>
      );
    };

    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="container mx-auto p-4 sm:p-6 md:p-8">
          <header className="mb-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <h1 className="text-3xl sm:text-4xl font-bold text-primary">ML Mining Research Platform</h1>
              <div className="flex flex-wrap gap-2 mb-4">
                <Button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} variant="outline">
                  Toggle Theme
                </Button>
                <Button onClick={triggerArxivFetch} variant="default">
                  Fetch New Papers
                </Button>
                <Button onClick={checkDatabaseStatus} variant="default">
                  Check Database Status
                </Button>
                <Button onClick={populateSampleData} variant="default">
                  Populate Sample Data
                </Button>
              </div>
            </div>
            <p className="text-xl text-muted-foreground mt-2">Discover, analyze, and collaborate on cutting-edge ML research in mining</p>
          </header>
          
          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex space-x-2">
              <Input
                type="search"
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-grow text-lg"
                aria-label="Search articles"
              />
              <Button type="submit" size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
                <SearchIcon className="h-5 w-5 mr-2" />
                Search
              </Button>
            </div>
          </form>

          {databaseStatus && (
            <p className="text-sm text-muted-foreground mb-4">{databaseStatus}</p>
          )}

          {/* Comment out this block
          <div className="flex items-center space-x-2 mb-4">
            <Switch
              id="use-mock-data"
              checked={useMockData}
              onCheckedChange={setUseMockData}
            />
            <label htmlFor="use-mock-data">Use mock data for visualization</label>
          </div>
          */}

          <Tabs defaultValue="articles" onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="grid w-full grid-cols-5 gap-4">
              <TabsTrigger value="articles" className="text-lg">
                <BookOpenIcon className="h-5 w-5 mr-2" />
                Articles
              </TabsTrigger>
              <TabsTrigger value="visualization" className="text-lg">
                <SearchIcon className="h-5 w-5 mr-2" />
                Visualization
              </TabsTrigger>
              <TabsTrigger value="recommendations" className="text-lg">
                <StarIcon className="h-5 w-5 mr-2" />
                Recommendations
              </TabsTrigger>
              <TabsTrigger value="collection" className="text-lg">
                <UsersIcon className="h-5 w-5 mr-2" />
                Collection
              </TabsTrigger>
              <TabsTrigger value="ai-insights" className="text-lg">
                <ChevronRightIcon className="h-5 w-5 mr-2" />
                AI Insights
              </TabsTrigger>
            </TabsList>

            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <TabsContent value="articles">
                  {isLoading ? (
                    <div className="flex justify-center items-center h-64">
                      <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-primary"></div>
                    </div>
                  ) : (
                    <div className="h-[calc(100vh-300px)]">
                      <AutoSizer>
                        {({ height, width }) => (
                          <List
                            height={height}
                            itemCount={filteredArticles.length}
                            itemSize={250}
                            width={width}
                            itemData={filteredArticles}
                          >
                            {renderRow}
                          </List>
                        )}
                      </AutoSizer>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="visualization">
                  <VisualizationTab />
                </TabsContent>

                <TabsContent value="recommendations">
                  <RecommendationsTab />
                </TabsContent>

                <TabsContent value="collection">
                  <h2 className="text-2xl font-bold mb-4 text-primary">Your Collection</h2>
                  {collaborativeCollection.map(article => (
                    <motion.div
                      key={article.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Card className="mb-4 hover:shadow-lg transition-shadow duration-300">
                        <CardHeader>
                          <CardTitle className="text-xl font-bold text-primary">{article.title}</CardTitle>
                          <CardDescription className="text-sm text-muted-foreground">
                            {article.authors.join(', ')} • {article.publicationDate}
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <p className="text-secondary-foreground">{article.abstract.substring(0, 150)}...</p>
                          <Button 
                            onClick={() => removeFromCollection(article.id)}
                            variant="destructive"
                            size="sm"
                            className="mt-4"
                          >
                            Remove from Collection
                          </Button>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </TabsContent>

                <TabsContent value="ai-insights">
                  {/* ... (existing AI Insights tab content) */}
                </TabsContent>
              </motion.div>
            </AnimatePresence>
          </Tabs>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
              <strong className="font-bold">Error!</strong>
              <span className="block sm:inline"> {error}</span>
            </div>
          )}
        </div>
      </div>
    );
  }