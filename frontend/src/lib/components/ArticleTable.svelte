<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '../api';
  import { articles, setLoading, setError, clearError, addNotification } from '../stores';
  import type { Article } from '../api';

  let articleList: Article[] = [];
  let filteredArticles: Article[] = [];
  let searchQuery = '';
  let currentPage = 1;
  let itemsPerPage = 10;
  let sortBy = 'date'; // 'date', 'title', 'journal'
  let sortOrder = 'desc'; // 'asc', 'desc'

  // Subscribe to articles store
  articles.subscribe(value => {
    articleList = value;
    filterAndSortArticles();
  });

  // Reactive statements for pagination
  $: totalPages = Math.ceil(filteredArticles.length / itemsPerPage);
  $: startIndex = (currentPage - 1) * itemsPerPage;
  $: endIndex = Math.min(startIndex + itemsPerPage, filteredArticles.length);
  $: paginatedArticles = filteredArticles.slice(startIndex, endIndex);

  async function loadArticles() {
    setLoading(true);
    clearError();

    try {
      console.log('Loading articles from backend...');
      const fetchedArticles = await apiClient.getArticles();
      console.log(`Loaded ${fetchedArticles.length} articles`);
      
      articles.set(fetchedArticles);
      
      if (fetchedArticles.length > 0) {
        addNotification({
          type: 'success',
          message: `📚 Loaded ${fetchedArticles.length} articles`
        });
      }
    } catch (error) {
      console.error('Error loading articles:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to load articles. Please try again.';
      addNotification({
        type: 'error',
        message: errorMessage
      });
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateString: string): string {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  }

  function truncateText(text: string, maxLength: number = 200): string {
    if (!text || text.length <= maxLength) return text || '';
    return text.substring(0, maxLength) + '...';
  }

  function formatAuthors(authors: string[]): string {
    if (!authors || authors.length === 0) return 'No authors';
    if (authors.length === 1) return authors[0];
    if (authors.length === 2) return authors.join(' & ');
    return `${authors[0]} et al. (${authors.length} authors)`;
  }

  function filterAndSortArticles() {
    // Filter articles based on search query
    let filtered = articleList.filter(article => {
      if (!searchQuery.trim()) return true;
      
      const query = searchQuery.toLowerCase();
      return (
        article.title.toLowerCase().includes(query) ||
        article.abstract.toLowerCase().includes(query) ||
        article.journal.toLowerCase().includes(query) ||
        article.authors.some(author => author.toLowerCase().includes(query)) ||
        article.pmid.includes(query)
      );
    });

    // Sort articles
    filtered.sort((a, b) => {
      let aVal, bVal;
      
      switch (sortBy) {
        case 'title':
          aVal = a.title.toLowerCase();
          bVal = b.title.toLowerCase();
          break;
        case 'journal':
          aVal = a.journal.toLowerCase();
          bVal = b.journal.toLowerCase();
          break;
        case 'date':
        default:
          aVal = new Date(a.pub_date || '1900-01-01');
          bVal = new Date(b.pub_date || '1900-01-01');
          break;
      }
      
      if (sortOrder === 'asc') {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      } else {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
      }
    });

    filteredArticles = filtered;
    currentPage = 1; // Reset to first page when filtering
  }

  function changeSorting(field: string) {
    if (sortBy === field) {
      sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      sortBy = field;
      sortOrder = 'desc';
    }
    filterAndSortArticles();
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
    filterAndSortArticles();
  }

  async function exportToCSV() {
    try {
      const blob = await apiClient.exportToCSV();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `articles_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      addNotification({
        type: 'success',
        message: '📄 Articles exported to CSV successfully'
      });
    } catch (error) {
      console.error('Error exporting to CSV:', error);
      addNotification({
        type: 'error',
        message: 'Failed to export articles. Please try again.'
      });
    }
  }

  onMount(() => {
    loadArticles();
  });
</script>

<div class="card">
  <div class="flex justify-between items-center mb-4">
    <h2 class="text-xl font-semibold text-gray-900">📚 Articles</h2>
    <div class="flex space-x-2">
      <button
        on:click={exportToCSV}
        disabled={articleList.length === 0}
        class="btn-secondary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
      >
        📄 Export CSV
      </button>
      <button
        on:click={loadArticles}
        class="btn-secondary text-sm"
      >
        🔄 Refresh
      </button>
    </div>
  </div>

  <!-- Search and Filter Controls -->
  <div class="mb-4 flex flex-col sm:flex-row gap-4">
    <div class="flex-1">
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search articles by title, abstract, author, journal, or PMID..."
        class="input-field"
      />
    </div>
    <div class="flex gap-2">
      <select bind:value={itemsPerPage} on:change={() => currentPage = 1} class="input-field">
        <option value={5}>5 per page</option>
        <option value={10}>10 per page</option>
        <option value={20}>20 per page</option>
        <option value={50}>50 per page</option>
      </select>
    </div>
  </div>

  <!-- Results Summary -->
  <div class="mb-4 text-sm text-gray-600">
    Showing {startIndex + 1}-{endIndex} of {filteredArticles.length} articles
    {#if searchQuery}
      (filtered from {articleList.length} total)
    {/if}
  </div>

  {#if filteredArticles.length === 0}
    <div class="text-center py-8 text-gray-500">
      {#if searchQuery}
        <p class="text-lg">� No articles found matching "{searchQuery}"</p>
        <p class="text-sm">Try adjusting your search terms</p>
        <button 
          on:click={() => searchQuery = ''}
          class="btn-secondary mt-3"
        >
          Clear Search
        </button>
      {:else}
        <p class="text-lg">�📄 No articles found</p>
        <p class="text-sm">Search for articles using the search form above</p>
      {/if}
    </div>
  {:else}
    <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <button 
                on:click={() => changeSorting('title')}
                class="flex items-center hover:text-gray-700"
              >
                Article Details
                {#if sortBy === 'title'}
                  <span class="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                {/if}
              </button>
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <button 
                on:click={() => changeSorting('journal')}
                class="flex items-center hover:text-gray-700"
              >
                Journal & Authors
                {#if sortBy === 'journal'}
                  <span class="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                {/if}
              </button>
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <button 
                on:click={() => changeSorting('date')}
                class="flex items-center hover:text-gray-700"
              >
                Date
                {#if sortBy === 'date'}
                  <span class="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                {/if}
              </button>
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              PMID
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          {#each paginatedArticles as article}
            <tr class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="max-w-lg">
                  <div class="text-sm font-medium text-gray-900 mb-1">
                    {truncateText(article.title, 120)}
                  </div>
                  {#if article.abstract}
                    <div class="text-xs text-gray-500 leading-relaxed">
                      {truncateText(article.abstract, 200)}
                    </div>
                  {/if}
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900 mb-1">
                  {truncateText(article.journal, 40)}
                </div>
                <div class="text-xs text-gray-500">
                  {formatAuthors(article.authors)}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {formatDate(article.pub_date)}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-mono text-gray-900">
                  {article.pmid}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <a
                    href="/articles/{article.pmid}"
                    class="text-primary-600 hover:text-primary-900"
                    title="View details"
                  >
                    👁️
                  </a>
                  {#if article.doi}
                    <a
                      href="https://doi.org/{article.doi}"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-primary-600 hover:text-primary-900"
                      title="View DOI"
                    >
                      🔗
                    </a>
                  {/if}
                  <a
                    href="https://pubmed.ncbi.nlm.nih.gov/{article.pmid}/"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-primary-600 hover:text-primary-900"
                    title="View on PubMed"
                  >
                    📖
                  </a>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
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
              (<span class="font-medium">{filteredArticles.length}</span> total articles)
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

    <div class="mt-4 text-sm text-gray-500">
      Showing {articleList.length} article{articleList.length !== 1 ? 's' : ''}
    </div>
  {/if}
</div>
