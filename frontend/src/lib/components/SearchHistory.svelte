<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '../api';
  import { addNotification } from '../stores';

  let searchHistory: any[] = [];
  let isLoading = false;

  async function loadSearchHistory() {
    isLoading = true;
    try {
      searchHistory = await apiClient.getSearchHistory();
      console.log('Loaded search history:', searchHistory);
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

  async function viewOpportunityScores(searchId: number) {
    try {
      const scores = await apiClient.getOpportunityScores(searchId);
      console.log('Opportunity scores:', scores);
      addNotification({
        type: 'info',
        message: `Opportunity scores loaded for search ${searchId}`
      });
    } catch (error) {
      console.error('Error loading opportunity scores:', error);
      addNotification({
        type: 'error',
        message: 'Failed to load opportunity scores'
      });
    }
  }

  function formatDate(dateString: string): string {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  }

  onMount(() => {
    loadSearchHistory();
  });
</script>

<div class="card">
  <div class="flex justify-between items-center mb-4">
    <h2 class="text-xl font-semibold text-gray-900">📋 Search History</h2>
    <button
      on:click={loadSearchHistory}
      disabled={isLoading}
      class="btn-secondary text-sm disabled:opacity-50"
    >
      {#if isLoading}
        🔄 Loading...
      {:else}
        🔄 Refresh
      {/if}
    </button>
  </div>

  {#if searchHistory.length === 0}
    <div class="text-center py-8 text-gray-500">
      <p class="text-lg">📝 No search history found</p>
      <p class="text-sm">Search for articles to see your history</p>
    </div>
  {:else}
    <div class="space-y-4">
      {#each searchHistory as search}
        <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900 mb-1">
                Search ID: {search.search_id}
              </div>
              <div class="text-sm text-gray-600 mb-2">
                <strong>Idea:</strong> {search.idea_text || 'N/A'}
              </div>
              <div class="text-sm text-gray-600 mb-2">
                <strong>Keywords:</strong> {search.keyword_text}
              </div>
              <div class="text-xs text-gray-500">
                {formatDate(search.timestamp)} • {search.articles_found} articles found • Max results: {search.max_results}
              </div>
            </div>
            <div class="ml-4">
              <button
                on:click={() => viewOpportunityScores(search.search_id)}
                class="text-sm text-blue-600 hover:text-blue-800"
              >
                📊 View Scores
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
