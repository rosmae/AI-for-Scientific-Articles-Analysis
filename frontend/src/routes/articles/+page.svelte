<script lang="ts">
  import ArticleTable from '$lib/components/ArticleTable.svelte';
</script>

<svelte:head>
  <title>Articles - Prime Time Medical Research</title>
</svelte:head>

<div class="space-y-6">
  <div class="card">
    <h1 class="text-3xl font-bold text-gray-900 mb-4">
      📚 Article Database
    </h1>
    <p class="text-gray-600">
      Browse all articles retrieved from PubMed searches. Click on the links to view full articles.
    </p>
  </div>

  <ArticleTable />
</div>
