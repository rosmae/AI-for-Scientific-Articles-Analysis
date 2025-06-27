<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  export let type: 'success' | 'error' | 'info' | 'warning' = 'info';
  export let message: string;
  export let dismissible = true;
  export let autoClose = false;
  export let timeout = 5000;

  const dispatch = createEventDispatcher();

  function dismiss() {
    dispatch('dismiss');
  }

  // Auto-close functionality
  if (autoClose) {
    setTimeout(() => {
      dismiss();
    }, timeout);
  }

  const typeStyles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  const iconMap = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  };
</script>

<div class="p-4 border rounded-md {typeStyles[type]} mb-4" role="alert">
  <div class="flex items-start">
    <div class="flex-shrink-0">
      <span class="text-lg">{iconMap[type]}</span>
    </div>
    <div class="ml-3 flex-1">
      <p class="text-sm font-medium">{message}</p>
    </div>
    {#if dismissible}
      <div class="ml-auto pl-3">
        <button
          on:click={dismiss}
          class="inline-flex rounded-md p-1.5 hover:bg-opacity-20 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent"
        >
          <span class="sr-only">Dismiss</span>
          <span class="text-lg">×</span>
        </button>
      </div>
    {/if}
  </div>
</div>
