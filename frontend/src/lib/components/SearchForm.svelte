<script lang="ts">
  import { apiClient } from '../api';
  import { setLoading, setError, clearError, addNotification } from '../stores';
  import type { KeywordGenerationResponse, SearchResponse } from '../api';
  import KeywordPanel from './KeywordPanel.svelte';

  let researchIdea = '';
  let keywords = '';
  let maxResults = 10;
  let generatedKeywords: string[] = [];
  let expandedKeywords: string[] = [];
  let isGeneratingKeywords = false;
  let isSearching = false;

  async function generateKeywords() {
    if (!researchIdea.trim()) {
      setError('Please enter a research idea');
      return;
    }

    isGeneratingKeywords = true;
    clearError();

    try {
      const response: KeywordGenerationResponse = await apiClient.generateKeywords(researchIdea);
      generatedKeywords = response.keywords || [];
      expandedKeywords = response.expanded_keywords || [];
      
      // Auto-fill keywords field
      keywords = generatedKeywords.join(', ');
      
      // Show success notification
      addNotification({
        type: 'success',
        message: `Generated ${generatedKeywords.length} keywords and ${expandedKeywords.length} MeSH terms`
      });
      
    } catch (error) {
      console.error('Error generating keywords:', error);
      addNotification({
        type: 'error',
        message: 'Failed to generate keywords. Please try again.'
      });
    } finally {
      isGeneratingKeywords = false;
    }
  }

  async function searchPubmed() {
    if (!keywords.trim()) {
      setError('Please enter keywords or generate them from your research idea');
      return;
    }

    isSearching = true;
    setLoading(true);
    clearError();

    try {
      console.log('Starting PubMed search...');
      const response: SearchResponse = await apiClient.searchPubmed({
        keywords: keywords,
        max_results: maxResults
      });

      console.log('Search completed:', response);
      
      // Show success notification
      addNotification({
        type: 'success',
        message: `✅ Search completed! Found ${response.articles_found} articles (Search ID: ${response.search_id})`
      });
      
    } catch (error) {
      console.error('Error searching PubMed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to search PubMed. Please try again.';
      addNotification({
        type: 'error',
        message: errorMessage
      });
    } finally {
      isSearching = false;
      setLoading(false);
    }
  }
</script>

<div class="card">
  <h2 class="text-xl font-semibold mb-4 text-gray-900">🔍 Research Search</h2>
  
  <!-- Research Idea Input -->
  <div class="mb-4">
    <label for="research-idea" class="block text-sm font-medium text-gray-700 mb-2">
      Research Idea
    </label>
    <textarea
      id="research-idea"
      bind:value={researchIdea}
      placeholder="Enter your research idea (e.g., 'machine learning applications in cancer diagnosis')"
      rows="3"
      class="textarea-field"
    ></textarea>
  </div>

  <!-- Generate Keywords Button -->
  <div class="mb-4">
    <button
      on:click={generateKeywords}
      disabled={isGeneratingKeywords || !researchIdea.trim()}
      class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {#if isGeneratingKeywords}
        🔄 Generating Keywords...
      {:else}
        🧠 Generate Keywords
      {/if}
    </button>
  </div>

  <!-- Generated Keywords Display -->
  <KeywordPanel {generatedKeywords} {expandedKeywords} />

  <!-- Manual Keywords Input -->
  <div class="mb-4">
    <label for="keywords" class="block text-sm font-medium text-gray-700 mb-2">
      Keywords for PubMed Search
    </label>
    <input
      id="keywords"
      type="text"
      bind:value={keywords}
      placeholder="Enter keywords separated by commas"
      class="input-field"
    />
  </div>

  <!-- Search Parameters -->
  <div class="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
    <div>
      <label for="max-results" class="block text-sm font-medium text-gray-700 mb-2">
        Max Results
      </label>
      <select id="max-results" bind:value={maxResults} class="input-field">
        <option value={5}>5 articles</option>
        <option value={10}>10 articles</option>
        <option value={20}>20 articles</option>
        <option value={50}>50 articles</option>
      </select>
    </div>
  </div>

  <!-- Search Button -->
  <div class="flex gap-4">
    <button
      on:click={searchPubmed}
      disabled={isSearching || !keywords.trim()}
      class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {#if isSearching}
        🔄 Searching PubMed...
      {:else}
        🔍 Search PubMed
      {/if}
    </button>
    
    <button
      type="button"
      on:click={() => {
        researchIdea = '';
        keywords = '';
        generatedKeywords = [];
        expandedKeywords = [];
        clearError();
      }}
      class="btn-secondary"
    >
      🗑️ Clear
    </button>
  </div>
</div>
