<script lang="ts">
  import SearchForm from '$lib/components/SearchForm.svelte';
  import ArticleTable from '$lib/components/ArticleTable.svelte';
  import SearchHistory from '$lib/components/SearchHistory.svelte';
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api';
  import { setError, articles, addNotification } from '$lib/stores';

  let apiStatus = 'checking...';
  let articleCount = 0;

  // Subscribe to articles count
  articles.subscribe(value => {
    articleCount = value.length;
  });

  async function checkApiHealth() {
    try {
      await apiClient.healthCheck();
      apiStatus = 'connected ✅';
      addNotification({
        type: 'success', 
        message: '🔗 API connection established'
      });
    } catch (error) {
      console.error('API health check failed:', error);
      apiStatus = 'disconnected ❌';
      addNotification({
        type: 'error',
        message: 'Cannot connect to API backend. Make sure the API server is running on localhost:8000'
      });
    }
  }

  onMount(() => {
    checkApiHealth();
  });
</script>

<svelte:head>
  <title>Prime Time Medical Research - Dashboard</title>
</svelte:head>

<div class="space-y-6">
  <!-- Welcome Section -->
  <div class="card">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          🔬 Research Opportunity Dashboard
        </h1>
        <p class="mt-2 text-gray-600">
          Discover prime-time opportunities in medical research using AI-powered analysis
        </p>
      </div>
      <div class="text-right">
        <div class="text-sm text-gray-500">API Status</div>
        <div class="text-sm font-medium">{apiStatus}</div>
        <div class="text-xs text-blue-600 mt-1">
          📚 {articleCount} articles stored
        </div>
        <button
          on:click={checkApiHealth}
          class="text-xs text-blue-600 hover:text-blue-800 mt-1"
        >
          🔄 Refresh Status
        </button>
      </div>
    </div>
  </div>

  <!-- Search Form -->
  <SearchForm />

  <!-- Search History -->
  <SearchHistory />

  <!-- Articles Table -->
  <ArticleTable />

  <!-- Quick Info -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div class="card text-center">
      <div class="text-2xl mb-2">🧠</div>
      <h3 class="font-semibold text-gray-900">AI-Powered Keywords</h3>
      <p class="text-sm text-gray-600 mt-2">
        Generate relevant keywords from your research ideas using PubMedBERT
      </p>
    </div>
    
    <div class="card text-center">
      <div class="text-2xl mb-2">📊</div>
      <h3 class="font-semibold text-gray-900">Opportunity Scoring</h3>
      <p class="text-sm text-gray-600 mt-2">
        Analyze novelty, citation velocity, and recency to identify research opportunities
      </p>
    </div>
    
    <div class="card text-center">
      <div class="text-2xl mb-2">🔍</div>
      <h3 class="font-semibold text-gray-900">PubMed Integration</h3>
      <p class="text-sm text-gray-600 mt-2">
        Search and analyze medical literature with MeSH term expansion
      </p>
    </div>
  </div>
</div>
