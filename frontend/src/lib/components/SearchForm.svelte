<script lang="ts">
  import { apiClient } from '../api';
  import { setLoading, setError, clearError, addNotification } from '../stores';
  import type { KeywordGenerationResponse, SearchResponse } from '../api';
  import KeywordPanel from './KeywordPanel.svelte';
  import confetti from 'canvas-confetti';

  let researchIdea = '';
  let keywords = '';
  let maxResults = 10;
  let startDate = '';
  let endDate = '';
  let generatedKeywords: string[] = [];
  let expandedKeywords: string[] = [];
  let isGeneratingKeywords = false;
  let isSearching = false;
  let showDateFilters = false;

  // Set default date range (last 5 years)
  const today = new Date();
  const fiveYearsAgo = new Date(today.getFullYear() - 5, today.getMonth(), today.getDate());
  
  // Format dates for input fields (YYYY-MM-DD)
  endDate = today.toISOString().split('T')[0];
  startDate = fiveYearsAgo.toISOString().split('T')[0];

  function triggerConfetti() {
    try {
      console.log('Triggering confetti celebration!');
      
      // First burst - main celebration
      confetti({
        particleCount: 150,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
        zIndex: 9999
      });
      
      // Second burst - delayed for extra effect
      setTimeout(() => {
        confetti({
          particleCount: 80,
          spread: 45,
          origin: { y: 0.7 },
          colors: ['#3B82F6', '#10B981', '#F59E0B'],
          zIndex: 9999
        });
      }, 300);
      
      // Third burst - final celebration
      setTimeout(() => {
        confetti({
          particleCount: 50,
          spread: 120,
          origin: { y: 0.8 },
          colors: ['#10B981', '#F59E0B'],
          zIndex: 9999
        });
      }, 600);
      
    } catch (error) {
      console.error('Error triggering confetti:', error);
    }
  }

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
      expandedKeywords = response.expanded_keywords || []; // This might be empty from the backend
      
      // Auto-fill keywords field
      keywords = generatedKeywords.join('; '); // Use semicolons as backend expects
      
      // Show success notification
      addNotification({
        type: 'success',
        message: `Generated ${generatedKeywords.length} keywords${expandedKeywords.length > 0 ? ` and ${expandedKeywords.length} MeSH terms` : ''}`
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
      
      // Ensure idea_text meets minimum length requirement (10 chars)
      let ideaText = researchIdea?.trim() || '';
      if (ideaText.length < 10) {
        // If no research idea or too short, create a descriptive idea from keywords
        ideaText = `Research investigation into: ${keywords}`;
      }
      
      // Convert comma-separated keywords to semicolon-separated (backend format)
      const formattedKeywords = keywords.includes(';') ? keywords : keywords.replace(/,/g, ';');
      
      // Prepare search request with date filters if enabled
      const searchRequest = {
        keywords: formattedKeywords,
        idea_text: ideaText,
        max_results: maxResults,
        ...(showDateFilters && startDate && { start_date: startDate }),
        ...(showDateFilters && endDate && { end_date: endDate })
      };
      
      const response: SearchResponse = await apiClient.searchPubmed(searchRequest);

      console.log('Search completed:', response);
      
      // Trigger confetti if articles were successfully added
      if (response.articles_added && response.articles_added > 0) {
        console.log(`Articles added: ${response.articles_added} - triggering confetti!`);
        triggerConfetti();
      } else {
        console.log(`No articles added (${response.articles_added}) - no confetti`);
      }
      
      // Show success notification with confetti emoji
      addNotification({
        type: 'success',
        message: `🎉 ${response.message} (Search ID: ${response.search_id})`
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

  function setQuickDateRange(range: string) {
    const today = new Date();
    endDate = today.toISOString().split('T')[0];
    
    switch (range) {
      case '1year':
        const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());
        startDate = oneYearAgo.toISOString().split('T')[0];
        break;
      case '2years':
        const twoYearsAgo = new Date(today.getFullYear() - 2, today.getMonth(), today.getDate());
        startDate = twoYearsAgo.toISOString().split('T')[0];
        break;
      case '5years':
        const fiveYearsAgo = new Date(today.getFullYear() - 5, today.getMonth(), today.getDate());
        startDate = fiveYearsAgo.toISOString().split('T')[0];
        break;
      case '10years':
        const tenYearsAgo = new Date(today.getFullYear() - 10, today.getMonth(), today.getDate());
        startDate = tenYearsAgo.toISOString().split('T')[0];
        break;
      case 'all':
        startDate = '';
        endDate = '';
        break;
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
      placeholder="Enter keywords separated by semicolons (e.g., gene editing; sickle cell; CRISPR)"
      class="input-field"
    />
  </div>

  <!-- Search Parameters -->
  <div class="mb-4 space-y-4">
    <!-- Max Results -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label for="max-results" class="block text-sm font-medium text-gray-700 mb-2">
          Max Results
        </label>
        <select id="max-results" bind:value={maxResults} class="input-field">
          <option value={5}>5 articles</option>
          <option value={10}>10 articles</option>
          <option value={20}>20 articles</option>
          <option value={50}>50 articles</option>
          <option value={100}>100 articles</option>
        </select>
      </div>
      
      <!-- Date Filter Toggle -->
      <div class="md:col-span-2 flex items-end">
        <button
          type="button"
          on:click={() => showDateFilters = !showDateFilters}
          class="btn-secondary flex items-center space-x-2"
        >
          <span>📅</span>
          <span>{showDateFilters ? 'Hide' : 'Show'} Date Filters</span>
          <span class="transform transition-transform {showDateFilters ? 'rotate-180' : ''}">▼</span>
        </button>
      </div>
    </div>

    <!-- Date Filters (collapsible) -->
    {#if showDateFilters}
      <div class="border border-gray-200 rounded-lg p-4 bg-gray-50 space-y-4">
        <h3 class="text-sm font-medium text-gray-900 mb-3">📅 Publication Date Range</h3>
        
        <!-- Quick Date Range Buttons -->
        <div class="flex flex-wrap gap-2 mb-4">
          <button
            type="button"
            on:click={() => setQuickDateRange('1year')}
            class="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
          >
            Last Year
          </button>
          <button
            type="button"
            on:click={() => setQuickDateRange('2years')}
            class="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
          >
            Last 2 Years
          </button>
          <button
            type="button"
            on:click={() => setQuickDateRange('5years')}
            class="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
          >
            Last 5 Years
          </button>
          <button
            type="button"
            on:click={() => setQuickDateRange('10years')}
            class="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
          >
            Last 10 Years
          </button>
          <button
            type="button"
            on:click={() => setQuickDateRange('all')}
            class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
          >
            All Time
          </button>
        </div>

        <!-- Date Picker Inputs -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label for="start-date" class="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <input
              id="start-date"
              type="date"
              bind:value={startDate}
              class="input-field"
              max={endDate || undefined}
            />
          </div>
          <div>
            <label for="end-date" class="block text-sm font-medium text-gray-700 mb-2">
              End Date
            </label>
            <input
              id="end-date"
              type="date"
              bind:value={endDate}
              class="input-field"
              min={startDate || undefined}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>
        </div>

        <!-- Date Range Display -->
        {#if startDate || endDate}
          <div class="text-sm text-gray-600 bg-white rounded p-2 border">
            <strong>Selected Range:</strong>
            {#if startDate && endDate}
              From {new Date(startDate).toLocaleDateString()} to {new Date(endDate).toLocaleDateString()}
            {:else if startDate}
              From {new Date(startDate).toLocaleDateString()} onwards
            {:else if endDate}
              Up to {new Date(endDate).toLocaleDateString()}
            {/if}
          </div>
        {/if}
      </div>
    {/if}
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
    
    <!-- Test Confetti Button (for debugging) -->
    <!----><button
      type="button"
      on:click={triggerConfetti}
      class="px-4 py-2 text-sm bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors"
      title="Test confetti animation"
    >
      🎉 Test Confetti
    </button>
  </div>
</div>
