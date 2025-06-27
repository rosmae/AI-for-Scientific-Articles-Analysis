<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '../api';
  import { articles, setLoading, setError, clearError, addNotification } from '../stores';
  import type { Article } from '../api';

  let articleList: Article[] = [];

  // Subscribe to articles store
  articles.subscribe(value => {
    articleList = value;
  });

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

  {#if articleList.length === 0}
    <div class="text-center py-8 text-gray-500">
      <p class="text-lg">📄 No articles found</p>
      <p class="text-sm">Search for articles using the search form above</p>
    </div>
  {:else}
    <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Article Details
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Journal & Authors
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
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
          {#each articleList as article}
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

    <div class="mt-4 text-sm text-gray-500">
      Showing {articleList.length} article{articleList.length !== 1 ? 's' : ''}
    </div>
  {/if}
</div>
