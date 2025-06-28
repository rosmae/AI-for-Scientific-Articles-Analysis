<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api';
  import { addNotification } from '$lib/stores';

  let searchHistory: any[] = [];
  let filteredSearches: any[] = [];
  let selectedSearch: any = null;
  let opportunityScores: any = null;
  let isLoading = false;
  let isLoadingScores = false;
  
  // Pagination variables
  let currentPage = 1;
  let itemsPerPage = 12; // Show more searches per page
  let searchQuery = '';

  // Reactive statements for pagination
  $: totalPages = Math.ceil(filteredSearches.length / itemsPerPage);
  $: startIndex = (currentPage - 1) * itemsPerPage;
  $: endIndex = Math.min(startIndex + itemsPerPage, filteredSearches.length);
  $: paginatedSearches = filteredSearches.slice(startIndex, endIndex);

  async function loadSearchHistory() {
    isLoading = true;
    try {
      searchHistory = await apiClient.getSearchHistory();
      console.log('Loaded search history:', searchHistory);
      
      // Apply filtering
      filterSearches();
      
      if (searchHistory.length > 0) {
        selectedSearch = searchHistory[0]; // Auto-select the most recent search
        await loadOpportunityScores(selectedSearch.search_id);
      }
    } catch (error) {
      console.error('Error loading search history:', error);
      addNotification({
        type: 'error',
        message: 'Failed to load search history'
      });
    } finally {
      isLoading = false;
    }
  }

  function filterSearches() {
    if (!searchQuery.trim()) {
      filteredSearches = [...searchHistory];
    } else {
      const query = searchQuery.toLowerCase();
      filteredSearches = searchHistory.filter(search => 
        search.idea_text.toLowerCase().includes(query) ||
        search.keyword_text.toLowerCase().includes(query) ||
        search.search_id.toString().includes(query)
      );
    }
    currentPage = 1; // Reset to first page when filtering
  }

  function goToPage(page: number) {
    if (page >= 1 && page <= totalPages) {
      currentPage = page;
    }
  }

  function jumpToPage(event: Event) {
    const target = event.target as HTMLInputElement;
    const pageNum = parseInt(target.value);
    if (pageNum && pageNum >= 1 && pageNum <= totalPages) {
      goToPage(pageNum);
    }
    target.value = '';
  }

  // Watch for search query changes
  $: if (searchQuery !== undefined) {
    filterSearches();
  }

  async function loadOpportunityScores(searchId: number) {
    isLoadingScores = true;
    try {
      opportunityScores = await apiClient.getOpportunityScores(searchId);
      console.log('Loaded opportunity scores:', opportunityScores);
      
      addNotification({
        type: 'success',
        message: `Loaded opportunity analysis for search ${searchId}`
      });
    } catch (error) {
      console.error('Error loading opportunity scores:', error);
      addNotification({
        type: 'warning',
        message: 'Opportunity scores not yet computed for this search'
      });
      opportunityScores = null;
    } finally {
      isLoadingScores = false;
    }
  }

  function formatDate(dateString: string): string {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  }

  function getScoreColor(score: number): string {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    if (score >= 0.4) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  }

  function getScoreLabel(score: number): string {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Low';
  }

  function getRecommendation(scores: any): string {
    if (!scores) return '';
    
    const { novelty_score, citation_velocity_score, recency_score, overall_score } = scores;
    
    if (overall_score >= 0.8) {
      return '🎯 High Opportunity: This research area shows excellent potential with strong novelty, citation growth, and recent activity.';
    } else if (overall_score >= 0.6) {
      return '✅ Good Opportunity: This is a promising research area with solid fundamentals.';
    } else if (overall_score >= 0.4) {
      return '⚠️ Moderate Opportunity: Consider focusing on underexplored aspects or novel approaches.';
    } else {
      return '🔍 Limited Opportunity: This area may be saturated or declining. Consider pivoting to related but less explored topics.';
    }
  }

  onMount(() => {
    loadSearchHistory();
  });
