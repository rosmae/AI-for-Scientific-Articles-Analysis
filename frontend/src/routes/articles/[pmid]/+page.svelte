<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api';
  import { addNotification } from '$lib/stores';
  import type { Article } from '$lib/api';

  let article: Article | null = null;
  let isLoading = true;
  let pmid: string;

  $: pmid = $page.params.pmid;

  async function loadArticle() {
    if (!pmid) return;
    
    isLoading = true;
    try {
      article = await apiClient.getArticle(pmid);
      console.log('Loaded article:', article);
    } catch (error) {
      console.error('Error loading article:', error);
      addNotification({
        type: 'error',
        message: `Failed to load article ${pmid}`
      });
    } finally {
      isLoading = false;
    }
  }

  function formatDate(dateString: string): string {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  }

  onMount(() => {
    loadArticle();
  });
</script>

<svelte:head>
  <title>Article {pmid} - Prime Time Medical Research</title>
</svelte:head>

<div class="space-y-6">
  <!-- Navigation -->
  <div class="flex items-center space-x-2 text-sm text-gray-500">
    <a href="/" class="hover:text-gray-700">🏠 Dashboard</a>
    <span>›</span>
    <span>Article {pmid}</span>
  </div>

  {#if isLoading}
    <div class="card text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-600">Loading article details...</p>
    </div>
  {:else if article}
    <div class="card">
      <!-- Article Header -->
      <div class="border-b border-gray-200 pb-4 mb-4">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">
          {article.title}
        </h1>
        <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600">
          <span class="font-medium">PMID: {article.pmid}</span>
          <span>📅 {formatDate(article.pub_date)}</span>
          <span>📖 {article.journal}</span>
          {#if article.doi}
            <a
              href="https://doi.org/{article.doi}"
              target="_blank"
              rel="noopener noreferrer"
              class="text-blue-600 hover:text-blue-800"
            >
              🔗 DOI: {article.doi}
            </a>
          {/if}
        </div>
      </div>

      <!-- Authors -->
      {#if article.authors && article.authors.length > 0}
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-2">👥 Authors</h2>
          <div class="flex flex-wrap gap-2">
            {#each article.authors as author}
              <span class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
                {author}
              </span>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Abstract -->
      {#if article.abstract}
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-2">📝 Abstract</h2>
          <div class="prose max-w-none text-gray-700 leading-relaxed">
            {article.abstract}
          </div>
        </div>
      {/if}

      <!-- External Links -->
      <div class="border-t border-gray-200 pt-4">
        <h2 class="text-lg font-semibold text-gray-900 mb-3">🔗 External Links</h2>
        <div class="flex flex-wrap gap-3">
          <a
            href="https://pubmed.ncbi.nlm.nih.gov/{article.pmid}/"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-primary"
          >
            📖 View on PubMed
          </a>
          {#if article.doi}
            <a
              href="https://doi.org/{article.doi}"
              target="_blank"
              rel="noopener noreferrer"
              class="btn-secondary"
            >
              🔗 View DOI
            </a>
          {/if}
        </div>
      </div>
    </div>
  {:else}
    <div class="card text-center py-8">
      <p class="text-red-600 text-lg">❌ Article not found</p>
      <p class="text-gray-600 mt-2">The article with PMID {pmid} could not be loaded.</p>
      <a href="/" class="btn-primary mt-4">🏠 Back to Dashboard</a>
    </div>
  {/if}
</div>
