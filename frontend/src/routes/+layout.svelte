<script lang="ts">
  import '../app.css';
  import Header from '$lib/components/Header.svelte';
  import Notification from '$lib/components/Notification.svelte';
  import { error, isLoading, notifications, removeNotification } from '$lib/stores';
  import type { Notification as NotificationType } from '$lib/stores';

  let currentError: string | null = null;
  let loading: boolean = false;
  let notificationList: NotificationType[] = [];

  error.subscribe(value => currentError = value);
  isLoading.subscribe(value => loading = value);
  notifications.subscribe(value => notificationList = value);
</script>

<div class="min-h-screen bg-gray-50">
  <Header />
  
  <!-- Loading indicator -->
  {#if loading}
    <div class="fixed top-4 right-4 z-50">
      <div class="bg-primary-600 text-white px-4 py-2 rounded-md shadow-lg flex items-center space-x-2">
        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
        <span>Loading...</span>
      </div>
    </div>
  {/if}

  <!-- Error notification (legacy support) -->
  {#if currentError}
    <div class="fixed top-4 right-4 z-50">
      <div class="bg-red-600 text-white px-4 py-2 rounded-md shadow-lg flex items-center space-x-2">
        <span>❌</span>
        <span>{currentError}</span>
        <button 
          on:click={() => error.set(null)}
          class="text-red-200 hover:text-white ml-2"
        >
          ✕
        </button>
      </div>
    </div>
  {/if}

  <!-- Notification system -->
  <div class="fixed top-20 right-4 z-40 space-y-2 max-w-sm">
    {#each notificationList as notification (notification.id)}
      <Notification
        type={notification.type}
        message={notification.message}
        dismissible={notification.dismissible}
        autoClose={notification.autoClose}
        timeout={notification.timeout}
        on:dismiss={() => removeNotification(notification.id)}
      />
    {/each}
  </div>

  <!-- Main content -->
  <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
    <slot />
  </main>
</div>
