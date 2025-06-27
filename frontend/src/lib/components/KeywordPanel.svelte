<script lang="ts">
  import { addNotification } from '../stores';
  
  export let generatedKeywords: string[] = [];
  export let expandedKeywords: string[] = [];

  function copyToClipboard(text: string, type: string = 'keywords') {
    navigator.clipboard.writeText(text).then(() => {
      addNotification({
        type: 'success',
        message: `📋 ${type} copied to clipboard`
      });
    }).catch(() => {
      addNotification({
        type: 'error',
        message: 'Failed to copy to clipboard'
      });
    });
  }
</script>

{#if generatedKeywords.length > 0}
  <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-medium text-blue-900">🧠 Generated Keywords</h3>
      <button
        on:click={() => copyToClipboard(generatedKeywords.join(', '), 'Generated keywords')}
        class="text-xs text-blue-600 hover:text-blue-800"
        title="Copy to clipboard"
      >
        📋 Copy
      </button>
    </div>
    <div class="flex flex-wrap gap-2">
      {#each generatedKeywords as keyword}
        <span class="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
          {keyword}
        </span>
      {/each}
    </div>
    
    {#if expandedKeywords.length > 0}
      <div class="mt-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-medium text-green-900">🔬 MeSH Expanded Terms</h3>
          <button
            on:click={() => copyToClipboard(expandedKeywords.join(', '), 'MeSH expanded terms')}
            class="text-xs text-green-600 hover:text-green-800"
            title="Copy to clipboard"
          >
            📋 Copy
          </button>
        </div>
        <div class="flex flex-wrap gap-2">
          {#each expandedKeywords as keyword}
            <span class="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
              {keyword}
            </span>
          {/each}
        </div>
      </div>
    {/if}
  </div>
{/if}
