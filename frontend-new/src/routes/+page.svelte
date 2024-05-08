<script>
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    let inputRef;
    onMount(() => {
      inputRef.focus();
    });
  
    let query = '';
  
    function search() {
      // await goto(href, { shallow: true });
      goto(`/search?q=${encodeURIComponent(query)}`);
    }

    function handleKeyDown(event) {
      if (event.key === 'Enter' && query.trim() !== '') {
        search();
      }
    }
</script>
  
<main class="flex flex-col items-center justify-center h-screen bg-gray-100">
    <!-- <h1 class="text-3xl font-bold mb-4">Google-like Search</h1> -->
    <input
      type="text"
      bind:value={query}
      placeholder=""
      on:keydown={handleKeyDown}
      class="w-5/6 p-2 mb-4 text-lg border border-gray-300 rounded-md focus:outline-none"
      bind:this={inputRef}
    />
    <button
      on:click={search}
      class="px-4 py-2 bg-blue-600 text-white text-lg font-semibold rounded-md hover:bg-blue-700"
    >
      Research
    </button>
</main>