</script>

<svelte:head>
  <title>Analysis - Prime Time Medical Research</title>
</svelte:head>

<div class="space-y-6">
  <!-- Page Header -->
  <div class="card">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          📊 Research Opportunity Analysis
        </h1>
        <p class="mt-2 text-gray-600">
          Analyze research opportunities using AI-powered scoring and insights
        </p>
      </div>
      <button
        on:click={loadSearchHistory}
        disabled={isLoading}
        class="btn-secondary"
      >
        {#if isLoading}
          🔄 Loading...
        {:else}
          🔄 Refresh
        {/if}
      </button>
    </div>
  </div>

  {#if isLoading}
    <div class="card text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-600">Loading analysis data...</p>
    </div>
  {:else if searchHistory.length === 0}
    <div class="card text-center py-8">
      <p class="text-lg text-gray-500">📈 No searches found</p>
      <p class="text-sm text-gray-400 mt-2">Perform a PubMed search to generate analysis data</p>
      <a href="/" class="btn-primary mt-4">🏠 Go to Dashboard</a>
    </div>
  {:else}
    <!-- Search Selection -->
    <div class="card">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-gray-900">🔍 Select Search for Analysis</h2>
        <div class="flex space-x-2">
          <select bind:value={itemsPerPage} on:change={() => currentPage = 1} class="input-field text-sm">
            <option value={6}>6 per page</option>
            <option value={12}>12 per page</option>
            <option value={24}>24 per page</option>
            <option value={48}>48 per page</option>
          </select>
        </div>
      </div>

      <!-- Search and Filter Controls -->
      <div class="mb-4">
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="Search by research idea, keywords, or search ID..."
          class="input-field w-full"
        />
      </div>

      <!-- Results Summary -->
      <div class="mb-4 text-sm text-gray-600">
        Showing {startIndex + 1}-{endIndex} of {filteredSearches.length} searches
        {#if searchQuery}
          (filtered from {searchHistory.length} total)
        {/if}
      </div>

      {#if filteredSearches.length === 0}
        <div class="text-center py-8 text-gray-500">
          {#if searchQuery}
            <p class="text-lg">🔍 No searches found matching "{searchQuery}"</p>
            <p class="text-sm">Try adjusting your search terms</p>
            <button 
              on:click={() => searchQuery = ''}
              class="btn-secondary mt-3"
            >
              Clear Search
            </button>
          {:else}
            <p class="text-lg">📈 No searches found</p>
            <p class="text-sm">Perform a PubMed search to generate analysis data</p>
          {/if}
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each paginatedSearches as search}
            <button
              on:click={() => {
                selectedSearch = search;
                loadOpportunityScores(search.search_id);
              }}
              class="text-left p-4 border rounded-lg hover:bg-gray-50 transition-colors {selectedSearch?.search_id === search.search_id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}"
            >
              <div class="font-medium text-gray-900">Search #{search.search_id}</div>
              <div class="text-sm text-gray-600 mt-1 line-clamp-2">{search.idea_text}</div>
              <div class="text-xs text-gray-500 mt-2">
                {formatDate(search.timestamp)} • {search.articles_found} articles
              </div>
            </button>
          {/each}
        </div>

        <!-- Pagination Controls -->
        {#if totalPages > 1}
          <div class="mt-6 flex items-center justify-between">
            <div class="flex-1 flex justify-between sm:hidden">
              <!-- Mobile pagination -->
              <button
                on:click={() => goToPage(currentPage - 1)}
                disabled={currentPage <= 1}
                class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                on:click={() => goToPage(currentPage + 1)}
                disabled={currentPage >= totalPages}
                class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
            
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div class="flex items-center space-x-4">
                <p class="text-sm text-gray-700">
                  Showing page <span class="font-medium">{currentPage}</span> of <span class="font-medium">{totalPages}</span>
                  (<span class="font-medium">{filteredSearches.length}</span> total searches)
                </p>
                <div class="flex items-center space-x-2">
                  <label for="jumpToPage" class="text-sm text-gray-700">Jump to:</label>
                  <input
                    id="jumpToPage"
                    type="number"
                    min="1"
                    max={totalPages}
                    placeholder="Page"
                    class="w-16 px-2 py-1 border border-gray-300 rounded text-sm"
                    on:keypress={(e) => e.key === 'Enter' && jumpToPage(e)}
                  />
                </div>
              </div>
              <div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <!-- Previous button -->
                  <button
                    on:click={() => goToPage(currentPage - 1)}
                    disabled={currentPage <= 1}
                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span class="sr-only">Previous</span>
                    ←
                  </button>
                  
                  <!-- Page numbers -->
                  {#each Array.from({length: Math.min(7, totalPages)}, (_, i) => {
                    if (totalPages <= 7) return i + 1;
                    if (currentPage <= 4) return i + 1;
                    if (currentPage >= totalPages - 3) return totalPages - 6 + i;
                    return currentPage - 3 + i;
                  }) as pageNum}
                    <button
                      on:click={() => goToPage(pageNum)}
                      class="relative inline-flex items-center px-4 py-2 border text-sm font-medium {pageNum === currentPage 
                        ? 'z-10 bg-primary-50 border-primary-500 text-primary-600' 
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'}"
                    >
                      {pageNum}
                    </button>
                  {/each}
                  
                  <!-- Show ellipsis if needed -->
                  {#if totalPages > 7 && currentPage < totalPages - 3}
                    <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                      ...
                    </span>
                    <button
                      on:click={() => goToPage(totalPages)}
                      class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                    >
                      {totalPages}
                    </button>
                  {/if}
                  
                  <!-- Next button -->
                  <button
                    on:click={() => goToPage(currentPage + 1)}
                    disabled={currentPage >= totalPages}
                    class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span class="sr-only">Next</span>
                    →
                  </button>
                </nav>
              </div>
            </div>
          </div>
        {/if}
      {/if}
    </div>

    {#if selectedSearch}
      <!-- Selected Search Details -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-4 text-gray-900">📋 Search Details</h2>
        <div class="bg-gray-50 p-4 rounded-lg">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div class="text-sm font-medium text-gray-700">Research Idea</div>
              <div class="text-gray-900">{selectedSearch.idea_text}</div>
            </div>
            <div>
              <div class="text-sm font-medium text-gray-700">Keywords</div>
              <div class="text-gray-900">{selectedSearch.keyword_text}</div>
            </div>
            <div>
              <div class="text-sm font-medium text-gray-700">Search Date</div>
              <div class="text-gray-900">{formatDate(selectedSearch.timestamp)}</div>
            </div>
            <div>
              <div class="text-sm font-medium text-gray-700">Articles Found</div>
              <div class="text-gray-900">{selectedSearch.articles_found} articles</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Opportunity Scores -->
      {#if isLoadingScores}
        <div class="card text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">Computing opportunity scores...</p>
        </div>
      {:else if opportunityScores}
        <div class="card">
          <h2 class="text-xl font-semibold mb-4 text-gray-900">🎯 Opportunity Scores</h2>
          
          <!-- Overall Score -->
          <div class="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">Overall Opportunity Score</h3>
                <p class="text-sm text-gray-600">Combined metric based on novelty, citation velocity, and recency</p>
              </div>
              <div class="text-right">
                <div class="text-3xl font-bold {getScoreColor(opportunityScores.overall_score)}">
                  {(opportunityScores.overall_score * 100).toFixed(0)}%
                </div>
                <div class="text-sm {getScoreColor(opportunityScores.overall_score)}">
                  {getScoreLabel(opportunityScores.overall_score)}
                </div>
              </div>
            </div>
          </div>

          <!-- Individual Scores -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div class="p-4 border rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium text-gray-900">🆕 Novelty Score</h4>
                <span class="text-lg font-bold {getScoreColor(opportunityScores.novelty_score)}">
                  {(opportunityScores.novelty_score * 100).toFixed(0)}%
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-blue-600 h-2 rounded-full" 
                  style="width: {opportunityScores.novelty_score * 100}%"
                ></div>
              </div>
              <p class="text-xs text-gray-600 mt-2">Measures how unique and unexplored this research area is</p>
            </div>

            <div class="p-4 border rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium text-gray-900">📈 Citation Velocity</h4>
                <span class="text-lg font-bold {getScoreColor(opportunityScores.citation_velocity_score)}">
                  {(opportunityScores.citation_velocity_score * 100).toFixed(0)}%
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-green-600 h-2 rounded-full" 
                  style="width: {opportunityScores.citation_velocity_score * 100}%"
                ></div>
              </div>
              <p class="text-xs text-gray-600 mt-2">Measures the rate of citation growth and research momentum</p>
            </div>

            <div class="p-4 border rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium text-gray-900">⏰ Recency Score</h4>
                <span class="text-lg font-bold {getScoreColor(opportunityScores.recency_score)}">
                  {(opportunityScores.recency_score * 100).toFixed(0)}%
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-purple-600 h-2 rounded-full" 
                  style="width: {opportunityScores.recency_score * 100}%"
                ></div>
              </div>
              <p class="text-xs text-gray-600 mt-2">Measures how recent and current the research activity is</p>
            </div>
          </div>

          <!-- Recommendation -->
          <div class="p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <h4 class="font-medium text-gray-900 mb-2">💡 AI Recommendation</h4>
            <p class="text-gray-700">{getRecommendation(opportunityScores)}</p>
          </div>
        </div>
      {:else}
        <div class="card text-center py-8">
          <p class="text-lg text-gray-500">⏳ Opportunity scores not available</p>
          <p class="text-sm text-gray-400 mt-2">
            Scores are computed in the background after each search. 
            Please wait a few moments and refresh.
          </p>
          <button
            on:click={() => loadOpportunityScores(selectedSearch.search_id)}
            class="btn-primary mt-4"
          >
            🔄 Check Again
          </button>
        </div>
      {/if}

      <!-- Research Insights -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-4 text-gray-900">🔬 Research Insights</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="p-4 border rounded-lg">
            <h4 class="font-medium text-gray-900 mb-2">📚 Publication Trends</h4>
            <p class="text-sm text-gray-600">
              Analysis of publication patterns and research momentum in this area.
            </p>
            <div class="mt-3 text-sm text-blue-600">
              Feature coming soon: Timeline visualization
            </div>
          </div>
          
          <div class="p-4 border rounded-lg">
            <h4 class="font-medium text-gray-900 mb-2">🌐 Research Clusters</h4>
            <p class="text-sm text-gray-600">
              Related research areas and emerging sub-topics identified by AI clustering.
            </p>
            <div class="mt-3 text-sm text-blue-600">
              Feature coming soon: Cluster visualization
            </div>
          </div>
          
          <div class="p-4 border rounded-lg">
            <h4 class="font-medium text-gray-900 mb-2">🔮 Future Predictions</h4>
            <p class="text-sm text-gray-600">
              AI-powered forecasts of research trends and citation growth.
            </p>
            <div class="mt-3 text-sm text-blue-600">
              Feature coming soon: Prediction charts
            </div>
          </div>
          
          <div class="p-4 border rounded-lg">
            <h4 class="font-medium text-gray-900 mb-2">🏆 Top Contributors</h4>
            <p class="text-sm text-gray-600">
              Leading researchers and institutions in this field.
            </p>
            <div class="mt-3 text-sm text-blue-600">
              Feature coming soon: Author rankings
            </div>
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>
